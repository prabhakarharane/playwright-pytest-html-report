import base64
from datetime import datetime
from pathlib import Path
import pytest

class PlaywrightReporter:
    def __init__(self, report_dir="reports"):
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(exist_ok=True)
        self.test_results = []
        self.start_time = datetime.now()

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()
        
        if report.when == "call" and report.failed:
            try:
                page = item.funcargs.get('page', None)
                if page:
                    screenshot = page.screenshot(type='png')
                    report.extra = [{'image': screenshot}]
            except Exception as e:
                print(f"Failed to capture screenshot: {e}")

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            file_path, test_name = report.nodeid.split("::", 1) if "::" in report.nodeid else (report.nodeid, "")
            
            # Get screenshot from extras if test failed
            screenshot = None
            if hasattr(report, 'extra'):
                for extra in report.extra:
                    if extra.get('image'):
                        try:
                            screenshot = base64.b64encode(extra['image']).decode('utf-8')
                        except Exception as e:
                            print(f"Failed to encode screenshot: {e}")

            test_result = {
                "file": file_path,
                "name": test_name,
                "status": report.outcome,
                "duration": report.duration * 1000,  # Convert to milliseconds
                "error": str(report.longrepr) if report.failed else None,
                "browser": "chromium",
                "screenshot": screenshot
            }
            self.test_results.append(test_result)

    def pytest_sessionfinish(self, session):
        duration = (datetime.now() - self.start_time).total_seconds()
        
        summary = {
            "total": len(self.test_results),
            "passed": len([r for r in self.test_results if r["status"] == "passed"]),
            "failed": len([r for r in self.test_results if r["status"] == "failed"]),
            "flaky": 0,
            "skipped": len([r for r in self.test_results if r["status"] == "skipped"]),
            "duration": duration
        }

        self.generate_html_report(summary)

    def generate_html_report(self, summary):
        html_content = f"""
<!DOCTYPE html>
<html data-theme="dark">
<head>
    <meta charset="utf-8">
    <title>Playwright Test Results</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/languages/python.min.js"></script>
    <style>
        :root {{
            --color-bg: #1c1c1c;
            --color-text: #f0f0f0;
            --color-text-secondary: #868686;
            --color-border: #3f3f3f;
            --color-passed: #2fb344;
            --color-failed: #f84747;
            --color-skipped: #2f90b3;
            --color-flaky: #d2c329;
            --color-selected-bg: #2f2f2f;
            --max-width: 980px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.4;
            color: var(--color-text);
            background: var(--color-bg);
        }}

        .container {{
            max-width: var(--max-width);
            margin: 0 auto;
        }}

        .header {{
            padding: 1rem 0;
            border-bottom: 1px solid var(--color-border);
        }}

        .title {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: var(--color-text);
        }}

        .controls {{
            display: flex;
            align-items: center;
            gap: 2rem;
        }}

        .search-bar {{
            flex: 1;
            background: #000;
            border: none;
            border: 1px solid var(--color-border);
            border-radius: 5px;
            color: var(--color-text);
            padding: 0.5rem;
            font-size: 1rem;
            min-width: 300px;
        }}

        .search-bar:focus {{
            outline: none;
            border-bottom-color: var(--color-text);
        }}

        .tabs {{
            display: flex;
            gap: 0.5rem;
        }}

        .tab {{
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--color-text-secondary);
        }}

        .tab.active {{
            background: var(--color-selected-bg);
            color: var(--color-text);
        }}

        .tab-count {{
            background: var(--color-selected-bg);
            padding: 0.1rem 0.4rem;
            border-radius: 10px;
            font-size: 0.8em;
        }}

        .file-item {{
            border: 1px solid var(--color-border);
            border-radius: 5px;
            margin-bottom: 10px;
        }}

        .file-header {{
            padding: 0.5rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            cursor: pointer;
        }}

        .file-header:hover {{
            background: var(--color-selected-bg);
        }}

        .file-name {{
            color: var(--color-text);
            font-weight: 500;
        }}

        .test-item {{
            padding: 1rem;
            border-bottom: 1px solid var(--color-border);
            cursor: pointer;
        }}

        .test-item:hover {{
            background: var(--color-selected-bg);
        }}

        .test-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .test-status {{
            width: 16px;
            height: 16px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .status-passed {{
            background: var(--color-passed);
        }}

        .status-failed {{
            background: var(--color-failed);
        }}

        .status-skipped {{
            background: var(--color-skipped);
        }}

        .status-flaky {{
            background: var(--color-flaky);
        }}

        .test-name {{
            flex-grow: 1;
        }}

        .test-duration {{
            color: var(--color-text-secondary);
            font-size: 0.9em;
        }}

        .test-browser {{
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
            background: var(--color-selected-bg);
            font-size: 0.8em;
            color: var(--color-text-secondary);
        }}

        .timestamp {{
            color: var(--color-text-secondary);
            font-size: 0.9em;
            text-align: right;
            padding: 0.5rem 1rem;
        }}

        .test-details {{
            display: none;
            padding: 1rem 2rem;
            background: var(--color-selected-bg);
            border-bottom: 1px solid var(--color-border);
        }}

        .test-details.expanded {{
            display: block;
        }}

        .test-error {{
            font-family: monospace;
            white-space: pre-wrap;
            margin-top: 1rem;
            padding: 1rem;
            background: var(--color-bg);
            border-radius: 4px;
            overflow-x: auto;
        }}

        .test-error pre {{
            margin: 0;
            padding: 1rem;
            background: #1e1e1e !important;
            border-radius: 4px;
        }}

        .test-error code {{
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
        }}

        .test-screenshot {{
            margin-top: 1rem;
            max-width: 100%;
            border-radius: 4px;
            border: 1px solid var(--color-border);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}

        .test-item.expanded {{
            background: var(--color-selected-bg);
        }}

        .error-line {{
            color: var(--color-failed);
            font-weight: bold;
        }}

        .error-message {{
            color: var(--color-text);
            margin-bottom: 1rem;
            padding: 1rem;
            background: rgba(248, 71, 71, 0.1);
            border-left: 4px solid var(--color-failed);
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}

        .error-trace {{
            margin-top: 1rem;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }}

        .error-trace pre {{
            margin: 0;
            padding: 1rem;
            background: #1e1e1e !important;
            border-radius: 4px;
            white-space: pre;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.5;
        }}

        .error-trace code {{
            font-family: inherit;
            padding: 0;
            background: none !important;
        }}

        .hljs {{
            background: #1e1e1e !important;
            color: #d4d4d4 !important;
        }}

        .error-trace .hljs {{
            background: none !important;
            padding: 0;
        }}

        .error-trace .line-number {{
            color: #858585;
            user-select: none;
        }}

        .error-trace .caret {{
            color: #dcdcaa;
        }}

        .error-trace .context-line {{
            padding-left: 2ch;
        }}

        .error-trace .def-line {{
            color: #4ec9b0;
        }}

        .error-trace .file-line {{
            color: #569cd6;
        }}

        .error-trace .context-line {{
            color: #ce9178;
        }}

        .error-message {{
            display: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="title">Playwright Test Results</h1>
            <div class="controls">
                <input type="text" class="search-bar" placeholder="Search" id="searchInput">
                <div class="tabs">
                    <div class="tab active" data-status="all">
                        All <span class="tab-count">{summary['total']}</span>
                    </div>
                    <div class="tab" data-status="passed">
                        Passed <span class="tab-count">{summary['passed']}</span>
                    </div>
                    <div class="tab" data-status="failed">
                        Failed <span class="tab-count">{summary['failed']}</span>
                    </div>
                    <div class="tab" data-status="flaky">
                        Flaky <span class="tab-count">{summary['flaky']}</span>
                    </div>
                    <div class="tab" data-status="skipped">
                        Skipped <span class="tab-count">{summary['skipped']}</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="timestamp">
            {datetime.now().strftime('%m/%d/%Y, %I:%M:%S %p')} · Total time: {summary['duration']:.1f}s
        </div>

        <div id="testResults">
            {self._generate_test_results()}
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Register a custom language for pytest traceback
            hljs.registerLanguage('pytb', function(hljs) {{
                return {{
                    name: 'Python Traceback',
                    contains: [
                        {{
                            className: 'error-line',
                            begin: '^E.*',
                            end: '$'
                        }},
                        {{
                            className: 'file-line',
                            begin: 'File "',
                            end: '$'
                        }},
                        {{
                            className: 'def-line',
                            begin: '(def |class |async def |@)',
                            end: '$'
                        }},
                        {{
                            className: 'context-line',
                            begin: '^>',
                            end: '$'
                        }}
                    ]
                }};
            }});

            const searchInput = document.getElementById('searchInput');
            const tabs = document.querySelectorAll('.tab');
            const testItems = document.querySelectorAll('.test-item');
            const fileItems = document.querySelectorAll('.file-item');

            // Initialize syntax highlighting
            document.querySelectorAll('pre code').forEach((block) => {{
                hljs.highlightElement(block);
            }});

            // Search functionality
            searchInput.addEventListener('input', function(e) {{
                const searchTerm = e.target.value.toLowerCase();
                fileItems.forEach(file => {{
                    const fileName = file.querySelector('.file-name').textContent.toLowerCase();
                    const tests = file.querySelectorAll('.test-item');
                    let hasVisibleTests = false;

                    tests.forEach(test => {{
                        const testName = test.querySelector('.test-name').textContent.toLowerCase();
                        const shouldShow = testName.includes(searchTerm) || fileName.includes(searchTerm);
                        test.style.display = shouldShow ? 'block' : 'none';
                        if (shouldShow) hasVisibleTests = true;
                    }});

                    file.style.display = hasVisibleTests ? 'block' : 'none';
                }});
            }});

            // Tab filtering
            tabs.forEach(tab => {{
                tab.addEventListener('click', function() {{
                    tabs.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');

                    const status = this.dataset.status;
                    fileItems.forEach(file => {{
                        const tests = file.querySelectorAll('.test-item');
                        let hasVisibleTests = false;

                        tests.forEach(test => {{
                            const testStatus = test.querySelector('.test-status').dataset.status;
                            const shouldShow = status === 'all' || testStatus === status;
                            test.style.display = shouldShow ? 'block' : 'none';
                            if (shouldShow) hasVisibleTests = true;
                        }});

                        file.style.display = hasVisibleTests ? 'block' : 'none';
                    }});
                }});
            }});

            // File item expansion
            fileItems.forEach(file => {{
                const header = file.querySelector('.file-header');
                const tests = file.querySelectorAll('.test-item');
                const details = file.querySelectorAll('.test-details');
                
                // Initially hide all tests
                tests.forEach(test => test.style.display = 'none');

                header.addEventListener('click', function() {{
                    const isExpanded = header.classList.contains('expanded');
                    tests.forEach(test => {{
                        test.style.display = isExpanded ? 'none' : 'block';
                        test.classList.remove('expanded');
                    }});
                    details.forEach(detail => {{
                        detail.classList.remove('expanded');
                    }});
                    header.classList.toggle('expanded');
                }});
            }});

            // Test item expansion
            testItems.forEach(test => {{
                test.addEventListener('click', function(e) {{
                    // Don't expand if clicking a link inside the test
                    if (e.target.tagName === 'A') return;
                    
                    const details = test.nextElementSibling;
                    if (details && details.classList.contains('test-details')) {{
                        details.classList.toggle('expanded');
                        test.classList.toggle('expanded');
                    }}
                }});
            }});
        }});
    </script>
</body>
</html>
        """

        report_file = self.report_dir / "report.html"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _generate_test_results(self):
        # Group tests by file
        tests_by_file = {}
        for test in self.test_results:
            file_path = test["file"]
            if file_path not in tests_by_file:
                tests_by_file[file_path] = []
            tests_by_file[file_path].append(test)

        # Generate HTML for each file and its tests
        html_parts = []
        for file_path, tests in tests_by_file.items():
            file_html = f"""
                <div class="file-item">
                    <div class="file-header">
                        <svg class="chevron" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                        <span class="file-name">{file_path}</span>
                    </div>
            """

            for test in tests:
                duration_text = f"{test['duration']:.0f}ms" if test['duration'] < 1000 else f"{test['duration']/1000:.1f}s"
                
                # Test item
                file_html += f"""
                    <div class="test-item">
                        <div class="test-header">
                            <div class="test-status status-{test['status']}" data-status="{test['status']}"></div>
                            <div class="test-name">{test['name']}</div>
                            <div class="test-browser">{test ['browser']}</div>
                            <div class="test-duration">{duration_text}</div>
                        </div>
                    </div>
                """

                # Test details (error and screenshot)
                if test['error'] or test['screenshot']:
                    file_html += f"""
                    <div class="test-details">
                """
                    if test['error']:
                        # Format error message with syntax highlighting
                        error_text = test['error']
                        # Replace any HTML special characters
                        error_text = error_text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        # Split into lines and format
                        error_lines = error_text.split('\\n')
                        formatted_lines = []
                        
                        for line in error_lines:
                            if line.strip().startswith('E '):  # Error lines
                                formatted_lines.append(f'<span class="error-line">{line}</span>')
                            elif line.strip().startswith(('def ', 'class ', '@', 'async def')):  # Function/class definitions
                                formatted_lines.append(f'<span class="def-line">{line}</span>')
                            elif ': ' in line and any(word in line for word in ['File "', 'line ']):  # File/line references
                                formatted_lines.append(f'<span class="file-line">{line}</span>')
                            elif line.strip().startswith('>'):  # Code context lines
                                formatted_lines.append(f'<span class="context-line">{line}</span>')
                            else:
                                formatted_lines.append(line)
                        
                        formatted_error = '\\n'.join(formatted_lines)
                        
                        file_html += f"""
                        <div class="error-trace">
                            <pre><code class="language-pytb">{formatted_error}</code></pre>
                        </div>
                """
                    if test['screenshot']:
                        file_html += f"""
                        <img class="test-screenshot" src="data:image/png;base64,{test['screenshot']}" alt="Test failure screenshot">
                """
                    file_html += "</div>"

            file_html += "</div>"
            html_parts.append(file_html)

        return "\n".join(html_parts) 