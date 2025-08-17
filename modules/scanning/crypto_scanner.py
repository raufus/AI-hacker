import ssl
import socket
from .scanning_module import ScanningModule
import logging

class CryptoScanner(ScanningModule):
    """Scanner for cryptographic weaknesses, like weak SSL/TLS protocols."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @property
    def name(self) -> str:
        return "Crypto Scanner"

    def scan(self, target: str, options: dict = None):
        """Checks for weak SSL/TLS protocols on a given port."""
        if options is None:
            options = {}
        port = options.get('port', 443)

        self.logger.info(f"Starting crypto scan on {target}:{port}")
        weak_protocols = []

        protocols = {
            'SSLv2': ssl.PROTOCOL_SSLv2,
            'SSLv3': ssl.PROTOCOL_SSLv3,
            'TLSv1': ssl.PROTOCOL_TLSv1,
            'TLSv1.1': ssl.PROTOCOL_TLSv1_1
        }

        for proto_name, proto_const in protocols.items():
            try:
                context = ssl.SSLContext(proto_const)
                with socket.create_connection((target, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=target) as ssock:
                        weak_protocols.append({
                            'protocol': proto_name,
                            'status': 'Supported',
                            'description': f'Weak protocol {proto_name} is supported on {target}:{port}'
                        })
                        self.logger.warning(f"Weak protocol {proto_name} supported on {target}:{port}")
            except (ssl.SSLError, socket.timeout, ConnectionRefusedError):
                # This is expected if the protocol is not supported
                pass
            except Exception as e:
                self.logger.error(f"Error checking {proto_name} on {target}:{port}: {e}")

        return {'weak_protocols': weak_protocols}
