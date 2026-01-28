# LitmusChaos Experiment Guide using Terraform

This guide explains how to deploy and run LitmusChaos experiments using the provided Terraform infrastructure setup in the Wazuh Performance Testing project.

## 1. Infrastructure Setup Overview

The LitmusChaos setup relies on two main components defined in the Terraform modules:

1.  **LitmusChaos Framework Installation** (`terraform/litmuschaos`): This module installs the core LitmusChaos components (including the operator and CRDs) into the Kubernetes cluster using the Helm provider.
2.  **Chaos Experiment Definitions** (`terraform/chaos-experiment`): This is a reusable module that deploys a specific chaos experiment by taking a YAML definition as input via the `experiment_yaml` variable. Specific experiments (like CPU Stress, Pod Delete, etc.) are instantiated as modules that point to their respective YAML definitions (e.g., `cpu-stress.yaml`).

The main entry point for provisioning is [`terraform/main.tf`](terraform/main.tf), which sets up the `tests` namespace and conditionally enables and depends on the LitmusChaos installation and various experiment modules.

## 2. Addressing Key Questions

### Should the agent and the chaos cluster be on the same infrastructure?

**Recommendation:** The LitmusChaos framework (the chaos cluster/control plane) should **not** be installed on the same infrastructure as the Wazuh agent you intend to test against, **unless** the goal is to test the agent's resilience to infrastructure failure itself.

*   **Separation of Concerns:** For testing the agent's performance and failure handling under stress, the agent should be running on its own distinct set of target infrastructure (the System Under Test or SUT).
*   **Litmus Installation:** The Terraform module in [`terraform/litmuschaos/main.tf`](terraform/litmuschaos/main.tf) deploys LitmusChaos components (operator, CRDs) into a specified Kubernetes `namespace` (defaulting to `litmus` in the module, but the main configuration deploys into the `tests` namespace). This control plane *must* have connectivity to the Kubernetes cluster where the SUT (including the Wazuh agent) resides.
*   **Experiment Targets:** The actual chaos experiments deployed via [`terraform/chaos-experiment/main.tf`](terraform/chaos-experiment/main.tf) will target workloads *within* the cluster based on their YAML definition, which should include the deployment/pod labels of your Wazuh agent/manager deployment if you wish to target them directly.

### Can everything be done from a script, or is the dashboard approach recommended?

**Recommendation:** For automated performance testing and integration into CI/CD pipelines, **everything should be done via scripting using Terraform**, as provided in this repository.

*   **Terraform/Scripting Approach (Recommended):** The infrastructure is set up for declarative, repeatable execution via Terraform. You use Terraform commands (`plan`, `apply`) to install LitmusChaos and then to define and apply the experiment manifests (as seen in modules like [`terraform/chaos-cpu-stress/main.tf`](terraform/chaos-cpu-stress/main.tf) which uses `kubernetes_manifest` to apply the experiment YAML). This is ideal for performance testing where execution must be consistent and traceable.
*   **Dashboard Approach (Manual):** The LitmusChaos UI (dashboard) is available (the service type is set to `LoadBalancer` in [`terraform/litmuschaos/main.tf`](terraform/litmuschaos/main.tf)) and can be used for manual experimentation, debugging, or exploring experiments. However, it should **not** be the primary method for automated performance test runs.

## 3. Step-by-Step Guide to Run a Chaos Experiment

This guide assumes you have a Kubernetes cluster accessible via the configuration referenced in [`terraform/variables.tf`](terraform/variables.tf) (specifically `kube_config_path` and `kube_config_context`) and that your target workloads are deployed in the cluster.

### Prerequisites

1.  **Terraform Installed:** Ensure Terraform is installed on your local machine.
2.  **Kubernetes Access:** Ensure your `kubectl` context is set up correctly, as Terraform uses the Kubernetes provider configured by default via `$HOME/.kube/config` or the path specified in [`terraform/variables.tf`](terraform/variables.tf).
3.  **Target Workload:** Ensure the target application/workload you wish to disrupt (e.g., a deployment you are testing) is running in the cluster, preferably targeted by labels that the chaos experiment YAML will select.

### Execution Steps

#### Step 1: Initialize Terraform

Navigate to the project root and initialize the Terraform workspace.

Execute:
```bash
terraform init
```

#### Step 2: Install the LitmusChaos Framework

To install the base LitmusChaos components (operator and CRDs), you must enable the `litmuschaos` module in [`terraform/variables.tf`](terraform/variables.tf) (set `enable_litmuschaos` to `true` if it wasn't already) and apply the configuration.

Execute to install LitmusChaos:
```bash
terraform apply -var="enable_litmuschaos=true"
```

This step will deploy the framework, which may take several minutes. The module in [`terraform/litmuschaos/main.tf`](terraform/litmuschaos/main.tf) uses Helm to deploy the necessary components.

#### Step 3: Select and Enable a Specific Experiment

Review the available experiment modules in the root [`terraform/main.tf`](terraform/main.tf) file. For this example, we will enable the CPU Stress experiment.

1.  **Enable the Experiment:** Set the corresponding variable in `terraform.tfvars` or pass it as a variable during `apply`. To enable CPU Stress:
    ```bash
    # Example: Pass via command line
    terraform apply -var="enable_chaos_cpu_stress=true"
    ```
    *(Note: If you have a [`terraform/terraform.tfvars`](terraform/terraform.tfvars) file, you can set `enable_chaos_cpu_stress = true` there instead.)*

2.  **Review Experiment Details (Optional but recommended):** Examine the specific experiment YAML to confirm its targets. For CPU stress, check [`terraform/chaos-cpu-stress/cpu-stress.yaml`](terraform/chaos-cpu-stress/cpu-stress.yaml) to see which Kubernetes labels it selects for stress application.

#### Step 4: Apply the Experiment Configuration

Apply the changes again. Terraform will now provision the `kubernetes_manifest` resource defined in [`terraform/chaos-cpu-stress/main.tf`](terraform/chaos-cpu-stress/main.tf), which creates the actual Chaos Experiment resource.

Execute:
```bash
terraform apply -var="enable_chaos_cpu_stress=true"
```

The execution of the experiment starts immediately upon the creation of the resource, provided the experiment YAML is valid and its targets exist.

#### Step 5: Monitor and Clean Up

1.  **Monitoring:** You can monitor the experiment status using `kubectl` targeting the namespace defined (usually `litmus` or `tests`):
    ```bash
    kubectl get chaosexperiment -n litmus
    # Or check the status of the execution:
    kubectl get litmuschaosresults -n litmus
    ```

2.  **Cleanup:** To tear down the deployed infrastructure, including the specific experiment and the base LitmusChaos installation (if no other experiments rely on it), execute:
    ```bash
    terraform destroy
    ```
    *Note: You may need to explicitly disable the experiment variables if you only want to destroy the experiment but keep the framework, or vice-versa.*
