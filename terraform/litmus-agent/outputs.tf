output "depends_on_crds" {
  value = helm_release.litmus_agent.id
}
