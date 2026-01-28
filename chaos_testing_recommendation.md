# Recommendation: Replace Chaos Testing Modules

## Analysis of Existing Modules

### `chaos-network-delay`

*   **Purpose:** Introduces network latency to test the resilience of the system.
*   **Problem:** This module is not functional due to a known issue with the Terraform Kubernetes provider and its interaction with the Chaos Mesh CRDs. The use of `kubernetes_manifest` is the likely cause of the problem.
*   **Effort to Fix:** Fixing this would require a significant rewrite of the module to use a more reliable method of deploying Chaos Mesh experiments, potentially using the Helm provider or a custom provider. This would be a complex and time-consuming task.

### `stress-*` Modules (CPU, Disk, Memory, Network)

*   **Purpose:** These modules use the `stress` tool to apply load to various system resources.
*   **Problem:** While functional, these modules use the older `stress` tool. The more modern `stress-ng` tool offers a wider range of stressors and more precise control over the stress tests.
*   **Effort to Improve:** Upgrading to `stress-ng` would require updating the Python scripts and Terraform configurations. This is a moderate amount of work.

## Alternative: LitmusChaos

LitmusChaos is a popular, open-source, and CNCF-incubating chaos engineering framework for Kubernetes. It provides a wide range of chaos experiments and integrates well with CI/CD pipelines.

### Benefits of LitmusChaos

*   **Kubernetes-Native:** Litmus is designed specifically for Kubernetes, making it a natural fit for this project.
*   **Rich Experiment Library:** Litmus offers a large library of pre-defined chaos experiments, covering a wide range of scenarios.
*   **Extensible:** You can create custom experiments to meet your specific needs.
*   **Community Support:** Litmus has a strong and active community.

## Recommendation

I recommend replacing the existing chaos testing modules with LitmusChaos.

### Justification

*   **Cost-Benefit Analysis:** The effort required to fix the `chaos-network-delay` module is high, and the result would still be a custom solution that needs to be maintained. The `stress-*` modules could be improved, but they would still be using a less powerful tool. By switching to LitmusChaos, we can leverage a powerful, well-supported, and feature-rich framework for a similar or lower amount of effort.
*   **Long-Term Value:** LitmusChaos will provide more value in the long run by enabling a wider range of chaos experiments and better integration with the existing CI/CD pipeline.

## Plan

1.  **Remove Existing Chaos Modules:** Delete the `terraform/chaos-network-delay`, `terraform/stress-cpu`, `terraform/stress-disk`, `terraform/stress-memory`, and `terraform/stress-network` directories.
2.  **Install LitmusChaos:** Create a new Terraform module to install LitmusChaos using its Helm chart.
3.  **Create LitmusChaos Experiments:** Create new Terraform modules to define LitmusChaos experiments that replicate the functionality of the old modules (network delay, CPU stress, etc.).
4.  **Update CI/CD Pipeline:** Update the CI/CD pipeline to run the new LitmusChaos experiments.
