import json
import os
import sys
from pathlib import Path
import html
import shutil
import pandas as pd
import matplotlib.pyplot as plt

def generate_graphs(run_dir):
    """Generates PNG charts from metrics CSV files in the run directory."""
    metrics_dir = Path(run_dir) / "stress_metrics"
    if not metrics_dir.exists():
        print(f"No metrics directory found in {run_dir}")
        return []

    csv_files = list(metrics_dir.glob("*_metrics.csv"))
    if not csv_files:
        print(f"No CSV files found in {metrics_dir}")
        return []

    generated_images = []

    for csv_file in csv_files:
        pod_name = csv_file.stem.replace("_metrics", "")
        df = pd.read_csv(csv_file)
        if df.empty:
            continue
        
        # Convert timestamp to relative time or datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
            df = df.sort_values('timestamp')
            df['relative_time'] = (df['timestamp'] - df['timestamp'].iloc[0]).dt.total_seconds()
        else:
            df['relative_time'] = range(len(df))

        # Plot 1: Resource Usage (CPU and Memory)
        fig, ax1 = plt.subplots(figsize=(10, 6))
        ax1.set_xlabel('Time (s)')
        
        cpu_col = 'cpu_percent' if 'cpu_percent' in df.columns else ('cpu' if 'cpu' in df.columns else None)
        mem_col = 'memory_percent' if 'memory_percent' in df.columns else ('memory' if 'memory' in df.columns else None)

        if cpu_col:
            ax1.set_ylabel('CPU (%)', color='tab:red')
            ax1.plot(df['relative_time'], df[cpu_col], color='tab:red', label='CPU (%)')
            ax1.tick_params(axis='y', labelcolor='tab:red')
            ax1.set_ylim(0, 100)

        if mem_col:
            ax2 = ax1.twinx()
            ax2.set_ylabel('Memory (%)', color='tab:blue')
            ax2.plot(df['relative_time'], df[mem_col], color='tab:blue', label='Memory (%)')
            ax2.tick_params(axis='y', labelcolor='tab:blue')
            ax2.set_ylim(0, 100)

        plt.title(f'Resource Usage - {pod_name}')
        fig.tight_layout()
        
        cpu_mem_img = f"resource_usage_{pod_name}.png"
        plt.savefig(Path(run_dir) / cpu_mem_img)
        plt.close()
        generated_images.append(cpu_mem_img)

        # Plot 2: I/O Throughput
        read_col = 'disk_read_bytes' if 'disk_read_bytes' in df.columns else ('disk_read' if 'disk_read' in df.columns else None)
        write_col = 'disk_write_bytes' if 'disk_write_bytes' in df.columns else ('disk_write' if 'disk_write' in df.columns else None)

        if read_col or write_col:
            plt.figure(figsize=(10, 6))
            if read_col:
                # Convert bytes to MB/s if it looks like bytes
                data = df[read_col]
                label = 'Disk Read (MB/s)'
                if 'bytes' in read_col:
                    data = data / (1024 * 1024)
                plt.plot(df['relative_time'], data, label=label)
            if write_col:
                data = df[write_col]
                label = 'Disk Write (MB/s)'
                if 'bytes' in write_col:
                    data = data / (1024 * 1024)
                plt.plot(df['relative_time'], data, label=label)
            
            plt.xlabel('Time (s)')
            plt.ylabel('Throughput (MB/s)')
            plt.title(f'I/O Throughput - {pod_name}')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()

            io_img = f"io_throughput_{pod_name}.png"
            plt.savefig(Path(run_dir) / io_img)
            plt.close()
            generated_images.append(io_img)

    return generated_images

def generate_html_report(data, run_dir, images, logs):
    """Generates an HTML report from test data and writes it to the run directory."""
    run_path = Path(run_dir)
    
    # Copy the stylesheet to the run directory
    current_script_dir = Path(__file__).parent
    stylesheet_path = current_script_dir / "style.css"
    if stylesheet_path.exists():
        shutil.copy(stylesheet_path, run_path / "style.css")
    else:
        print("Warning: style.css not found. Report will be unstyled.")

    # --- Sanitize data for HTML injection ---
    report_title = html.escape(data.get("report_title", "Test Report"))
    test_run_id = html.escape(data.get("test_run_id", "N/A"))
    timestamp = html.escape(data.get("timestamp", "N/A"))
    
    environment = {k: html.escape(str(v)) for k, v in data.get("environment", {}).items()}
    test_parameters = {k: html.escape(str(v)) for k, v in data.get("test_parameters", {}).items()}

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_title}</title>
        <link rel="stylesheet" href="style.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>{report_title}</h1>
            <div class="summary">
                <p><strong>Test Run ID:</strong> {test_run_id}</p>
                <p><strong>Generated On:</strong> {timestamp}</p>
                <div class="flex-container">
                    <div class="flex-item">
                        <h3>Environment</h3>
                        <ul>
                            <li><strong>OS:</strong> {environment.get("os", "N/A")}</li>
                            <li><strong>CPU:</strong> {environment.get("cpu", "N/A")}</li>
                            <li><strong>Memory:</strong> {environment.get("memory", "N/A")}</li>
                        </ul>
                    </div>
                    <div class="flex-item">
                        <h3>Test Parameters</h3>
                        <ul>
                            <li><strong>Duration (minutes):</strong> {test_parameters.get("duration_minutes", "N/A")}</li>
                        </ul>
                    </div>
                </div>
            </div>
    """

    # Cluster Health / Logs Section
    if logs:
        html_content += """
            <div class="section">
                <h2>Cluster Logs</h2>
                <ul>
        """
        for log in logs:
            log_name = Path(log).name
            # Relative path to logs inside the run dir
            rel_log_path = f"wazuh/{log_name}"
            html_content += f'<li><a href="{rel_log_path}" target="_blank">{log_name}</a></li>'
        html_content += """
                </ul>
            </div>
        """

    # Performance Graphs Section
    if images:
        html_content += """
            <div class="section">
                <h2>Resource Utilization (Stress Nodes)</h2>
                <div class="graph-grid">
        """
        for img in images:
            html_content += f"""
                    <div class="graph-item">
                        <img src="{img}" alt="{img}">
                    </div>
            """
        html_content += """
                </div>
            </div>
        """

    all_test_cases = [case for suite in data.get("test_suites", []) for case in suite.get("test_cases", [])]
    passed_count = len([case for case in all_test_cases if case.get("status") == "passed"])
    failed_count = len(all_test_cases) - passed_count

    html_content += f"""
        <div class="chart-container">
            <h2>Test Case Summary</h2>
            <canvas id="testCaseChart"></canvas>
        </div>
        <script>
            var ctx = document.getElementById('testCaseChart').getContext('2d');
            new Chart(ctx, {{
                type: 'pie',
                data: {{
                    labels: ['Passed', 'Failed'],
                    datasets: [{{
                        label: 'Test Cases',
                        data: [{passed_count}, {failed_count}],
                        backgroundColor: ['#28a745', '#dc3545']
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'top',
                        }},
                        title: {{
                            display: false
                        }}
                    }}
                }}
            }});
        </script>
    """

    for suite in data.get("test_suites", []):
        suite_name = html.escape(suite.get("name", "N/A"))
        suite_status = html.escape(suite.get("status", "N/A"))
        suite_duration = suite.get("duration", 0)

        html_content += f"""
            <div class="test-suite">
                <h3>Test Suite: {suite_name} <span class="status-{suite_status}">{suite_status.upper()}</span> (Duration: {suite_duration:.2f}s)</h3>
                <div class="details">
        """
        for case in suite.get("test_cases", []):
            case_name = html.escape(case.get("name", "N/A"))
            case_status = html.escape(case.get("status", "N/A"))
            case_duration = case.get("duration", 0)
            error_message = html.escape(case.get("error_message") or "")
            metrics = {k: html.escape(str(v)) for k, v in case.get("metrics", {}).items()}

            html_content += f"""
                    <div class="test-case {case_status}">
                        <p><strong>Test Case:</strong> {case_name}</p>
                        <p><strong>Status:</strong> <span class="status-{case_status}">{case_status.upper()}</span></p>
                        <p><strong>Duration:</strong> {case_duration:.2f}s</p>
                        <div class="metrics">
            """
            for key, value in metrics.items():
                html_content += f"            <p><strong>{html.escape(key.replace('_', ' ').title())}:</strong> {value}</p>\n"
            html_content += """
                        </div>
            """
            if error_message:
                html_content += f"""
                        <pre class="error-message">Error: {error_message}</pre>
                """
            html_content += "</div>"
        html_content += "</div></div>"

    html_content += "</div></body></html>"

    report_path = run_path / "report.html"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated at: {report_path}")

def get_latest_run_dir(base_output_dir):
    """Finds the latest timestamped directory in the output folder."""
    output_path = Path(base_output_dir)
    if not output_path.exists():
        return None
    
    run_dirs = [d for d in output_path.iterdir() if d.is_dir() and d.name != "test_report"]
    if not run_dirs:
        return None
    
    return max(run_dirs, key=lambda d: d.name)

if __name__ == "__main__":
    run_dir = None
    if len(sys.argv) > 1:
        run_dir = Path(sys.argv[1])
    else:
        # Try to find the latest run in output/
        project_root = Path(__file__).parent.parent
        run_dir = get_latest_run_dir(project_root / "output")

    if not run_dir or not run_dir.exists():
        print("Error: Could not find a valid run directory.")
        print("Usage: python generate_report.py [path_to_run_directory]")
        sys.exit(1)

    results_file = run_dir / "test_results.json"
    if not results_file.exists():
        print(f"Error: {results_file} not found in {run_dir}")
        sys.exit(1)

    try:
        with open(results_file, "r") as f:
            test_data = json.load(f)

        # Generate graphs
        images = generate_graphs(run_dir)
        
        # Collect logs
        log_files = list((run_dir / "wazuh").glob("*.log"))
        
        # Generate HTML report inside the run directory
        generate_html_report(test_data, run_dir, images, log_files)

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
