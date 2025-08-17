
#!/bin/bash
# AI_HackerOS Installation Script

echo "🔧 Installing AI_HackerOS..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🛠️ Installing system tools..."
sudo apt install -y \
    python3 \
    python3-pip \
    nmap \
    sqlmap \
    nikto \
    whatweb \
    sublist3r \
    gobuster \
    dirb \
    wget \
    curl \
    git \
    chromium-browser \
    genisoimage

# Install Metasploit (if not already installed)
if ! command -v msfconsole &> /dev/null; then
    echo "🔥 Installing Metasploit Framework..."
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
    chmod 755 msfinstall
    ./msfinstall
    rm msfinstall
fi

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip3 install -r requirements.txt

# Setup directories
echo "📁 Creating directories..."
mkdir -p models reports logs templates

# Download sample AI model (optional)
echo "🤖 Setting up AI models..."
if [ ! -f "models/llama-model.gguf" ]; then
    echo "Note: Place your GGUF model file in the models/ directory"
    echo "You can download models from HuggingFace"
fi

# Make scripts executable
chmod +x scripts/*.sh

# Setup completed
echo "✅ AI_HackerOS installation completed!"
echo ""
echo "🚀 Quick start:"
echo "  python3 main.py --manual"
echo "  python3 main.py --target <target> --auto"
echo ""
echo "⚠️  Remember: Only use on authorized targets!"
