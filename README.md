# Playwright Testing Framework

A modern testing framework using Playwright and pytest for web application testing with a custom HTML report generator. That will generate the html report similar to the Playwright nodejs framework.

## Features

- **Custom HTML Report**: Beautiful, interactive HTML report with:
  - Dark theme
  - Search functionality
  - Status filtering (All, Passed, Failed, Skipped)
  - Expandable test details
  - Screenshots for failed tests
  - Syntax-highlighted error traces
- **Test Data Management**: Separate configuration for test data
- **Video Recording**: Automatic video recording of test runs
- **Screenshot Capture**: Automatic screenshots for failed tests

## Project Structure

```
.
├── playwright_html_reporter/
│   └── reporter.py          # Custom HTML report generator
├── tests/
│   ├── test_example.py        # Example test cases
│   └── conftest.py          # Test configuration
├── reports/                 # Generated reports
├── pytest.ini              # Pytest configuration
└── requirements.txt        # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

## Configuration

### pytest.ini
```ini
[pytest]
addopts = --html=reports/report.html --self-contained-html
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

[metadata]
name = Playwright Test Suite
version = 1.0.0
description = Automated tests for web application

[playwright]
browser = chromium
headless = true
```

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_example.py
```

Run tests with specific browser:
```bash
pytest --browser chromium
```

## Report Generation

The framework automatically generates an HTML report in the `reports` directory after test execution. The report includes:

- Test summary statistics
- Search functionality
- Status filtering
- Expandable test details
- Screenshots for failed tests
- Error traces with syntax highlighting

## Best Practices

1. **Use Page Object Model**:
   - Keep page-specific selectors in page classes
   - Implement reusable methods for page interactions
   - Separate page logic from test logic

2. **Test Data Management**:
   - Store test data in separate configuration files
   - Use fixtures for test data
   - Keep sensitive data in environment variables

3. **Test Organization**:
   - Group related tests in separate files
   - Use descriptive test names
   - Add docstrings to explain test purpose

4. **Error Handling**:
   - Use explicit waits instead of hard-coded sleeps
   - Implement proper error assertions
   - Add meaningful error messages

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 