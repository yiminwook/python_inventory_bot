import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class TimeoutException(Exception):
    pass


class SeleniumRecoveryTests(unittest.TestCase):
    def setUp(self):
        names = [
            "selenium", "selenium.webdriver", "selenium.webdriver.chrome",
            "selenium.webdriver.chrome.service", "selenium.webdriver.chrome.options",
            "selenium.webdriver.common", "selenium.webdriver.common.by",
            "selenium.webdriver.support", "selenium.webdriver.support.ui",
            "selenium.webdriver.support.expected_conditions", "selenium.common",
            "selenium.common.exceptions", "src.config", "src.util",
        ]
        modules = {name: types.ModuleType(name) for name in names}
        modules["selenium"].webdriver = modules["selenium.webdriver"]
        self.browser = Mock()
        modules["selenium.webdriver"].Chrome = Mock(return_value=self.browser)
        modules["selenium.webdriver.chrome.service"].Service = Mock()
        modules["selenium.webdriver.chrome.options"].Options = Mock()
        modules["selenium.webdriver.common.by"].By = Mock()
        self.wait = Mock()
        modules["selenium.webdriver.support.ui"].WebDriverWait = self.wait
        conditions = modules["selenium.webdriver.support.expected_conditions"]
        conditions.presence_of_element_located = Mock()
        conditions.visibility_of_any_elements_located = Mock()
        modules["selenium.common.exceptions"].TimeoutException = TimeoutException
        modules["src.config"].ABSOLUTE_CHROME_DRIVER_PATH = "chromedriver"
        modules["src.config"].PURCHASE_PAGE_URL = "https://example.com"
        modules["src.util"].time_print = Mock()
        with patch.dict(sys.modules, modules):
            spec = importlib.util.spec_from_file_location(
                "inventory_selenium", Path(__file__).resolve().parents[1] / "src/selenium_util.py"
            )
            self.module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.module)

    def test_navigation_timeout_cleans_up_and_next_check_succeeds(self):
        self.browser.get.side_effect = [TimeoutException("renderer timeout"), None]
        self.assertIsNone(self.module.get_page_content())
        self.assertIsNone(self.module.driver)
        self.assertTrue(self.module.get_page_content())
        self.assertEqual(self.browser.quit.call_count, 2)
        self.browser.set_page_load_timeout.assert_called_with(45)

    def test_missing_button_returns_false(self):
        self.wait.return_value.until.side_effect = [Mock(), TimeoutException()]
        self.assertFalse(self.module.get_page_content())
        self.browser.quit.assert_called_once()

    def test_quit_failure_does_not_hide_failed_check(self):
        self.browser.get.side_effect = TimeoutException()
        self.browser.quit.side_effect = RuntimeError("disconnected")
        self.assertIsNone(self.module.get_page_content())
        self.assertIsNone(self.module.driver)

    def test_browser_start_failure_returns_unknown(self):
        self.module.webdriver.Chrome.side_effect = RuntimeError("start failure")
        self.assertIsNone(self.module.get_page_content())


if __name__ == "__main__":
    unittest.main()
