import json
import os
import matplotlib.pyplot as plt
import io
import base64

def generate_html_report(data, output_dir="test_report"):
    os.makedirs(output_dir, exist_ok=True)
    
    report_title = data.get("report_title", "Test Report")
    test_run_id = data.get("test_run_id", "N/A")
    timestamp = data.get("timestamp", "N/A")
    environment = data.get("environment", {})
    test_parameters = data.get("test_parameters", {})

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
                <h3>Environment</h3>
                <ul>
                    <li><strong>OS:</strong> {environment.get("os", "N/A")}</li>
                    <li><strong>CPU:</strong> {environment.get("cpu", "N/A")}</li>
                    <li><strong>Memory:</strong> {environment.get("memory", "N/A")}</li>
                </ul>
                <h3>Test Parameters</h3>
                <ul>
                    <li><strong>Virtual Users:</strong> {test_parameters.get("virtual_users", "N/A")}</li>
                    <li><strong>Duration (minutes):</strong> {test_parameters.get("duration_minutes", "N/A")}</li>
                    <li><strong>Ramp-up (seconds):</strong> {test_parameters.get("ramp_up_seconds", "N/A")}</li>
                </ul>
            </div>
    """

    # Generate summary charts
    all_test_cases = [case for suite in data.get("test_suites", []) for case in suite.get("test_cases", [])]
    passed_cases = [case for case in all_test_cases if case.get("status") == "passed"]
    failed_cases = [case for case in all_test_cases if case.get("status") == "failed"]

    html_content += f"""
        <div class="chart-container">
            <h2>Test Case Summary</h2>
            <canvas id="testCaseChart"></canvas>
        </div>
        <script>
            var ctx = document.getElementById('testCaseChart').getContext('2d');
            var testCaseChart = new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels: ['Passed', 'Failed'],
                    datasets: [{{
                        label: 'Test Cases',
                        data: [{len(passed_cases)}, {len(failed_cases)}],
                        backgroundColor: ['#28a745', '#dc3545']
                    }}]
                }},
                options: {{
                    responsive: true,
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        </script>
    """

    for suite in data.get("test_suites", []):
        suite_name = suite.get("name", "N/A")
        suite_status = suite.get("status", "N/A")
        suite_duration = suite.get("duration", 0)
        
        html_content += f"""
            <div class="test-suite">
                <h3>Test Suite: {suite_name} <span class="status-{suite_status}">{suite_status.upper()}</span> (Duration: {suite_duration:.2f}s)</h3>
                <div class="details">
        """
        for i, case in enumerate(suite.get("test_cases", [])):
            case_name = case.get("name", "N/A")
            case_status = case.get("status", "N/A")
            case_duration = case.get("duration", 0)
            error_message = case.get("error_message", "")
            metrics = case.get("metrics", {})

            html_content += f"""
                    <div class="test-case {case_status}">
                        <p><strong>Test Case:</strong> {case_name}</p>
                        <p><strong>Status:</strong> <span class="status-{case_status}">{case_status.upper()}</span></p>
                        <p><strong>Duration:</strong> {case_duration:.2f}s</p>
                        <div class="metrics">
                            <p><strong>Avg. Response Time:</strong> {metrics.get("response_time_avg", "N/A")}ms</p>
                            <p><strong>P95 Response Time:</strong> {metrics.get("response_time_p95", "N/A")}ms</p>
                            <p><strong>P99 Response Time:</strong> {metrics.get("response_time_p99", "N/A")}ms</p>
                            <p><strong>Throughput:</strong> {metrics.get("throughput", "N/A")} req/s</p>
                            <p><strong>Error Rate:</strong> {metrics.get("error_rate", "N/A") * 100:.2f}%</p>
                        </div>
            """
            if error_message:
                html_content += f"""
                        <pre class="error-message">Error: {error_message}</pre>
                """
            
            # Chart for each test case
            chart_id = f"chart_{suite_name.replace(' ', '_')}_{i}"
            html_content += f'<div class="chart-container"><canvas id="{chart_id}"></canvas></div>'
            
            html_content += f"""
                <script>
                    var ctx_{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                    new Chart(ctx_{chart_id}, {{
                        type: 'line',
                        data: {{
                            labels: ['Avg', 'P95', 'P99'],
                            datasets: [{{
                                label: 'Response Time (ms)',
                                data: [{metrics.get("response_time_avg", 0)}, {metrics.get("response_time_p95", 0)}, {metrics.get("response_time_p99", 0)}],
                                borderColor: '#007bff',
                                fill: false
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            scales: {{
                                y: {{
                                    beginAtZero: true
                                }}
                            }}
                        }}
                    }});
                </script>
            """
            
            html_content += "</div>"
        html_content += """
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """

    # Write HTML file
    report_path = os.path.join(output_dir, "index.html")
    with open(report_path, "w") as f:
        f.write(html_content)
    
    # Write CSS file
    css_content = """
    body { font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
    .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }
    h1, h2, h3 { color: #0056b3; }
    h2, h3 { border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .summary, .test-suite { margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }
    .summary p, .summary ul, .test-suite h3 { padding: 10px; margin: 0; }
    .summary p, .summary ul { background-color: #e9ecef; border-bottom: 1px solid #ddd; }
    .test-suite h3 { background-color: #d1ecf1; border-bottom: 1px solid #ddd; }
    .test-suite .details { padding: 10px; }
    .test-case { margin-bottom: 10px; padding: 8px; border-left: 5px solid; }
    .test-case.passed { border-color: #28a745; background-color: #e9f7ed; }
    .test-case.failed { border-color: #dc3545; background-color: #fbe9ea; }
    .test-case p { margin: 5px 0; }
    .status-passed { color: #28a745; font-weight: bold; }
    .status-failed { color: #dc3545; font-weight: bold; }
    .error-message { color: #dc3545; font-size: 0.9em; margin-top: 5px; white-space: pre-wrap; background-color: #fff; padding: 5px; border: 1px solid #f5c6cb; }
    .metrics { margin-top: 10px; padding-top: 10px; border-top: 1px solid #eee; }
    .chart-container { width: 80%; margin: 20px auto; }
    """
    css_path = os.path.join(output_dir, "style.css")
    with open(css_path, "w") as f:
        f.write(css_content)
        
    print(f"HTML report generated at: {report_path}")

if __name__ == "__main__":
    try:
        with open("test_results.json", "r") as f:
            test_data = json.load(f)
        generate_html_report(test_data)
    except FileNotFoundError:
        print("Error: test_results.json not found. Please create the file with test data.")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from test_results.json. Check file format.")
