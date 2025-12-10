# Wazuh Performance Tests

This repository contains Terraform configurations for deploying infrastructure to perform performance tests on Wazuh.

## Project Structure

This project is organized into the following main directories and files:

- [`README.md`](README.md): Provides a comprehensive overview of the project, including its purpose, structure, setup instructions, and how to run tests and view results.
- [`recommendations.md`](recommendations.md): Contains recommendations and best practices for performance testing with Wazuh.
- [`scripts/`](scripts/): This directory holds all the Python scripts necessary for orchestrating the performance tests.
  - [`scripts/generate_report.py`](scripts/generate_report.py): Script responsible for processing test results and generating an HTML report.
  - [`scripts/requirements.txt`](scripts/requirements.txt): Lists the Python dependencies required to run the scripts.
  - [`scripts/run_tests.py`](scripts/run_tests.py): The main orchestration script that initiates Terraform deployments, waits for test completion, collects results, and triggers report generation.
  - [`scripts/test_results.json`](scripts/test_results.json): A placeholder file containing mock test data used for report generation.
- [`terraform/`](terraform/): Contains all Terraform configurations for deploying the necessary infrastructure.
  - [`terraform/.terraform.lock.hcl`](terraform/.terraform.lock.hcl): Terraform's dependency lock file.
  - [`terraform/main.tf`](terraform/main.tf): The primary Terraform configuration file that orchestrates the deployment of various modules.
  - [`terraform/outputs.tf`](terraform/outputs.tf): Defines the outputs from the Terraform deployment.
  - [`terraform/variables.tf`](terraform/variables.tf): Declares input variables for the Terraform configurations.
  - [`terraform/.terraform/`](terraform/.terraform/): Directory where Terraform stores plugins and modules.
  - [`terraform/chaos-network-delay/`](terraform/chaos-network-delay/): Terraform module designed to introduce network latency and simulate network degradation.
    - [`terraform/chaos-network-delay/main.tf`](terraform/chaos-network-delay/main.tf): Main configuration for network delay injection.
    - [`terraform/chaos-network-delay/outputs.tf`](terraform/chaos-network-delay/outputs.tf): Outputs specific to the network delay module.
    - [`terraform/chaos-network-delay/variables.tf`](terraform/chaos-network-delay/variables.tf): Variables for configuring network delay.
  - [`terraform/stress-cpu/`](terraform/stress-cpu/): Terraform module to simulate high CPU load on target systems.
    - [`terraform/stress-cpu/main.tf`](terraform/stress-cpu/main.tf): Main configuration for CPU stress testing.
    - [`terraform/stress-cpu/outputs.tf`](terraform/stress-cpu/outputs.tf): Outputs specific to the CPU stress module.
    - [`terraform/stress-cpu/variables.tf`](terraform/stress-cpu/variables.tf): Variables for configuring CPU stress.
  - [`terraform/wazuh-log-generator/`](terraform/wazuh-log-generator/): Terraform module for generating simulated Wazuh logs to test the SIEM's ingestion and processing capabilities.
    - [`terraform/wazuh-log-generator/main.tf`](terraform/wazuh-log-generator/main.tf): Main configuration for the log generator.
    - [`terraform/wazuh-log-generator/outputs.tf`](terraform/wazuh-log-generator/outputs.tf): Outputs specific to the log generator module.
    - [`terraform/wazuh-log-generator/variables.tf`](terraform/wazuh-log-generator/variables.tf): Variables for configuring the log generator.
- [`test_report/`](test_report/): This directory will contain the generated HTML report after the tests are executed.
  - [`test_report/index.html`](test_report/index.html): The main HTML file for the performance test report.
  - [`test_report/style.css`](test_report/style.css): The stylesheet for the HTML report.

## Getting Started
To use these configurations, ensure you have Terraform installed and configured with the necessary cloud provider credentials.

## Running Tests

To execute the performance tests and generate the report, follow these steps:

1.  **Install Dependencies:**
    Ensure you have Python 3 installed, then install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Test Suite:**
    Execute the orchestration script:
    ```bash
    python3 scripts/run_tests.py
    ```
    This script will:
    *   Initialize and apply the Terraform configuration.
    *   Wait for the test jobs to complete.
    *   Collect the results (currently using mock data based on `test_results.json`).
    *   Generate an HTML report.

3.  **View Results:**
    The generated HTML report will be available in the `test_report/` directory. Open `test_report/index.html` in your browser to view the detailed analysis.