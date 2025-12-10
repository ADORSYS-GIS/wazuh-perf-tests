import subprocess
import time
import json
import os
from kubernetes import client, config, watch
from pathlib import Path

def run_command(command, cwd=None):
    """Executes a command and returns its output."""
    result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=cwd)
    return result.stdout

def wait_for_jobs_to_complete(namespace, job_names):
    """Waits for all specified jobs in a namespace to complete."""
    config.load_kube_config()
    api = client.BatchV1Api()

    for job_name in job_names:
        w = watch.Watch()
        print(f"Waiting for job: {job_name}")
        for event in w.stream(api.list_namespaced_job, namespace=namespace, field_selector=f"metadata.name={job_name}", timeout_seconds=600):
            if isinstance(event, dict) and 'object' in event:
                job = event['object']
                if hasattr(job, "status") and job.status:
                    if job.status.succeeded:
                        print(f"Job '{job_name}' has completed successfully.")
                        w.stop()
                        break
                    elif job.status.failed:
                        print(f"Job '{job_name}' has failed.")
                        w.stop()
                        break

def collect_results(namespace, job_names):
    """
    Collects results from the test jobs.
    
    This is a mock implementation. In a real-world scenario, this function
    would fetch logs from the pods of each completed job, parse them, and
    generate the results dynamically.
    """
    print("Generating mock test_results.json...")
    # In a real implementation, you would build this JSON from the logs of the test pods.
    # For now, we'll just use the existing enriched file as a template.
    with open("test_results.json", "r") as f:
        return json.load(f)

def main():
    """Main function to orchestrate the performance tests."""
    # 1. Initialize and apply Terraform configuration
    print("Initializing Terraform...")
    current_script_dir = Path(__file__).parent
    project_root = current_script_dir.parent

    # Change to project root for terraform commands
    os.chdir(project_root)

    run_command(["terraform", "init"], cwd=project_root)
    print("Applying Terraform configuration to start test jobs...")
    run_command(["terraform", "apply", "-auto-approve"], cwd=project_root)

    # Note: Subsequent file operations will now need to explicitly use paths relative to the project root
    # or ensure os.chdir is managed carefully. For now, we'll assume relative paths work from project_root
    # or that the scripts handle their own pathing correctly.

    # 2. Wait for jobs to complete
    namespace = "tests"
    job_names = ["cpu-stress", "network-delay", "log-generator"] # These should match the job names in your TF modules
    print("Waiting for test jobs to complete...")
    wait_for_jobs_to_complete(namespace, job_names)

    # 3. Collect results
    print("Collecting results...")
    results_data = collect_results(namespace, job_names)
    
    with open("test_results_final.json", "w") as f:
        json.dump(results_data, f, indent=2)

    # 4. Generate HTML report
    print("Generating HTML report...")
    # We assume generate_report.py is in the same directory
    # and it reads from a file named 'test_results.json'
    # so we will rename our final results to that.
    if os.path.exists("test_results.json"):
        os.rename("test_results.json", "test_results.json.bak")
        print("Backed up existing 'test_results.json' to 'test_results.json.bak'")

    os.rename("test_results_final.json", "test_results.json")
    run_command(["python3", "./generate_report.py"])

    print("\nPerformance test run complete.")
    print("Report is in the 'test_report' directory.")

if __name__ == "__main__":
    main()