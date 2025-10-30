# Quick Start Guide

Get up and running with Idea Capture in 5 minutes.

## Step 1: CouchDB Setup (2 minutes)

### Option A: Docker (Easiest)

```bash
docker run -d --name couchdb \
  -p 5984:5984 \
  -e COUCHDB_USER=admin \
  -e COUCHDB_PASSWORD=secretpass \
  couchdb:latest
```

### Option B: Using Existing CouchDB

Skip to Step 2 if you already have CouchDB running.

## Step 2: Install Idea Capture (1 minute)

```bash
# Clone/navigate to this directory
cd ToDoMCP

# Install
pip install -e .
```

## Step 3: Configure (1 minute)

Create `.env` file:

```bash
cat > .env << EOF
COUCHDB_URL=http://localhost:5984
COUCHDB_USERNAME=admin
COUCHDB_PASSWORD=secretpass
COUCHDB_DATABASE=ideas
EOF
```

## Step 4: Initialize (30 seconds)

```bash
idea setup
```

You should see:
```
Setting up database...
Database 'ideas' is ready
Installing design documents...
Design documents installed

Setup complete!
```

## Step 5: Try It Out! (30 seconds)

```bash
# Add your first idea
idea add "Learn more about AI agents"

# Add another with tags
idea add "Review project documentation" -t work -p high

# See what's next
idea next

# List everything
idea list
```

## Step 6: (Optional) Natural Language Interface (30 seconds)

Install the `/idea` slash command for Claude Code:

```bash
./setup_slash_command.sh
```

Restart Claude Code, then use natural language:
```
/idea make sure we review the API endpoints
/idea show me high priority tasks
/idea what should I work on next?
```

## What's Next?

### Use Natural Language Slash Command (Recommended)

The `/idea` command is now installed! Use it in Claude Code with natural language:

```
/idea add a task to refactor the database layer, tag it as technical-debt
/idea show me all work items
/idea mark abc123 as done
```

### Or Use MCP Server (Alternative)

Add to `~/.config/claude-code/mcp_servers.json`:

```json
{
  "idea-capture": {
    "command": "python",
    "args": ["-m", "idea_capture.mcp_server"],
    "cwd": "/path/to/ToDoMCP",
    "env": {
      "COUCHDB_URL": "http://localhost:5984",
      "COUCHDB_USERNAME": "admin",
      "COUCHDB_PASSWORD": "secretpass",
      "COUCHDB_DATABASE": "ideas"
    }
  }
}
```

Then in Claude Code:
```
"What should I work on next?"
"Add an idea: Implement user authentication"
```

### Use with Claude Mobile

Ask Claude:
```
"Can you add an idea to my CouchDB?
URL: http://my-server:5984/ideas
Auth: admin:secretpass
Content: 'Check email responses'"
```

Claude will make the HTTP request for you.

## Common Commands Cheat Sheet

```bash
# Add
idea add "content" -t tag1 -t tag2 -p high

# List
idea list                    # all
idea list --status todo      # filter by status
idea list --priority high    # filter by priority
idea list --tag work         # filter by tag

# Next actions
idea next                    # top 5
idea next -l 10              # top 10

# Update
idea update <id> -s done
idea update <id> -p high
idea update <id> --add-tag urgent

# Delete
idea delete <id>

# Get details
idea get <id>
```

## Tips

1. **Quick Capture**: Create a shell alias
   ```bash
   alias i='idea add'
   # Then: i "Quick thought"
   ```

2. **View in Browser**: Open CouchDB's Fauxton UI
   ```
   http://localhost:5984/_utils
   ```

3. **Backup**: CouchDB handles replication automatically
   ```bash
   # Replicate to another server
   curl -X POST http://admin:pass@localhost:5984/_replicate \
     -d '{"source":"ideas","target":"http://backup-server:5984/ideas"}' \
     -H "Content-Type: application/json"
   ```

## Troubleshooting

**"Configuration error: CouchDB credentials not configured"**
- Make sure `.env` file exists with valid credentials

**"Connection refused"**
- Check CouchDB is running: `curl http://localhost:5984/`
- Verify the URL in `.env`

**"Database does not exist"**
- Run: `idea setup`

**Commands not working**
- Reinstall: `pip install -e .`
- Verify: `which idea`

## Next Steps

Read the full [README.md](README.md) for:
- Advanced usage patterns
- MCP server configuration
- Mobile app integration
- Custom metadata and workflows
- Direct CouchDB API access
