import subprocess
import time
import json
from pathlib import Path
import datetime
from kubernetes import client, config, stream
import sys
import argparse
import shutil

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



def get_litmus_chaos_status(namespace, kubeconfig=None, context=None, engine_name=None):
    """Queries LitmusChaos Engine status for a given chaos experiment."""
    print("Checking LitmusChaos Engine status...")
    try:
        config.load_kube_config(config_file=kubeconfig, context=context)
        custom_api = client.CustomObjectsApi()
        chaos_engine = custom_api.get_namespaced_custom_object(
            group="litmuschaos.io",
            version="v1alpha1",
            namespace=namespace,
            plural="chaosengines",
            name=engine_name
        )
        status = "failed"
        error_msg = ""
        if isinstance(chaos_engine, dict):
            status_dict = chaos_engine.get("status", {})
            if isinstance(status_dict, dict):
                experiments = status_dict.get("experiments", [])
                if experiments:
                    exp_status = experiments[0].get("status", "")
                    if exp_status in ["Running", "Completed", "Passed"]:
                        status = "passed"
                    else:
                        status = "failed"
                        error_msg = f"LitmusChaos experiment status: {exp_status}"
                else:
                    error_msg = "No experiments found in ChaosEngine status."
        return {"status": status, "error_message": error_msg}
    except client.ApiException as e:
        if e.status == 404:
            return {"status": "failed", "error_message": "LitmusChaosEngine not found."}
        return {"status": "failed", "error_message": f"API error checking LitmusChaos status: {e}"}
    except Exception as e:
        return {"status": "failed", "error_message": f"Unexpected error checking LitmusChaos status: {e}"}

def collect_stress_metrics(output_dir, namespace, kubeconfig=None, context=None):
    """
    Retrieves metrics.csv from stress pods.
    """
    print("\n--- Collecting System Metrics from Stress Pods ---")
    metrics_output_dir = output_dir / "stress_metrics"
    metrics_output_dir.mkdir(parents=True, exist_ok=True)

    config.load_kube_config(config_file=kubeconfig, context=context)
    api = client.CoreV1Api()

    # List all pods in the test namespace with stress labels
    # Note: Network stress uses iperf-client label
    selectors = ["app=cpu-stress", "app=memory-stress", "app=disk-stress", "app=iperf-client"]
    for selector in selectors:
        pods = api.list_namespaced_pod(namespace=namespace, label_selector=selector)
        for pod in pods.items:
            pod_name = pod.metadata.name
            print(f"Collecting metrics from pod: {pod_name}")
            remote_path = "/tmp/metrics.csv"
            dest_path = metrics_output_dir / f"{pod_name}_metrics.csv"
            
            try:
                cp_command = ["kubectl", "cp", f"{namespace}/{pod_name}:{remote_path}", str(dest_path)]
                if kubeconfig:
                    cp_command.extend(["--kubeconfig", kubeconfig])
                if context:
                    cp_command.extend(["--context", context])
                
                subprocess.run(cp_command, check=False, capture_output=True)
            except Exception as e:
                print(f"  - Failed to collect metrics from {pod_name}: {e}")

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

def _parse_network_chaos_results(chaos_status, test_name="Network Chaos Test"):
    """Helper to format network chaos test results."""
    if not chaos_status:
        return None
    
    return {
        "name": test_name,
        "status": chaos_status["status"],
        "duration": 60,
        "test_cases": [
            {
                "name": f"Execute {test_name}",
                "status": chaos_status["status"],
                "duration": 60,
                "metrics": {},
                "error_message": chaos_status["error_message"]
            }
        ]
    }

def parse_results_to_report_format(raw_results, test_duration, chaos_status, chaos_test_name=None):
    """Parses raw log data and formats it for the HTML report generator."""
    print("Parsing raw results into report format...")
    test_suites = []


    # --- REPORTING FOR CHAOS EXPERIMENTS ---
    if chaos_status:
        chaos_result = _parse_network_chaos_results(chaos_status, chaos_test_name or "Chaos Experiment")
        if chaos_result:
            test_suites.append(chaos_result)

    return test_suites

def collect_cluster_environment():
    try:
        config.load_kube_config()
    except:
        config.load_incluster_config()

    v1 = client.CoreV1Api()
    nodes_info = []

    nodes = v1.list_node().items
    if not nodes:
        return {
            "os": "Unknown",
            "cpu": "Unknown",
            "memory": "Unknown",
            "nodes": []
        }

    # Aggregate info from first node for summary, and keep all nodes details
    first_node = nodes[0]
    
    def parse_memory(mem_str):
        if not mem_str: return 0
        if mem_str.endswith('Ki'):
            return int(mem_str[:-2]) / 1024
        elif mem_str.endswith('Mi'):
            return int(mem_str[:-2])
        elif mem_str.endswith('Gi'):
            return int(mem_str[:-2]) * 1024
        return int(mem_str)

    for node in nodes:
        capacity = node.status.capacity
        allocatable = node.status.allocatable
        nodes_info.append({
            "name": node.metadata.name,
            "os": node.status.node_info.operating_system,
            "os_version": node.status.node_info.os_image,
            "kernel_version": node.status.node_info.kernel_version,
            "architecture": node.status.node_info.architecture,
            "kubelet_version": node.status.node_info.kubelet_version,
            "cpu_capacity": capacity.get("cpu"),
            "cpu_allocatable": allocatable.get("cpu"),
            "memory_capacity_mb": parse_memory(capacity.get("memory")),
            "memory_allocatable_mb": parse_memory(allocatable.get("memory")),
            "pods_allocatable": allocatable.get("pods")
        })

    return {
        "os": first_node.status.node_info.os_image,
        "cpu": first_node.status.capacity.get("cpu"),
        "memory": f"{parse_memory(first_node.status.capacity.get('memory'))} MB",
        "nodes": nodes_info
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
    parser.add_argument('--enable-chaos-pod-delete', action='store_true', help="Enable the LitmusChaos Pod Delete experiment.")
    parser.add_argument('--enable-chaos-network-latency', action='store_true', help="Enable the LitmusChaos Network Latency experiment.")
    parser.add_argument('--enable-chaos-cpu-stress', action='store_true', help="Enable the LitmusChaos CPU Stress experiment.")
    parser.add_argument('--enable-chaos-disk-stress', action='store_true', help="Enable the LitmusChaos Disk Stress experiment.")
    parser.add_argument('--enable-chaos-memory-stress', action='store_true', help="Enable the LitmusChaos Memory Stress experiment.")
    parser.add_argument('--kubeconfig', type=str, default=None, help="Path to the kubeconfig file.")
    parser.add_argument('--context', type=str, default=None, help="The context to use from the kubeconfig file.")
    parser.add_argument('--job-timeout', type=int, default=600, help="Timeout in seconds for waiting on Kubernetes jobs to complete.")
    args = parser.parse_args()

    current_script_dir = Path(__file__).parent
    terraform_dir = current_script_dir.parent / "terraform"
    output_dir = current_script_dir.parent / "output"
    
    # Artifact Organization: Use timestamped directory
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_output_dir = output_dir / timestamp
    run_output_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = run_output_dir / "test_results.json"
    global_results_file = output_dir / "test_results.json"
    
    all_test_suites = []

    try:
        print("\n--- Initializing Terraform ---")
        run_command(["terraform", "init"], cwd=terraform_dir)

        chaos_experiments = []
        if args.enable_chaos_pod_delete:
            chaos_experiments.append({"name": "Pod Delete Chaos", "module": "chaos_pod_delete", "engine_name": "pod-delete-chaos"})
        if args.enable_chaos_network_latency:
            chaos_experiments.append({"name": "Network Latency Chaos", "module": "chaos_network_latency", "engine_name": "network-latency-chaos"})
        if args.enable_chaos_cpu_stress:
            chaos_experiments.append({"name": "CPU Stress Chaos", "module": "chaos_cpu_stress", "engine_name": "cpu-stress-chaos"})
        if args.enable_chaos_disk_stress:
            chaos_experiments.append({"name": "Disk Stress Chaos", "module": "chaos_disk_stress", "engine_name": "disk-stress-chaos"})
        if args.enable_chaos_memory_stress:
            chaos_experiments.append({"name": "Memory Stress Chaos", "module": "chaos_memory_stress", "engine_name": "memory-stress-chaos"})

        if not chaos_experiments:
            print("No chaos experiments enabled. Running standard performance test.")
            chaos_experiments.append({"name": "Standard Performance Test", "module": None, "engine_name": None})

        for experiment in chaos_experiments:
            print(f"\n--- Running Chaos Experiment: {experiment['name']} ---")
            
            try:
                print("\n--- Applying Terraform Configuration ---")
                apply_command = ["terraform", "apply", "-auto-approve"]
                if experiment["module"]:
                    apply_command.append(f"-target=module.{experiment['module']}")
                
                run_command(apply_command, cwd=terraform_dir)

                print("\n--- Waiting for workloads to stabilize and run ---")
                tf_outputs = get_terraform_outputs(terraform_dir)
                test_namespace = tf_outputs.get("namespace", {}).get("value", "tests")
                print(f"Using test namespace: {test_namespace}")

                # For LitmusChaos, we wait for the ChaosEngine to complete
                chaos_status = None  # Ensure variable is defined even when no engine is used
                if experiment["engine_name"]:
                    chaos_status = get_litmus_chaos_status(test_namespace, kubeconfig=args.kubeconfig, context=args.context, engine_name=experiment["engine_name"])
                    if chaos_status["status"] == "failed":
                        raise RuntimeError(f"Chaos experiment {experiment['name']} failed: {chaos_status['error_message']}")
                
                print(f"\n--- Running tests for {args.test_duration} seconds ---")
                time.sleep(args.test_duration)
                
                print("\n--- Collecting and Parsing Results ---")
                # Collect only cluster-level logs; focusing on performance metrics rather than specific workloads.
                workloads_to_collect = []
                if args.enable_chaos_cpu_stress:
                    workloads_to_collect.append({"name": "cpu-stress", "selector": "app=cpu-stress", "namespace": test_namespace})

                # Add Wazuh components for log collection
                suites = parse_results_to_report_format(None, args.test_duration, chaos_status if experiment["engine_name"] else None, chaos_test_name=experiment['name'] if experiment["engine_name"] else None)
                all_test_suites.extend(suites)

            except Exception as e:
                print(f"Error during test execution: {e}")
            finally:
                # Collect artifacts regardless of test success, before destruction
                try:
                    tf_outputs = get_terraform_outputs(terraform_dir)
                    test_namespace = tf_outputs.get("namespace", {}).get("value", "tests")
                    collect_stress_metrics(run_output_dir, test_namespace, kubeconfig=args.kubeconfig, context=args.context)
                except Exception as e:
                    print(f"Failed to collect some artifacts: {e}")

                # Destroy resources after each chaos scenario to ensure clean state for next test
                if not args.skip_destroy:
                    print("\n--- Destroying Terraform Resources after scenario ---")
                    run_command(["terraform", "destroy", "-auto-approve", f"-target=module.{experiment['module']}"], cwd=terraform_dir)

        report_data = {
            "report_title": "Wazuh Performance Test Report",
            "test_run_id": f"run-{int(time.time())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "environment": collect_cluster_environment(),
            "test_parameters": {"duration_minutes": args.test_duration / 60},
            "test_suites": all_test_suites
        }
        
        # Write results to the timestamped directory
        print(f"Creating {results_file}")
        with open(results_file, "w") as f:
            json.dump(report_data, f, indent=2)

        # Update global test_results.json if it exists, otherwise create it
        if global_results_file.exists():
            print(f"Updating global {global_results_file}")
            with open(global_results_file, "r") as f:
                try:
                    global_data = json.load(f)
                    global_data.setdefault("test_suites", []).extend(all_test_suites)
                except json.JSONDecodeError:
                    global_data = report_data
            with open(global_results_file, "w") as f:
                json.dump(global_data, f, indent=2)
        else:
            print(f"Creating global {global_results_file}")
            with open(global_results_file, "w") as f:
                json.dump(report_data, f, indent=2)

        print("\n--- Generating HTML Report ---")
        run_command(["python3", str(current_script_dir / "generate_report.py"), str(run_output_dir)], cwd=current_script_dir.parent)
        
        # Copy the report to the timestamped directory
        report_src = output_dir / "test_report"
        if report_src.exists():
            report_dest = run_output_dir / "test_report"
            shutil.copytree(report_src, report_dest, dirs_exist_ok=True)
            print(f"\nPerformance test run complete. Report saved in '{report_dest}'")

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

    finally:
        if not args.skip_destroy:
            print("\n--- Destroying all remaining Terraform Resources ---")
            run_command(["terraform", "destroy", "-auto-approve"], cwd=terraform_dir)
        else:
            print("\n--- Skipping Terraform Destroy ---")

if __name__ == "__main__":
    main()
