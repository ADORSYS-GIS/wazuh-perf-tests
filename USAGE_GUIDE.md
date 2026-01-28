# Usage Guide for Wazuh Litmus Chaos Testing Environment

This document provides instructions on how to manage, run, observe, and interpret the results of chaos experiments orchestrated via Terraform.

## Overview

The chaos experiments are defined as reusable Terraform modules. The root configuration file, [`terraform/main.tf`](terraform/main.tf), orchestrates the deployment of the necessary LitmusChaos components (Chaos Experiments, Chaos Engines, and necessary prerequisites) using these modules.

## Running Experiments

By default, all defined experiments are enabled.

### Disabling an Experiment

To disable a specific experiment, you must comment out both the `module` block for the experiment itself and the corresponding `module` block for the `chaos-engine` in [`terraform/main.tf`](terraform/main.tf).

For example, to disable the `pod-delete` experiment, modify [`terraform/main.tf`](terraform/main.tf) as follows:

```hcl
# Example modification in terraform/main.tf

# Comment out the experiment module block
# module "chaos-pod-delete" {
#   source = "./chaos-pod-delete"
#   ...
# }

# Comment out the corresponding engine module block
# module "chaos-engine-pod-delete" {
#   source = "./chaos-engine"
#   ...
# }
```

### Applying Changes

After modifying the configuration in `terraform/main.tf`, you must apply the changes to the environment:

```bash
terraform -chdir=terraform apply -auto-approve
```

## Observing Experiments

Once an experiment is triggered, you can monitor its progress using `kubectl`.

### Watching Experiment Pods

Watch the creation and status of LitmusChaos pods in the `wazuh` namespace:

```bash
kubectl get pods -n wazuh -w
```

### Checking ChaosEngine Status

To check the status, events, and execution details of a running `ChaosEngine`, use `kubectl describe`. Replace `<chaos-engine-name>` with the actual name of the engine deployed by Terraform (often matching the experiment name):

```bash
kubectl describe chaosengine <chaos-engine-name> -n wazuh
```

## Viewing Results

After an experiment completes (whether successfully or not), LitmusChaos creates a `ChaosResult` custom resource.

### Inspecting ChaosResult

Inspect the detailed outcome of the experiment by querying the `ChaosResult`. Replace `<chaos-engine-name>` and `<experiment-name>` with the appropriate values:

```bash
kubectl get chaosresult <chaos-engine-name>-<experiment-name> -n wazuh -o yaml
```

## Customizing Experiments

The behavior and targets of the experiments can be customized.

### Experiment Parameters

The core operational parameters for each experiment (such as duration, stress level, or target selectors) are defined within the YAML configuration files located inside their respective module directories.

For example, CPU stress parameters are in: [`terraform/chaos-cpu-stress/cpu-stress.yaml`](terraform/chaos-cpu-stress/cpu-stress.yaml)

### Global Variables

Global configuration variables, such as the label used to select the target application for all experiments, are stored in the root variables file: [`terraform/terraform.tfvars`](terraform/terraform.tfvars)

"