import unittest
from unittest.mock import patch, MagicMock
from modules.target_discovery import TargetDiscovery

class TestTargetDiscovery(unittest.TestCase):
    def setUp(self):
        self.td = TargetDiscovery()

    @patch('modules.target_discovery.TargetDiscovery.ping_network_gateway')
    def test_discover_internal_networks_all_active(self, mock_ping):
        """Test discover_internal_networks when all networks are active"""
        mock_ping.return_value = True
        expected = ["192.168.0.0/16", "10.0.0.0/8", "172.16.0.0/12"]
        result = self.td.discover_internal_networks()
        self.assertEqual(result, expected)
        self.assertEqual(mock_ping.call_count, 3)

    @patch('modules.target_discovery.TargetDiscovery.ping_network_gateway')
    def test_discover_internal_networks_none_active(self, mock_ping):
        """Test discover_internal_networks when no networks are active"""
        mock_ping.return_value = False
        result = self.td.discover_internal_networks()
        self.assertEqual(result, [])
        self.assertEqual(mock_ping.call_count, 3)

    @patch('modules.target_discovery.TargetDiscovery.ping_network_gateway')
    def test_discover_internal_networks_mixed(self, mock_ping):
        """Test discover_internal_networks with a mix of active/inactive networks"""
        mock_ping.side_effect = [True, False, True]
        expected = ["192.168.0.0/16", "172.16.0.0/12"]
        result = self.td.discover_internal_networks()
        self.assertEqual(result, expected)
        self.assertEqual(mock_ping.call_count, 3)

    @patch('modules.target_discovery.subprocess.run')
    def test_ping_network_gateway_success(self, mock_run):
        """Test successful ping of network gateway"""
        mock_run.return_value = MagicMock(returncode=0)
        result = self.td.ping_network_gateway("192.168.1.0/24")
        self.assertTrue(result)
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        self.assertIn("192.168.1.1", args[0])

    @patch('modules.target_discovery.subprocess.run')
    def test_ping_network_gateway_failure(self, mock_run):
        """Test unsuccessful ping of network gateway"""
        mock_run.return_value = MagicMock(returncode=1)
        result = self.td.ping_network_gateway("10.0.0.0/8")
        self.assertFalse(result)
        mock_run.assert_called_once()

    @patch('modules.target_discovery.subprocess.run')
    def test_ping_network_gateway_exception(self, mock_run):
        """Test ping when subprocess raises an exception"""
        mock_run.side_effect = Exception("Ping failed")
        result = self.td.ping_network_gateway("172.16.0.0/12")
        self.assertFalse(result)
        mock_run.assert_called_once()

    def test_ping_network_gateway_invalid_network(self):
        """Test ping with an invalid network string"""
        result = self.td.ping_network_gateway("invalid_network")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
