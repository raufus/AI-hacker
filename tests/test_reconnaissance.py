import unittest
from unittest.mock import patch, MagicMock
import subprocess
from modules.reconnaissance import ReconModule

class TestReconModuleErrorHandling(unittest.TestCase):
    def setUp(self):
        self.recon = ReconModule()
        self.target = "127.0.0.1"

    @patch('modules.reconnaissance.subprocess.run')
    @patch('modules.reconnaissance.ReconModule._is_nmap_installed')
    def test_nmap_scan_called_process_error(self, mock_is_nmap_installed, mock_run):
        # Mock _is_nmap_installed to return True so we reach subprocess.run
        mock_is_nmap_installed.return_value = True

        # Create a CalledProcessError
        error = subprocess.CalledProcessError(returncode=1, cmd='nmap')
        error.stderr = "nmap command failed"
        mock_run.side_effect = error

        result = self.recon.nmap_scan(self.target)

        self.assertIn("error", result)
        self.assertTrue(result["error"].startswith("Command 'nmap' returned non-zero exit status 1."))
        self.assertEqual(result["target"], self.target)
        self.assertEqual(result["ports"], [])

    @patch('modules.reconnaissance.subprocess.run')
    @patch('modules.reconnaissance.ReconModule._is_nmap_installed')
    def test_nmap_scan_file_not_found_error(self, mock_is_nmap_installed, mock_run):
        # Mock _is_nmap_installed to return True so we reach subprocess.run
        mock_is_nmap_installed.return_value = True

        mock_run.side_effect = FileNotFoundError("nmap executable not found")

        result = self.recon.nmap_scan(self.target)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "nmap executable not found")
        self.assertEqual(result["target"], self.target)
        self.assertEqual(result["ports"], [])

    @patch('modules.reconnaissance.subprocess.run')
    @patch('modules.reconnaissance.ReconModule._is_nmap_installed')
    def test_nmap_scan_generic_exception(self, mock_is_nmap_installed, mock_run):
        # Mock _is_nmap_installed to return True so we reach subprocess.run
        mock_is_nmap_installed.return_value = True

        mock_run.side_effect = Exception("Unexpected failure")

        result = self.recon.nmap_scan(self.target)

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to parse Nmap output.")
        self.assertEqual(result["target"], self.target)
        self.assertEqual(result["ports"], [])

if __name__ == '__main__':
    unittest.main()
