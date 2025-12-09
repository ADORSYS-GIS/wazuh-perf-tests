import json
import os
import matplotlib.pyplot as plt
import io
import base64

def generate_html_report(data, output_dir="test_report"):
    os.makedirs(output_dir, exist_ok=True)
    report_title = data.get("report_title", "Test Report")
    timestamp = data.get("timestamp", "N/A")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{report_title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
            .container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
            h1 {{ color: #0056b3; }}
            h2 {{ color: #0056b3; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
            .summary, .test-suite {{ margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9; }}
            .summary p, .test-suite h3 {{ padding: 10px; margin: 0; }}
            .summary p {{ background-color: #e9ecef; border-bottom: 1px solid #ddd; }}
            .test-suite h3 {{ background-color: #d1ecf1; border-bottom: 1px solid #ddd; }}
            .test-suite .details {{ padding: 10px; }}
            .test-case {{ margin-bottom: 10px; padding: 8px; border-left: 5px solid; }}
            .test-case.passed {{ border-color: #28a745; background-color: #e9f7ed; }}
            .test-case.failed {{ border-color: #dc3545; background-color: #fbe9ea; }}
            .test-case p {{ margin: 0; }}
            .status-passed {{ color: #28a745; font-weight: bold; }}
            .status-failed {{ color: #dc3545; font-weight: bold; }}
            .error-message {{ color: #dc3545; font-size: 0.9em; margin-top: 5px; white-space: pre-wrap; }}
            .chart-container {{ width: 60%; margin: 20px auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{report_title}</h1>
            <div class="summary">
                <p><strong>Generated On:</strong> {timestamp}</p>
                <p><strong>Total Test Suites:</strong> {len(data.get("test_suites", []))}</p>
            </div>
    """

    # Generate pie chart for test suite status
    suite_statuses = [suite.get("status", "unknown") for suite in data.get("test_suites", [])]
    passed_suites = suite_statuses.count("passed")
    failed_suites = suite_statuses.count("failed")
    
    labels = []
    sizes = []
    colors = []
    
    if passed_suites > 0:
        labels.append("Passed")
        sizes.append(passed_suites)
        colors.append("#28a745")
    if failed_suites > 0:
        labels.append("Failed")
        sizes.append(failed_suites)
        colors.append("#dc3545")
    
    if sizes:
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig1)
        
        chart_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        
        html_content += f"""
            <div class="chart-container">
                <h2>Test Suite Summary</h2>
                <img src="data:image/png;base64,{chart_base64}" alt="Test Suite Status Pie Chart">
            </div>
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
        for case in suite.get("test_cases", []):
            case_name = case.get("name", "N/A")
            case_status = case.get("status", "N/A")
            case_duration = case.get("duration", 0)
            error_message = case.get("error_message", "")

            html_content += f"""
                    <div class="test-case {case_status}">
                        <p><strong>Test Case:</strong> {case_name}</p>
                        <p><strong>Status:</strong> <span class="status-{case_status}">{case_status.upper()}</span></p>
                        <p><strong>Duration:</strong> {case_duration:.2f}s</p>
            """
            if error_message:
                html_content += f"""
                        <pre class="error-message">Error: {error_message}</pre>
                """
            html_content += f"""
                    </div>
            """
        html_content += f"""
                </div>
            </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """

    report_path = os.path.join(output_dir, "index.html")
    with open(report_path, "w") as f:
        f.write(html_content)
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
