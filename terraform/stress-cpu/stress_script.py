import argparse
import json
import os
import subprocess
import sys
import time

def run_stress_test(cpu_count, timeout_seconds):
    """
    Executes the 'stress' command with specified CPU count and timeout.
    Returns a dictionary of metrics.
    """
    start_time = time.time()
    success = False
    error_message = None
    duration = 0

    # Run the stress command in a subprocess
    try:
        command = ["stress", "--cpu", str(cpu_count), "--timeout", f"{timeout_seconds}s"]
        
        # Execute the command and capture output/errors
        subprocess.run(command, capture_output=True, text=True, check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        success = True
        
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        error_message = f"Stress command failed: {e.stderr.strip()}"
        print(f"Error: {error_message}", file=sys.stderr)
    except FileNotFoundError:
        duration = time.time() - start_time
        error_message = "Stress command not found. Ensure 'stress' is installed in the container."
        print(f"Error: {error_message}", file=sys.stderr)
    except Exception as e:
        duration = time.time() - start_time
        error_message = f"An unexpected error occurred: {str(e)}"
        print(f"Error: {error_message}", file=sys.stderr)
    
    metrics = {
        "test_name": "cpu_stress_test",
        "cpu_count": cpu_count,
        "timeout_seconds": timeout_seconds,
        "actual_duration_seconds": round(duration, 2),
        "success": success,
        "error_message": error_message,
        "load_average_at_end": os.getloadavg() if hasattr(os, 'getloadavg') else None
    }
    
    return metrics

def main():
    parser = argparse.ArgumentParser(
        description="CPU Stress Test Script",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Use environment variables as defaults if available
    env_cpu_count = os.environ.get("STRESS_CPU_COUNT")
    env_timeout = os.environ.get("STRESS_TIMEOUT_SECONDS")

    parser.add_argument(
        "--cpu-count", 
        type=int, 
        default=int(env_cpu_count) if env_cpu_count and env_cpu_count.isdigit() else 1,
        help="Number of CPU workers to spawn."
    )
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=int(env_timeout) if env_timeout and env_timeout.isdigit() else 60,
        help="Timeout in seconds for the stress test."
    )

    args = parser.parse_args()

    # Input validation
    if args.cpu_count <= 0:
        print("Error: --cpu-count must be a positive integer.", file=sys.stderr)
        sys.exit(1)
    if args.timeout <= 0:
        print("Error: --timeout must be a positive integer.", file=sys.stderr)
        sys.exit(1)

    metrics = run_stress_test(args.cpu_count, args.timeout)
    print(json.dumps(metrics))

    if not metrics["success"]:
        sys.exit(1)

if __name__ == "__main__":
    main()
