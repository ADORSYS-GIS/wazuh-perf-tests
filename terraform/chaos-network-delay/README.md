# Network Chaos Module

This module provisions a Chaos Mesh network chaos experiment that introduces latency into the network.

**Note:** This module is not fully functional at this time due to a known issue with the Terraform Kubernetes provider. For more information, please see the main `README.md` file.

## Resources

This module creates the following resources:

*   **`kubernetes_manifest.network_chaos`**: This resource defines the network chaos experiment.

## Configuration

The following variables can be used to configure the module:

*   **`action`**: The type of network chaos to introduce. Can be one of `delay`, `loss`, `duplicate`, `corrupt`, or `bandwidth`.
*   **`latency`**: The amount of latency to introduce, in milliseconds.
*   **`loss_percentage`**: The percentage of packets to drop.
*   **`duplicate_percentage`**: The percentage of packets to duplicate.
*   **`corrupt_percentage`**: The percentage of packets to corrupt.
*   **`bandwidth_rate`**: The bandwidth rate to enforce.

## Usage

To use the module, you can add the following to your Terraform configuration:

```terraform
module "chaos_network" {
  source = "./modules/chaos-network-delay"

  action  = "delay"
  latency = "200ms"
}
```
