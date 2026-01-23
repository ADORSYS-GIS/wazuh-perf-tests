import subprocess
import time
import json
from pathlib import Path
import datetime
from kubernetes import client, config
import sys
import argparse

def run_command(command, cwd=None, check=True):
    """Executes a command and returns its output."""
    print(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, check=False) # Always capture output, handle check manually
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        if check: # Only raise exception if check is True
            raise subprocess.CalledProcessError(result.returncode, command, output=result.stdout, stderr=result.stderr)
    return result.stdout

def wait_for_resources_to_be_ready(namespace, kubeconfig=None, context=None, job_names=None, deployment_names=None, timeout=600):
    """Waits for specified jobs to complete and deployments to be ready in a namespace."""
    config.load_kube_config(config_file=kubeconfig, context=context)
    batch_api = client.BatchV1Api()
    apps_api = client.AppsV1Api()

    if job_names:
        for job_name in job_names:
            print(f"Waiting for job '{job_name}' to complete...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    job = batch_api.read_namespaced_job_status(name=job_name, namespace=namespace)
                    if isinstance(job, client.V1Job) and job.status:
                        if job.status.succeeded:
                            print(f"Job '{job_name}' completed successfully.")
                            break
                        if job.status.failed:
                            print(f"Job '{job_name}' failed.")
                            raise RuntimeError(f"Job '{job_name}' failed.")
                except client.ApiException as e:
                    if e.status == 404:
                        print(f"Waiting for job '{job_name}' to be created...")
                    else:
                        print(f"Error checking job status for '{job_name}': {e}")
                time.sleep(15)
            else:
                raise TimeoutError(f"Job '{job_name}' did not complete in {timeout} seconds.")

    if deployment_names:
        for deployment_name in deployment_names:
            print(f"Waiting for deployment '{deployment_name}' to be ready...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    deployment = apps_api.read_namespaced_deployment_status(name=deployment_name, namespace=namespace)
                    if (isinstance(deployment, client.V1Deployment) and deployment.status and
                            deployment.status.ready_replicas is not None and
                            deployment.status.replicas is not None and
                            deployment.status.ready_replicas >= deployment.status.replicas):
                        print(f"Deployment '{deployment_name}' is ready.")
                        break
                except client.ApiException as e:
                    if e.status == 404:
                        print(f"Waiting for deployment '{deployment_name}' to be created...")
                    else:
                        print(f"Error checking deployment status for '{deployment_name}': {e}")
                time.sleep(15)
            else:
                raise TimeoutError(f"Deployment '{deployment_name}' did not become ready in {timeout} seconds.")


def collect_logs(workloads, kubeconfig=None, context=None):
    """
    Collects logs from specified workloads (jobs and deployments) by fetching logs from their pods.
    Each workload in the list should be a dictionary with 'name', 'selector', and 'namespace'.
    """
    config.load_kube_config(config_file=kubeconfig, context=context)
    api = client.CoreV1Api()
    all_results = {}

    for workload in workloads:
        name = workload['name']
        selector = workload['selector']
        namespace = workload['namespace']
        
        print(f"Collecting logs for: {name} in namespace {namespace} with selector {selector}")
        pod_list = api.list_namespaced_pod(namespace=namespace, label_selector=selector)
        
        if not pod_list.items:
            print(f"  - WARNING: No pods found for selector '{selector}' in namespace '{namespace}'.")
            all_results[name] = ""
            continue

        logs = ""
        for pod in pod_list.items:
            try:
                pod_log = api.read_namespaced_pod_log(name=pod.metadata.name, namespace=namespace)
                logs += pod_log
                print(f"  - Collected {len(pod_log.splitlines())} lines from pod: {pod.metadata.name}")
            except client.ApiException as e:
                print(f"  - Could not retrieve logs for pod {pod.metadata.name}: {e}")
        all_results[name] = logs

    return all_results

def get_chaos_test_status(namespace, kubeconfig=None, context=None):
    """Queries the Kubernetes API for the status of the NetworkChaos experiment."""
    print("Checking status of Network Chaos experiment...")
    try:
        config.load_kube_config(config_file=kubeconfig, context=context)
        custom_api = client.CustomObjectsApi()
        
        chaos_object = custom_api.get_namespaced_custom_object(
            group="chaos-mesh.org",
            version="v1alpha1",
            namespace=namespace,
            plural="networkchaos",
            name="network-delay-chaos"
        )
        
        status = "Unknown"
        if isinstance(chaos_object, dict):
            status_dict = chaos_object.get("status")
            if isinstance(status_dict, dict):
                experiment_dict = status_dict.get("experiment")
                if isinstance(experiment_dict, dict):
                    status = experiment_dict.get("phase", "Unknown")
        if status == "Finished":
            return {"status": "passed", "error_message": ""}
        else:
            return {"status": "failed", "error_message": f"Chaos experiment ended with status: {status}"}
            
    except client.ApiException as e:
        if e.status == 404:
            return {"status": "failed", "error_message": "NetworkChaos custom object not found."}
        return {"status": "failed", "error_message": f"API error checking chaos status: {e}"}
    except Exception as e:
        return {"status": "failed", "error_message": f"An unexpected error occurred while checking chaos status: {e}"}


def _parse_cpu_stress_results(raw_logs, default_duration):
    """Helper to parse CPU stress test logs."""
    if not raw_logs:
        return {
            "name": "CPU Stress Test", "status": "failed", "duration": default_duration,
            "test_cases": [{"name": "Parse CPU Stress Results", "status": "failed", "duration": default_duration, "metrics": {}, "error_message": "No logs found."}]
        }

    logs = raw_logs.strip().split('\n')
    metrics = None
    
    # Robustly find the JSON line
    for line in logs:
        stripped_line = line.strip()
        if stripped_line.startswith('{') and "load_average" in stripped_line:
            try:
                metrics = json.loads(stripped_line)
                break
            except json.JSONDecodeError:
                continue
    
    if metrics:
        status = "passed" if metrics.get("success") else "failed"
        return {
            "name": "CPU Stress Test", "status": status, "duration": metrics.get("actual_duration_seconds", 0),
            "test_cases": [{"name": "Verify performance under CPU load", "status": status, "duration": metrics.get("actual_duration_seconds", 0), "metrics": metrics, "error_message": metrics.get("error_message", "")}]
        }
    else:
        return {
            "name": "CPU Stress Test", "status": "failed", "duration": default_duration,
            "test_cases": [{"name": "Parse CPU Stress Results", "status": "failed", "duration": default_duration, "metrics": {}, "error_message": "Could not find a valid JSON result line with metrics."}]
        }

def _parse_network_chaos_results(chaos_status):
    """Helper to format network chaos test results."""
    if not chaos_status:
        return None
    
    return {
        "name": "Network Delay Chaos Test", "status": chaos_status["status"], "duration": 60,
        "test_cases": [{"name": "Inject 100ms network delay", "status": chaos_status["status"], "duration": 60, "metrics": {}, "error_message": chaos_status["error_message"]}]
    }

def parse_results_to_report_format(raw_results, test_duration, chaos_status):
    """Parses raw log data and formats it for the HTML report generator."""
    print("Parsing raw results into report format...")
    test_suites = []

    # --- PARSING LOGIC FOR CPU STRESS TEST ---
    if "cpu-stress" in raw_results:
        test_suites.append(_parse_cpu_stress_results(raw_results["cpu-stress"], test_duration))

    # --- PARSING LOGIC FOR WAZUH POD LOGS ---
    wazuh_component_logs = {k: v for k, v in raw_results.items() if k.startswith("wazuh-helm-")}
    
    total_wazuh_logs_collected = 0
    wazuh_test_cases = []
    
    for component_name, logs_content in wazuh_component_logs.items():
        logs = logs_content.strip().split('\n')
        component_log_count = len([l for l in logs if l])
        total_wazuh_logs_collected += component_log_count
        
        component_status = "passed" if component_log_count > 0 else "failed"
        component_error_msg = f"No logs collected for {component_name}." if component_log_count == 0 else ""
        
        wazuh_test_cases.append({
            "name": f"Verify log collection for {component_name}",
            "status": component_status,
            "duration": test_duration,
            "metrics": {"logs_collected": component_log_count},
            "error_message": component_error_msg
        })

    if wazuh_component_logs:
        overall_wazuh_status = "passed" if total_wazuh_logs_collected > 0 else "failed"
        overall_wazuh_error_msg = "No Wazuh logs collected from any component." if total_wazuh_logs_collected == 0 else ""

        test_suites.append({
            "name": "Wazuh Pod Log Collection",
            "status": overall_wazuh_status,
            "duration": test_duration,
            "test_cases": wazuh_test_cases,
            "metrics": {"total_wazuh_logs_collected": total_wazuh_logs_collected},
            "error_message": overall_wazuh_error_msg
        })

    # --- REPORTING FOR NETWORK CHAOS TEST ---
    network_chaos_result = _parse_network_chaos_results(chaos_status)
    if network_chaos_result:
        test_suites.append(network_chaos_result)

    return {
        "report_title": "Wazuh Performance Test Report", "test_run_id": f"run-{int(time.time())}", "timestamp": datetime.datetime.now().isoformat(),
        "environment": {"os": "Linux", "cpu": "Dynamic", "memory": "Dynamic"}, "test_parameters": {"duration_minutes": test_duration / 60},
        "test_suites": test_suites
    }

def get_terraform_outputs(terraform_dir):
    """Fetches outputs from Terraform in JSON format."""
    print("Fetching Terraform outputs...")
    output = run_command(["terraform", "output", "-json"], cwd=terraform_dir)
    return json.loads(output)

def main():
    """Main function to orchestrate the performance tests."""
    parser = argparse.ArgumentParser(description="Wazuh Performance Test Orchestrator")
    parser.add_argument('--skip-destroy', action='store_true', help="If set, skips the final 'terraform destroy' step.")
    parser.add_argument('--test-duration', type=int, default=120, help="Duration of the test run in seconds.")
    parser.add_argument('--enable-cpu-stress', action='store_true', help="Enable the CPU stress test module.")
    parser.add_argument('--enable-network-chaos', action='store_true', help="Enable the network chaos test module.")
    parser.add_argument('--kubeconfig', type=str, default=None, help="Path to the kubeconfig file.")
    parser.add_argument('--context', type=str, default=None, help="The context to use from the kubeconfig file.")
    parser.add_argument('--job-timeout', type=int, default=600, help="Timeout in seconds for waiting on Kubernetes jobs to complete.")
    args = parser.parse_args()

    current_script_dir = Path(__file__).parent
    terraform_dir = current_script_dir.parent / "terraform"
    output_dir = current_script_dir.parent / "output"
    output_dir.mkdir(exist_ok=True)
    results_file = output_dir / "test_results.json"
    
    try:
        print("\n--- Initializing Terraform ---")
        run_command(["terraform", "init"], cwd=terraform_dir)

        print("\n--- Applying Terraform Configuration ---")
        apply_command = ["terraform", "apply", "-auto-approve"]
        if args.enable_cpu_stress:
            apply_command.append("-var=enable_stress_cpu=true")
        if args.enable_network_chaos:
            apply_command.append("-var=enable_chaos_network_delay=true")
        
        run_command(apply_command, cwd=terraform_dir)

        print("\n--- Waiting for workloads to stabilize and run ---")
        tf_outputs = get_terraform_outputs(terraform_dir)
        test_namespace = tf_outputs.get("namespace", {}).get("value", "tests")
        print(f"Using test namespace: {test_namespace}")

        jobs_to_wait = []
        if args.enable_cpu_stress:
            jobs_to_wait.append("cpu-stress")
        
        wait_for_resources_to_be_ready(
            namespace=test_namespace,
            job_names=jobs_to_wait,
            timeout=args.job_timeout,
            kubeconfig=args.kubeconfig,
            context=args.context
        )
        
        print(f"\n--- Running tests for {args.test_duration} seconds ---")
        time.sleep(args.test_duration)
        
        print("\n--- Collecting and Parsing Results ---")
        workloads_to_collect = [
            {"name": "wazuh-helm-pods", "selector": "app.kubernetes.io/name=wazuh-helm", "namespace": "wazuh"},
        ]
        if args.enable_cpu_stress:
            workloads_to_collect.insert(0, {"name": "cpu-stress", "selector": "app=cpu-stress", "namespace": test_namespace})

        raw_results = collect_logs(workloads_to_collect, kubeconfig=args.kubeconfig, context=args.context)
        
        chaos_status = None
        if args.enable_network_chaos:
            chaos_status = get_chaos_test_status(test_namespace, kubeconfig=args.kubeconfig, context=args.context)
        
        report_data = parse_results_to_report_format(raw_results, args.test_duration, chaos_status)
        
        with open(results_file, "w") as f:
            json.dump(report_data, f, indent=2)

        print("\n--- Generating HTML Report ---")
        run_command(["python3", str(current_script_dir / "generate_report.py"), str(results_file)], cwd=current_script_dir.parent)
        print(f"\nPerformance test run complete. Report generated in '{output_dir / 'test_report'}'")

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        if not args.skip_destroy:
            print("\n--- Destroying Terraform Resources ---")
            run_command(["terraform", "destroy", "-auto-approve"], cwd=terraform_dir)
        else:
            print("\n--- Skipping Terraform Destroy ---")

if __name__ == "__main__":
    main()
