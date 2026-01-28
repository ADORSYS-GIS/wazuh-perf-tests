# helm repository will be specified directly in helm_release

resource "helm_release" "litmus" {
  name             = var.release_name
  repository       = "https://litmuschaos.github.io/litmus-helm"
  chart            = "litmus"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.24.0"
  timeout          = 900
  wait             = true
  wait_for_jobs    = true

  set {
    name  = "installCRDs"
    value = "false"
  }

  set {
    name  = "portal.frontend.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "mongodb.enabled"
    value = "true"
  }

  set {
    name  = "mongodb.auth.enabled"
    value = "true"
  }

  set {
    name  = "server.waitForMongodb.enabled"
    value = "true"
  }
}

resource "kubernetes_service_account" "litmus_project_creator" {
  metadata {
    name      = "litmus-project-creator"
    namespace = var.namespace
  }
}

resource "kubernetes_role" "litmus_project_creator" {
  metadata {
    name      = "litmus-project-creator"
    namespace = var.namespace
  }

  rule {
    api_groups = [""]
    resources  = ["configmaps"]
    verbs      = ["get", "create", "patch", "update"]
  }
}

resource "kubernetes_role_binding" "litmus_project_creator" {
  metadata {
    name      = "litmus-project-creator"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.litmus_project_creator.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.litmus_project_creator.metadata[0].name
    namespace = var.namespace
  }
}

resource "kubernetes_job" "create_litmus_project" {
  metadata {
    name      = "create-litmus-project"
    namespace = var.namespace
  }

  spec {
    template {
      metadata {
        name = "create-litmus-project"
      }
      spec {
        service_account_name = kubernetes_service_account.litmus_project_creator.metadata[0].name
        container {
          name  = "create-litmus-project"
          image = "alpine/k8s:1.28.3"
          command = ["/bin/sh", "-c"]
          args = [
            <<-EOT
            # Wait for litmus auth server to be ready
            until curl -s http://litmus-auth-server-service.${var.namespace}.svc.cluster.local:9003/auth/login > /dev/null; do
              echo "Waiting for Litmus Auth server..."
              sleep 5
            done

            echo "Attempting login..."
            RESPONSE=$(curl -s -X POST \
              -H "Content-Type: application/json" \
              -d "{\"username\": \"${var.litmus_admin_username}\", \"password\": \"${var.litmus_admin_password}\"}" \
              http://litmus-auth-server-service.${var.namespace}.svc.cluster.local:9003/auth/login)
            
            AUTH_TOKEN=$(echo $RESPONSE | jq -r '.token // .accessToken // .data.token // empty')

            if [ -z "$AUTH_TOKEN" ] || [ "$AUTH_TOKEN" == "null" ]; then
              echo "Failed to get LitmusChaos authentication token. Response: $RESPONSE"
              exit 1
            fi

            echo "Login successful. Checking for project..."

            # Check if project already exists
            PROJECT_ID=$(curl -s -X POST \
              -H "Content-Type: application/json" \
              -H "Authorization: Bearer $AUTH_TOKEN" \
              -d '{"query": "query { listProjects(project: {name: \"'${var.litmus_project_name}'\"}) { project_id name } }"}' \
              http://litmus-server-service.${var.namespace}.svc.cluster.local:9002/api/query | jq -r '.data.listProjects[]? | select(.name=="'${var.litmus_project_name}'") | .project_id' | head -n 1)

            if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "null" ]; then
              echo "Project not found, creating..."
              PROJECT_ID=$(curl -s -X POST \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $AUTH_TOKEN" \
                -d "{\"query\": \"mutation { createProject(project: {name: \\\"${var.litmus_project_name}\\\"}) { project_id } }\"}" \
                http://litmus-server-service.${var.namespace}.svc.cluster.local:9002/api/query | jq -r '.data.createProject.project_id')
            fi

            if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" == "null" ]; then
              echo "Failed to obtain LitmusChaos project ID."
              exit 1
            fi

            echo "LitmusChaos project '${var.litmus_project_name}' ID: $PROJECT_ID"
            
            # Create ConfigMap with the project ID
            kubectl create configmap litmus-project-id --from-literal=project_id=$PROJECT_ID -n ${var.namespace} --dry-run=client -o yaml | kubectl apply -f -
            EOT
          ]
        }
        restart_policy = "Never"
      }
    }
    backoff_limit = 4
  }

  wait_for_completion = true
  timeouts {
    create = "5m"
    update = "5m"
  }

  depends_on = [helm_release.litmus, kubernetes_role_binding.litmus_project_creator]
}

data "kubernetes_config_map" "project_id" {
  metadata {
    name      = "litmus-project-id"
    namespace = var.namespace
  }
  depends_on = [kubernetes_job.create_litmus_project]
}

resource "helm_release" "litmus_agent" {
  name             = "litmus-agent"
  repository       = "https://litmuschaos.github.io/litmus-helm"
  chart            = "litmus-agent"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.24.0"
  timeout          = 300
  wait             = true
  skip_crds        = true

  set {
    name  = "installCRDs"
    value = "false"
  }

  set {
    name  = "LITMUS_URL"
    value = "http://litmus-frontend-service.${var.namespace}.svc.cluster.local:9091"
  }

  set {
    name  = "LITMUS_BACKEND_URL"
    value = "http://litmus-server-service.${var.namespace}.svc.cluster.local:9002"

  }

  set {
    name  = "INFRA_MODE"
    value = "cluster"
  }

  set {
    name  = "PLATFORM"
    value = "Rancher"
  }

  set {
    name  = "workflow-controller.crds.create"
    value = "false"
  }

  set {
    name  = "PROJECT_ID"
    value = data.kubernetes_config_map.project_id.data["project_id"]
  }

  depends_on = [helm_release.litmus, data.kubernetes_config_map.project_id]
}


# Install LitmusChaos experiment CRDs (ChaosExperiment) via kubernetes-chaos chart
resource "helm_release" "litmus_experiments" {
  name             = "litmus-experiments"
  repository       = "https://litmuschaos.github.io/litmus-helm"
  chart            = "kubernetes-chaos"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.25.0"
  timeout          = 300
  wait             = true

  set {
    name  = "installCRDs"
    value = "true"
  }

  depends_on = [helm_release.litmus, kubernetes_job.create_litmus_project]
}
