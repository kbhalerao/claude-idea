#!/bin/bash
# Setup script for the /idea slash command

set -e

echo "==================================="
echo "Setting up /idea slash command"
echo "==================================="
echo ""

# Create global commands directory if it doesn't exist
CLAUDE_COMMANDS_DIR="$HOME/.claude/commands"
mkdir -p "$CLAUDE_COMMANDS_DIR"

# Copy the slash command
echo "Installing /idea slash command to $CLAUDE_COMMANDS_DIR..."
cp .claude/commands/idea.md "$CLAUDE_COMMANDS_DIR/idea.md"

echo ""
echo "✓ Slash command installed!"
echo ""
echo "The /idea command is now available system-wide in Claude Code."
echo ""
echo "Usage examples:"
echo "  /idea make sure we review the authentication module"
echo "  /idea show me all high priority tasks"
echo "  /idea what should I work on next?"
echo "  /idea give me all pinion project tasks"
echo ""
echo "⚠️  Note: You may need to restart Claude Code for the command to appear."
echo ""
