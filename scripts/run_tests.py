import subprocess
import time
import json
from kubernetes import client, config, watch
from pathlib import Path
import os

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
    Collects results from the test jobs by fetching logs from their pods.
    """
    config.load_kube_config()
    api = client.CoreV1Api()
    all_results = {}

    for job_name in job_names:
        print(f"Collecting results for job: {job_name}")
        pod_list = api.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")
        job_pods_logs = {}
        for pod in pod_list.items:
            try:
                # Assuming the job pods have only one container or we care about the first one
                pod_log = api.read_namespaced_pod_log(name=pod.metadata.name, namespace=namespace)
                job_pods_logs[pod.metadata.name] = pod_log
                print(f"  - Collected logs from pod: {pod.metadata.name}")
            except client.ApiException as e:
                print(f"  - Could not retrieve logs for pod {pod.metadata.name}: {e}")
        all_results[job_name] = job_pods_logs
    
    # In a real implementation, you would parse these logs to extract metrics.
    # For now, we'll return the raw logs.
    return all_results

def main():
    """Main function to orchestrate the performance tests."""
    # 1. Initialize and apply Terraform configuration
    # Terraform operations are now handled by the Makefile.
    # Ensure 'terraform-init' and 'terraform-apply' have been run prior to executing this script.

    current_script_dir = Path(__file__).parent
    project_root = current_script_dir.parent

    # 2. Wait for jobs to complete
    namespace = "tests"
    job_names = ["cpu-stress", "network-delay", "log-generator"] # These should match the job names in your TF modules
    print("Waiting for test jobs to complete...")
    wait_for_jobs_to_complete(namespace, job_names)

    # 3. Collect results
    print("Collecting results...")
    results_data = collect_results(namespace, job_names)
    
    with open(project_root / "output/test_results.json", "w") as f:
        json.dump(results_data, f, indent=2)

    # 4. Generate HTML report
    print("Generating HTML report...")
    # The generate_report.py script expects 'test_results.json' in the current working directory.
    run_command(["python3", str(project_root / "scripts" / "generate_report.py")], cwd=project_root)

    print("\nPerformance test run complete.")
    print("Report is in the 'test_report' directory.")

if __name__ == "__main__":
    main()