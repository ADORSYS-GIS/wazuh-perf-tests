# Wazuh Performance and Reliability Testing Framework

This project provides a framework for conducting performance and reliability tests on Wazuh environments. It uses Terraform to provision the necessary infrastructure and orchestrate the execution of various test scenarios.

## Overview

The framework is designed to be flexible and extensible, allowing users to define their own test scenarios and metrics. It currently includes modules for:

*   **CPU Stress Testing**: Simulates high CPU load on the Wazuh manager and agent nodes.
*   **Network Chaos Testing**: Introduces network latency, packet loss, and other chaos engineering experiments to test the resilience of the Wazuh environment.

## Known Issues

The current version of the framework has a known issue with the Terraform configuration for the network chaos testing module. Specifically, the `kubernetes_manifest` resource used to manage the Chaos Mesh CRDs is not functioning as expected. This is due to an incompatibility between the Terraform Kubernetes provider and the way Chaos Mesh uses finalizers to manage the lifecycle of its resources.

The following attempts have been made to resolve this issue, without success:

*   Using the `ignore_changes` lifecycle argument to prevent Terraform from managing the `finalizers` field.
*   Using a `null_resource` with a `local-exec` provisioner to remove the finalizers using `kubectl patch`.
*   Explicitly setting the `finalizers` field to an empty list in the manifest.

As a result of this issue, the network chaos testing module is not fully functional at this time. The CPU stress testing module, however, is fully functional.

## Getting Started

To get started with the framework, you will need to have the following dependencies installed:

*   Terraform
*   kubectl
*   A running Kubernetes cluster

Once you have these dependencies installed, you can clone the repository and run the following command to initialize the Terraform workspace:

```bash
terraform init
```

To run the CPU stress test, you can use the following command:

```bash
python3 scripts/run_tests.py --enable-cpu-stress
```

## Interpreting the Results

The results of the tests are stored in the `output` directory. The `test_results.json` file contains a summary of the test results, including the following metrics:

*   `cpu_usage`: The average CPU usage during the test.
*   `memory_usage`: The average memory usage during the test.
*   `network_latency`: The average network latency during the test.

The `raw_logs` directory contains the raw logs from the test pods. These logs can be used to further investigate any issues that may have occurred during the test.
