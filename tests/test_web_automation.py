import unittest
from unittest.mock import MagicMock, patch
from browser_bot.web_automation import WebAutomation
from selenium.webdriver.common.by import By

class TestWebAutomation(unittest.TestCase):
    @patch('browser_bot.web_automation.webdriver.Chrome')
    def setUp(self, mock_chrome):
        self.mock_chrome_class = mock_chrome
        self.mock_driver = MagicMock()
        self.mock_chrome_class.return_value = self.mock_driver
        self.web_auto = WebAutomation(headless=True)

    def test_sql_injection_vulnerability_found(self):
        """Test SQL injection when an error indicator is found in page source"""
        form_data = {
            "action": "/login",
            "method": "POST",
            "inputs": [
                {"name": "username", "type": "text"},
                {"name": "password", "type": "password"}
            ]
        }

        # Mock element interactions
        mock_input_element = MagicMock()
        mock_submit_btn = MagicMock()

        # We have 2 inputs, so find_element will be called for each input, then for the submit button.
        def side_effect_find_element(by, value):
            if by == By.NAME and value in ["username", "password"]:
                return mock_input_element
            if by == By.CSS_SELECTOR and "submit" in value:
                return mock_submit_btn
            return MagicMock()

        self.mock_driver.find_element.side_effect = side_effect_find_element

        # Set page source to include an error indicator ("mysql")
        self.mock_driver.page_source = "<html><body>Warning: mysql_fetch_array()</body></html>"

        vulns = self.web_auto.test_sql_injection(form_data)

        # 3 payloads * 1 form_action (we just report per payload)
        self.assertEqual(len(vulns), 3)
        for vuln in vulns:
            self.assertEqual(vuln["type"], "SQL Injection")
            self.assertEqual(vuln["form_action"], "/login")
            self.assertEqual(vuln["severity"], "High")
            self.assertIn(vuln["payload"], [
                "' OR '1'='1",
                "' UNION SELECT NULL--",
                "'; DROP TABLE users--"
            ])

        # Verify find_element was called correctly
        self.assertTrue(self.mock_driver.find_element.called)
        self.assertTrue(mock_input_element.clear.called)
        self.assertTrue(mock_input_element.send_keys.called)
        self.assertTrue(mock_submit_btn.click.called)

    def test_sql_injection_no_vulnerability(self):
        """Test SQL injection when no error indicator is found in page source"""
        form_data = {
            "action": "/search",
            "method": "GET",
            "inputs": [
                {"name": "q", "type": "text"}
            ]
        }

        mock_input_element = MagicMock()
        mock_submit_btn = MagicMock()

        def side_effect_find_element(by, value):
            if by == By.NAME and value == "q":
                return mock_input_element
            if by == By.CSS_SELECTOR and "submit" in value:
                return mock_submit_btn
            return MagicMock()

        self.mock_driver.find_element.side_effect = side_effect_find_element

        # Set page source with no error indicators
        self.mock_driver.page_source = "<html><body>Search Results</body></html>"

        vulns = self.web_auto.test_sql_injection(form_data)

        self.assertEqual(len(vulns), 0)

    def test_sql_injection_ignores_non_text_inputs(self):
        """Test SQL injection ignores hidden, radio, checkbox, etc inputs"""
        form_data = {
            "action": "/update",
            "method": "POST",
            "inputs": [
                {"name": "csrf_token", "type": "hidden"},
                {"name": "agree", "type": "checkbox"}
            ]
        }

        mock_submit_btn = MagicMock()

        def side_effect_find_element(by, value):
            if by == By.CSS_SELECTOR and "submit" in value:
                return mock_submit_btn
            return MagicMock()

        self.mock_driver.find_element.side_effect = side_effect_find_element

        # Make a mock tracker for find_element
        self.mock_driver.page_source = "<html><body>Success</body></html>"

        # Reset the mock to track calls explicitly
        self.mock_driver.find_element.reset_mock()

        vulns = self.web_auto.test_sql_injection(form_data)

        self.assertEqual(len(vulns), 0)

        # Verify that for each payload, find_element was ONLY called for the submit button
        # and NOT for 'csrf_token' or 'agree'
        for call in self.mock_driver.find_element.call_args_list:
            by, value = call[0]
            self.assertNotEqual(by, By.NAME)
            self.assertNotIn(value, ["csrf_token", "agree"])

    def test_sql_injection_handles_exception(self):
        """Test that exceptions during testing are caught and handled gracefully"""
        form_data = {
            "action": "/login",
            "method": "POST",
            "inputs": [
                {"name": "username", "type": "text"}
            ]
        }

        # Raise exception on find_element
        self.mock_driver.find_element.side_effect = Exception("Element not found")

        # Should not raise exception
        vulns = self.web_auto.test_sql_injection(form_data)

        self.assertEqual(len(vulns), 0)

if __name__ == '__main__':
    unittest.main()
