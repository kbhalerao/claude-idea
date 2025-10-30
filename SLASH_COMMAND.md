# /idea Slash Command Guide

The `/idea` slash command provides a natural language interface to your journal/idea capture system within Claude Code.

## Installation

### Quick Install
```bash
./setup_slash_command.sh
```

### Manual Install
```bash
mkdir -p ~/.claude/commands
cp .claude/commands/idea.md ~/.claude/commands/
```

**Important:** Restart Claude Code after installation.

## How It Works

The slash command acts as a natural language translator that:
1. Interprets your request in plain English
2. Translates it to the appropriate `idea` CLI command
3. Executes the command
4. Shows you the results

## Usage Examples

### Adding Tasks/Ideas

```
/idea make sure we change the pin configuration on the pinion project
→ idea add "Change pin configuration on pinion project" -t pinion -p high

/idea remind me to review the authentication docs, tag it as security
→ idea add "Review authentication docs" -t security

/idea we need to update the database schema
→ idea add "Update database schema" -t database
```

### Viewing Tasks

```
/idea give me pinion tasks
→ idea list --tag pinion

/idea show me all high priority items
→ idea list --priority high

/idea what should I work on next?
→ idea next

/idea show me todo items
→ idea list --status todo

/idea show me work-related tasks
→ idea list --tag work
```

### Updating Tasks

```
/idea mark task abc123 as done
→ idea update abc123 -s done

/idea change abc123 to high priority
→ idea update abc123 -p high

/idea mark def456 as in progress
→ idea update def456 -s in-progress
```

### Getting Details

```
/idea show me details for task abc123
→ idea get abc123
```

## Smart Features

### Auto-Tagging
The command automatically extracts project/context as tags:
- "work on the **pinion** project" → `-t pinion`
- "**security** issue to fix" → `-t security`
- "**urgent** task" → `-p high`

### Priority Detection
Urgency words are detected and mapped to priorities:
- "urgent", "asap", "critical" → `high`
- "important", "soon" → `high`
- "eventually", "nice to have" → `low`
- Default → `medium`

### Status Inference
Action words map to status:
- "mark as done/complete" → `-s done`
- "start working on" → `-s in-progress`
- "archive" → `-s archived`

## Tips

### Be Natural
You don't need to use exact CLI syntax. Just describe what you want:
```
Good: /idea remind me to check the logs tomorrow
Good: /idea show urgent tasks
Good: /idea we should refactor the auth module
```

### Multiple Tags
You can mention multiple topics, and they'll be extracted:
```
/idea review the security and authentication documentation
→ Extracts both "security" and "authentication" as tags
```

### Context Awareness
The command understands context:
```
/idea high priority: fix the memory leak in production
→ Creates high priority task tagged with "production"
```

## Comparison with Direct CLI

| Approach | Example |
|----------|---------|
| **Slash Command** | `/idea make sure we review auth` |
| **Direct CLI** | `idea add "Review auth" -t review` |
| | |
| **Slash Command** | `/idea show me high priority tasks` |
| **Direct CLI** | `idea list --priority high` |
| | |
| **Slash Command** | `/idea mark abc123 as done` |
| **Direct CLI** | `idea update abc123 -s done` |

## Troubleshooting

### Command Not Found
- Ensure the command is installed: `ls ~/.claude/commands/idea.md`
- Restart Claude Code
- Check Claude Code's command palette for `/idea`

### Unexpected Behavior
The command shows you what CLI command it's running. If it's not what you expected:
- Be more specific in your request
- Use different wording
- Fall back to direct CLI commands

### Manual Override
You can always use the CLI directly:
```bash
idea add "Task" -t tag -p high
```

## Advanced Usage

### Chaining Operations
You can handle multiple tasks in one conversation:
```
/idea show me all pinion tasks
[results shown]
Now mark the first one as done
[uses the ID from previous results]
```

### Custom Metadata
For complex metadata, use the CLI directly:
```bash
idea add "Complex task" -m '{"deadline": "2025-02-01", "budget": 5000}'
```

## Integration with Workflow

### Daily Review
```
/idea what should I work on next?
```

### Quick Capture
```
/idea don't forget to check server logs
/idea review PR #456
/idea meeting with Sarah at 2pm
```

### Project Management
```
/idea show me all pinion-project tasks
/idea mark completed tasks from yesterday
```

## Benefits

1. **Faster**: No need to remember CLI syntax
2. **Natural**: Write like you think
3. **Smart**: Auto-extracts tags, priorities, context
4. **Transparent**: Shows the actual command being run
5. **Flexible**: Works alongside direct CLI usage

## System-Wide Availability

The slash command is installed **globally** and works in:
- Any Claude Code session
- Any project/directory
- Alongside other Claude Code features

## Updates

To update the slash command:
```bash
cd /path/to/ToDoMCP
./setup_slash_command.sh
```

This will overwrite the existing command with any improvements.

## Support

If you encounter issues:
1. Check the command file exists: `cat ~/.claude/commands/idea.md`
2. Verify the CLI works: `idea list`
3. Restart Claude Code
4. File an issue with example input/output

## See Also

- [README.md](README.md) - Full documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick setup guide
- [API_EXAMPLES.md](API_EXAMPLES.md) - Direct CouchDB API usage
