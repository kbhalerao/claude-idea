#!/bin/bash
# Installation script for Idea Capture

set -e

echo "==================================="
echo "Idea Capture Installation"
echo "==================================="
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Found Python $PYTHON_VERSION"
echo ""

# Detect and use uv if available
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version | head -n1)
    echo "Found $UV_VERSION"
    echo ""

    # Ask user for installation type
    echo "Choose installation method:"
    echo "  1) Systemwide (recommended) - 'idea' command available everywhere"
    echo "  2) Development mode - editable install in current directory"
    echo ""
    read -p "Enter choice (1 or 2): " -n 1 -r
    echo ""
    echo ""

    if [[ $REPLY == "1" ]]; then
        echo "Installing systemwide with uv tool..."
        uv tool install .
    else
        echo "Installing in development mode with uv..."
        uv pip install -e .
    fi
else
    echo "uv not found, using pip..."
    echo ""

    # Ask user for installation type
    echo "Choose installation method:"
    echo "  1) Systemwide (recommended) - 'idea' command available everywhere"
    echo "  2) Development mode - editable install in current directory"
    echo ""
    read -p "Enter choice (1 or 2): " -n 1 -r
    echo ""
    echo ""

    if [[ $REPLY == "1" ]]; then
        echo "Installing systemwide with pip..."
        pip install .
    else
        echo "Installing in development mode with pip..."
        pip install -e .
    fi
fi
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your CouchDB credentials"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env with your CouchDB details:"
    echo "   nano .env"
    echo ""
    echo "2. Run the setup command:"
    echo "   idea setup"
    echo ""
    echo "3. Test the connection:"
    echo "   python test_connection.py"
    echo ""
else
    echo ".env file already exists"
    echo ""
    echo "Testing connection..."
    python test_connection.py
fi

echo ""
echo "Installation complete!"
echo ""

# Ask about slash command installation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Optional: Install /idea slash command?"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "The /idea slash command lets you use natural language in Claude Code:"
echo "  /idea make sure we review the auth module"
echo "  /idea show me high priority tasks"
echo ""
read -p "Install /idea slash command? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./setup_slash_command.sh
fi
echo ""

echo "Quick commands:"
echo "  idea add 'Your idea'    - Add a new idea"
echo "  idea list               - List all ideas"
echo "  idea next               - Get next actions"
echo "  idea setup              - Initialize database"
echo ""
echo "For more help, see README.md or QUICKSTART.md"
