# AI_HackerOS Usage Guide

## Installation

1. Install Python 3.8 or higher
2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the tool:
```bash
cp config/config.yaml.example config/config.yaml
# Edit config.yaml with your settings
```

## CLI Mode Usage

### Basic Commands

```bash
# Run basic scan
python main.py --target example.com

# Run in different modes
python main.py --target example.com --mode autonomous
python main.py --target example.com --mode manual
python main.py --target example.com --mode continuous

# Specify scan type
python main.py --target example.com --scan-type network
python main.py --target example.com --scan-type web
python main.py --target example.com --scan-type vulnerability
```

### Advanced Options

```bash
# Specify scan options
python main.py --target example.com --scan-options "{'ports': '80,443', 'rate': 'fast'}"

# Generate report
python main.py --target example.com --report-format pdf
python main.py --target example.com --report-format html
python main.py --target example.com --report-format json

# Save scan results
python main.py --target example.com --save-results
```

## Web Interface Usage

### Starting the Web Interface

1. Start the API server:
```bash
python api/server.py
```

2. Start the dashboard:
```bash
python dashboard/dashboard.py
```

3. Access the dashboard at:
```
http://localhost:8000
```

### Web Interface Features

1. **Dashboard Overview**
   - Real-time system metrics
   - Active scans
   - Recent vulnerabilities
   - Asset inventory

2. **Scan Management**
   - Start new scans
   - View scan history
   - Monitor scan progress
   - Export scan results

3. **Vulnerability Management**
   - View all vulnerabilities
   - Track vulnerability status
   - Generate mitigation plans
   - Export vulnerability reports

4. **Asset Management**
   - View all assets
   - Track asset status
   - Update asset information
   - Generate asset reports

### Authentication

1. Login to the web interface
2. Use your credentials from `auth/auth_data.json`
3. Default admin credentials:
   - Username: admin
   - Password: admin123

## Example Workflows

### Basic Scan Workflow

1. Start scan:
```bash
python main.py --target example.com --scan-type network
```

2. View results in dashboard:
   - Navigate to "Scan Results"
   - View detailed findings
   - Generate report

### Advanced Analysis Workflow

1. Start comprehensive scan:
```bash
python main.py --target example.com --scan-type vulnerability --scan-options "{'depth': 'deep', 'rate': 'normal'}"
```

2. Use AI analysis:
   - Navigate to "AI Analysis"
   - View vulnerability scores
   - Get automated recommendations

3. Generate detailed report:
```bash
python main.py --target example.com --report-format pdf --report-detail comprehensive
```

## Troubleshooting

1. **Common Issues**
   - Ensure all dependencies are installed
   - Check configuration file permissions
   - Verify API keys and credentials

2. **Error Handling**
   - Check logs in `logs/error.log`
   - Review system status in dashboard
   - Use debug mode for detailed output

## Security Best Practices

1. **Authentication**
   - Always use secure credentials
   - Change default passwords
   - Enable 2FA if available

2. **Data Protection**
   - Encrypt sensitive data
   - Regular backups
   - Secure database access

3. **System Security**
   - Regular updates
   - Firewall rules
   - Access controls
