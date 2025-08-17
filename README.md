
# AI Hacker OS

A fully autonomous, AI-powered penetration testing operating system designed to automate the entire hacking lifecycle. This system uses a local GGUF language model to make intelligent decisions, manage its own tools, and perform reconnaissance, scanning, exploitation, and reporting without human intervention.

## Vision

The goal of AI Hacker OS is to create a true "AI Red Teamer" in a box. It is built for cybersecurity professionals, researchers, and educators to simulate and execute complex penetration tests with maximum automation. By leveraging a local large language model, it can think, adapt, and act like a human hacker, but at machine speed and scale.

---

## ⚠️ DISCLAIMER

This tool is designed for **EDUCATIONAL PURPOSES ONLY** and authorized penetration testing. Only use this tool on systems you own or have explicit written permission to test. Unauthorized testing of computer systems is illegal and unethical. The developers assume no liability for misuse of this software.

---

## Core Features

-   **Autonomous Hacking Lifecycle**: The AI agent can independently execute all stages of a penetration test, from initial reconnaissance to final reporting.
-   **AI-Powered Decision Making**: Utilizes a local GGUF language model (`nous-hermes-2-solar-10.7b`) to analyze findings, suggest exploits, and generate custom payloads.
-   **Automatic Tool Management**: Automatically checks for required tools like Nmap, SQLMap, and Metasploit and guides the user on installation.
-   **Integrated Web Scanning**: Seamlessly launches and integrates with **Burp Suite** for passive scanning of all web traffic generated during automated browsing.
-   **Metasploit Integration**: Connects to the Metasploit RPC service (`msfrpcd`) to automate the exploitation phase.
-   **Multiple Operational Modes**:
    -   **Autonomous Mode**: Attack a specific, user-defined target.
    -   **Continuous Mode**: Automatically discover and attack new targets in a perpetual loop.
    -   **Manual Mode**: Provides an interactive shell for manual control.
-   **Comprehensive Reporting**: Generates detailed security reports at the end of each engagement.

---

## Application Architecture

The system is built on a modular architecture, separating the AI brain from the operational modules.

```
d:\AI penetration testing OS\
├── agent/
│   └── main_agent.py           # Core orchestrator that runs the hacking lifecycle.
│
├── ai_brain/
│   └── llm.py                  # Loads and interacts with the GGUF model for decision-making.
│
├── config/
│   ├── config_manager.py       # Manages loading and creating config.yaml.
│   └── config.yaml             # All settings (API keys, paths, targets).
│
├── logs/
│   └── app.log                 # All actions, errors, and results are logged here.
│
├── modules/
│   ├── reconnaissance.py       # Handles Nmap scans and information gathering.
│   ├── scanning.py             # Scans for vulnerabilities (SQLMap, etc.).
│   ├── exploitation.py         # Attempts to exploit found vulnerabilities (Metasploit).
│   ├── target_discovery.py     # Finds potential targets on the network.
│   ├── burp_launcher.py        # Starts and stops Burp Suite.
│   └── installer.py            # Checks for required tools.
│
├── report/
│   └── reporter.py             # Generates the final security reports.
│
├── tools/
│   └── Dr-FarFar.jar           # Folder for external tools like Burp Suite.
│
├── utils/
│   └── logger.py               # Sets up the application's logging system.
│
├── main.py                     # The main entry point to start the application.
└── requirements.txt            # List of all required Python packages.
```

---

## How the AI Thinks

The intelligence of this OS comes from the interaction between the modules and the AI Brain (`llm.py`). Here’s a typical thought process:

1.  **Observe**: The `reconnaissance` and `scanning` modules gather raw data. For example, an Nmap scan reveals an open port 80 with a specific web server version.
2.  **Orient**: The `main_agent` takes this data and formats it into a prompt for the AI. For example: *"I found an Apache 2.4.49 server on port 80. What are the likely vulnerabilities I should scan for?"*
3.  **Decide**: The GGUF model processes the prompt and provides a strategic recommendation, such as: *"Focus on directory traversal and check for known exploits related to this Apache version. Use SQLMap on any login forms found."*
4.  **Act**: The `main_agent` parses this recommendation and executes the appropriate module (`scanning.py` with SQLMap) to act on the AI's advice.
5.  **Generate Payload**: If a vulnerability is confirmed (e.g., SQL injection), the agent asks the AI for a specific payload to exploit it, which is then used by the `exploitation.py` module.

This Observe-Orient-Decide-Act (OODA) loop allows the system to behave dynamically and intelligently.

---

## Setup and Installation

Follow these steps to get the AI Hacker OS running.

### 1. Clone the repository:

```bash
git clone https://github.com/your-username/AI_HackerOS.git
cd AI_HackerOS
```

### 2. Install Dependencies:

To install the required system tools, you must run the application from a terminal with administrative (or root) privileges.

-   **On Windows:** Open PowerShell or Command Prompt as an Administrator.
-   **On Linux/macOS:** Use `sudo`.

Run the following command to install all tools:

```bash
python main.py --install-tools
```

### 3. Install Python Dependencies

Install all required Python packages using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up External Tools

-   **Metasploit Framework**: Must be installed on your system. The AI connects to its RPC service. [Download from Rapid7](https://www.rapid7.com/products/metasploit/download/).
-   **Burp Suite**: Place your Burp Suite JAR file (e.g., `Dr-FarFar.jar`) inside the `tools/` directory. The system will automatically detect and launch it.
-   **Other Tools**: Ensure standard command-line tools like `nmap` and `sqlmap` are installed and accessible in your system's PATH.

### 3. Configure the Application

The first time you run the application, it will generate a `config.yaml` file. You must edit this file to set:
-   The correct path to your GGUF model file.
-   Metasploit RPC credentials (`msf_user`, `msf_password`).
-   Any other required API keys or settings.

### 4. Start the Metasploit RPC Service

Before running the main application, you must start the Metasploit RPC server. Open the Metasploit console (`msfconsole`) and run:

```
msfrpcd -a 127.0.0.1 -p 55553 -U <your_user> -P <your_password>
```

Make sure the user and password match what you set in `config.yaml`.

---

## How to Use

Use the following commands to run the AI Hacker OS in its different modes.

### Continuous Mode (Fully Autonomous)

The AI discovers its own targets and attacks them in an endless loop. This is the most powerful, hands-off mode.

```bash
python main.py --continuous
```

### Autonomous Mode (Targeted Attack)

The AI performs a full penetration test on a single, specified target.

```bash
python main.py --target example.com --auto
```

### Manual Mode

Starts an interactive prompt for manual control over the tools and modules.

```bash
python main.py --manual
```

### Other Options

-   `--skip-checks`: Skips the initial check for required tools.
-   `--help`: Shows all available command-line options.
