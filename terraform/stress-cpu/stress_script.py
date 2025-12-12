import time
import json
import subprocess
import sys

def run_stress_test(cpu_count, timeout_seconds):
    start_time = time.time()
    
    # Run the stress command in a subprocess
    try:
        # Using 'stress-ng' for more control and better reporting if available,
        # otherwise fallback to 'stress'. Assuming 'stress-ng' is preferred.
        # For simplicity, let's stick to 'stress' as per original.
        command = ["stress", "--cpu", str(cpu_count), "--timeout", f"{timeout_seconds}s"]
        
        # Execute the command and capture output/errors
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Basic success metric: command ran without error
        success = True
        error_message = None
        
    except subprocess.CalledProcessError as e:
        success = False
        duration = time.time() - start_time
        error_message = f"Stress command failed: {e.stderr.strip()}"
        print(f"Error: {error_message}", file=sys.stderr)
    except FileNotFoundError:
        success = False
        duration = time.time() - start_time
        error_message = "Stress command not found. Ensure 'stress' is installed in the container."
        print(f"Error: {error_message}", file=sys.stderr)
    
    # For a simple stress test, latency isn't directly measured by 'stress' itself.
    # We can report the duration of the stress period.
    # If we were testing an application *under* stress, we'd measure its latency.
    # For now, we'll just report the duration of the stress process.
    
    metrics = {
        "test_name": "cpu_stress_test",
        "cpu_count": cpu_count,
        "timeout_seconds": timeout_seconds,
        "actual_duration_seconds": round(duration, 2),
        "success": success,
        "error_message": error_message,
        # Placeholder for more detailed metrics if a more sophisticated stress tool was used
        "load_average_at_end": None 
    }
    
    print(json.dumps(metrics))

if __name__ == "__main__":
    # Default values, can be made configurable via environment variables or arguments
    cpu_count = 1
    timeout_seconds = 60

    # Parse arguments if provided (e.g., from Kubernetes job args)
    if len(sys.argv) > 1:
        try:
            cpu_count = int(sys.argv[1])
            timeout_seconds = int(sys.argv[2])
        except (ValueError, IndexError):
            print("Usage: python stress_script.py [cpu_count] [timeout_seconds]", file=sys.stderr)
            sys.exit(1)

    run_stress_test(cpu_count, timeout_seconds)