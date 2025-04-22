from reporterAssets.reporter import PlaywrightReporter
import pytest
from datetime import datetime

def pytest_configure(config):
    config._metadata = {
        "Project": "Playwright Python Tests",
        "Environment": "Test",
        "Platform": "Windows",
        "Tested By": "QA Team",
        "Report Generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    config.pluginmanager.register(PlaywrightReporter())

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin("html")
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, "extra", [])

    if report.when == "call":
        xfail = hasattr(report, "wasxfail")
        if (report.skipped and xfail) or (report.failed and not xfail):
            # Add screenshot if test failed
            page = item.funcargs.get("page")
            if page:
                screenshot = page.screenshot(type="png")
                extra.append(pytest_html.extras.image(screenshot, "Screenshot"))
            
            # Add test trace
            extra.append(pytest_html.extras.text(report.longrepr, "Test Trace"))

        report.extra = extra

