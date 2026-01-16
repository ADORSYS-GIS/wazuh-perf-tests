import json
import os
import sys
from pathlib import Path
import html
import shutil

def generate_html_report(data, output_dir="test_report"):
    """Generates an HTML report from test data and writes it to the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Copy the stylesheet to the output directory
    current_script_dir = Path(__file__).parent
    stylesheet_path = current_script_dir / "style.css"
    if stylesheet_path.exists():
        shutil.copy(stylesheet_path, output_dir)
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
                <h3>Environment</h3>
                <ul>
                    <li><strong>OS:</strong> {environment.get("os", "N/A")}</li>
                    <li><strong>CPU:</strong> {environment.get("cpu", "N/A")}</li>
                    <li><strong>Memory:</strong> {environment.get("memory", "N/A")}</li>
                </ul>
                <h3>Test Parameters</h3>
                <ul>
                    <li><strong>Duration (minutes):</strong> {test_parameters.get("duration_minutes", "N/A")}</li>
                </ul>
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
                type: 'bar',
                data: {{
                    labels: ['Passed', 'Failed'],
                    datasets: [{{
                        label: 'Test Cases',
                        data: [{passed_count}, {failed_count}],
                        backgroundColor: ['#28a745', '#dc3545']
                    }}]
                }},
                options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
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
            error_message = html.escape(case.get("error_message", ""))
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

    report_path = os.path.join(output_dir, "index.html")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML report generated at: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_report.py <path_to_test_results.json>")
        sys.exit(1)

    results_file = sys.argv[1]

    try:
        with open(results_file, "r") as f:
            test_data = json.load(f)

        current_script_dir = Path(__file__).parent
        output_dir = current_script_dir.parent / "output" / "test_report"
        
        generate_html_report(test_data, output_dir=output_dir)

    except FileNotFoundError:
        print(f"Error: {results_file} not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {results_file}. Check file format.")
