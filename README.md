# Wazuh Performance Tests

This repository contains Terraform configurations for deploying infrastructure to perform performance tests on Wazuh.

## Structure
- `chaos-network-delay/`: Terraform module to introduce network delay.
- `stress-cpu/`: Terraform module to stress CPU.
- `wazuh-log-generator/`: Terraform module to generate Wazuh logs.
- `main.tf`: Main Terraform configuration.
- `variables.tf`: Variable definitions.
- `outputs.tf`: Output definitions.

## Getting Started
To use these configurations, ensure you have Terraform installed and configured with the necessary cloud provider credentials.