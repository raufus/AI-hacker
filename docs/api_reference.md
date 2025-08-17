# API Reference

## Core Components

### 1. Main Agent
```python
from agent.main_agent import AutonomousAgent

# Initialize agent
agent = AutonomousAgent(target="example.com")

# Run operations
agent.run_autonomous_operation()
agent.run_manual_mode()
```

### 2. Exploitation Module
```python
from modules.exploitation import ExploitationModule

# Initialize module
exploit = ExploitationModule()

# Search exploits
exploits = exploit.search_exploits("apache")

# Generate payload
payload = exploit.generate_payload(
    payload_type="windows/meterpreter/reverse_tcp",
    lhost="192.168.1.100",
    lport=4444
)
```

### 3. Scanning Modules
```python
from modules.scanning import NetworkScanner, WebScanner

# Network scanning
scanner = NetworkScanner()
results = scanner.scan_network("192.168.1.0/24")

# Web scanning
web_scanner = WebScanner()
web_results = web_scanner.scan_web_app("http://example.com")
```

### 4. Vulnerability Database
```python
from modules.vulnerability_database import VulnerabilityDatabase

# Initialize database
db = VulnerabilityDatabase()

# Search vulnerabilities
vulns = db.search_vulnerabilities("sql injection")

# Get specific vulnerability
details = db.get_vulnerability("web", "sql_injection")
```

### 5. Reporting
```python
from report.report_generator import SecurityReportGenerator

# Initialize report generator
generator = SecurityReportGenerator()

# Generate reports
markdown_report = generator.generate_markdown_report(data)
html_report = generator.generate_html_report(data)
json_report = generator.generate_json_report(data)
```

## Error Handling
```python
from utils.error_handler import ErrorHandler

try:
    # Some operation that might fail
    result = some_operation()
except Exception as e:
    handler = ErrorHandler()
    recovery = handler.handle_error(type(e), e, context={"operation": "scan"})
```

## Configuration
```yaml
# config.yaml
system:
  log_level: "INFO"
  max_concurrent_scans: 5
  resource_limits:
    memory: 8192  # MB
    cpu: 80       # %
    disk: 90      # %

network:
  timeout: 30    # seconds
  retries: 3
  scan_rate: "normal"

security:
  require_authorization: true
  max_scan_duration: 3600  # seconds
  log_all_actions: true
```

## Example Usage

### Basic Scan
```python
from main import main

# Run basic scan
main(target="example.com")
```

### Advanced Usage
```python
from agent.main_agent import AutonomousAgent
from modules.scanning import WebScanner
from report.report_generator import SecurityReportGenerator

# Initialize components
agent = AutonomousAgent(target="example.com")
scanner = WebScanner()
reporter = SecurityReportGenerator()

# Custom scan
results = scanner.scan_web_app("http://example.com")
report = reporter.generate_markdown_report(results)
```

## Best Practices

### 1. Authorization
- Always obtain proper authorization before testing
- Document all testing activities
- Keep detailed logs

### 2. Resource Management
- Monitor system resources
- Set appropriate limits
- Use proper error handling

### 3. Security
- Validate all inputs
- Use secure connections
- Follow ethical guidelines

### 4. Reporting
- Generate detailed reports
- Include recommendations
- Document findings

## Troubleshooting

### Common Issues
1. Connection Problems
   - Check network connectivity
   - Verify target availability
   - Review firewall rules

2. Resource Issues
   - Monitor system usage
   - Adjust scan parameters
   - Review error logs

3. Authorization Errors
   - Verify permissions
   - Check user rights
   - Review access controls

## API Endpoints

### 1. Scanning
```http
POST /api/v1/scan
Content-Type: application/json

{
    "target": "example.com",
    "type": "web",
    "options": {
        "depth": 3,
        "timeout": 30
    }
}
```

### 2. Reports
```http
GET /api/v1/reports/{report_id}
Accept: application/json
```

### 3. Vulnerabilities
```http
GET /api/v1/vulnerabilities
Parameters:
    - search: string
    - severity: string
    - type: string
```

## Response Formats

### JSON Response
```json
{
    "status": "success",
    "data": {
        "findings": [],
        "vulnerabilities": [],
        "recommendations": []
    },
    "timestamp": "2023-07-12T18:41:08+05:00"
}
```

### Error Response
```json
{
    "status": "error",
    "message": "Invalid target",
    "details": {
        "code": 400,
        "timestamp": "2023-07-12T18:41:08+05:00"
    }
}
```

## Security Considerations

### 1. Input Validation
- Always validate user input
- Use secure parsing
- Prevent injection attacks

### 2. Authentication
- Use secure authentication
- Implement proper authorization
- Follow least privilege principle

### 3. Logging
- Log all actions
- Secure log storage
- Implement log rotation

### 4. Error Handling
- Graceful error recovery
- Secure error messages
- Proper resource cleanup
