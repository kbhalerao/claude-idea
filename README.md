# Idea Capture System

A simple, personal idea capture and management system with CouchDB backend. Works seamlessly with Claude Code, Gemini CLI, and Claude mobile app.

## Features

- **Quick Capture**: Instantly save ideas from command line or AI assistants
- **Flexible Organization**: Tags, priorities, and status tracking
- **Smart Queries**: "What should I do next?", filter by status/priority/tags
- **Cross-Platform**: Works with CLI tools and mobile apps
- **Cloud Sync**: CouchDB handles storage and replication
- **MCP Integration**: Native integration with Claude Code via MCP server

## Architecture

```
┌─────────────────┐
│  Claude Code    │──┐
│  Gemini CLI     │  │
│  Claude Mobile  │  ├──> HTTP ──> CouchDB Server
│  Direct CLI     │  │              (your server)
└─────────────────┘──┘
```

No complex middleware - just direct HTTP communication with CouchDB's native REST API.

## Installation

### 1. Set up CouchDB

On your server, install CouchDB:

```bash
# Using Docker (recommended)
docker run -d --name couchdb \
  -p 5984:5984 \
  -e COUCHDB_USER=admin \
  -e COUCHDB_PASSWORD=your_password \
  couchdb:latest

# Or install natively
# Ubuntu/Debian
sudo apt-get install couchdb

# macOS
brew install couchdb
```

Enable CORS if accessing from mobile:

```bash
curl -X PUT http://admin:password@localhost:5984/_node/_local/_config/httpd/enable_cors -d '"true"'
curl -X PUT http://admin:password@localhost:5984/_node/_local/_config/cors/origins -d '"*"'
curl -X PUT http://admin:password@localhost:5984/_node/_local/_config/cors/credentials -d '"true"'
```

### 2. Install the CLI Tool

Clone this repository and install:

```bash
cd idea-capture
pip install -e .
```

### 3. Configure Credentials

Create a `.env` file in the project directory:

```bash
cp .env.example .env
```

Edit `.env` with your CouchDB details:

```
COUCHDB_URL=http://your-server:5984
COUCHDB_USERNAME=admin
COUCHDB_PASSWORD=your_password
COUCHDB_DATABASE=ideas
```

### 4. Initialize Database

Run the setup command to create the database and install query views:

```bash
idea setup
```

### 5. (Optional) Install Slash Command for Claude Code

Install the natural language `/idea` slash command:

```bash
./setup_slash_command.sh
```

This allows you to use natural language in Claude Code:
```
/idea make sure we review the authentication module
/idea show me all high priority tasks
/idea what should I work on next?
```

**Note:** Restart Claude Code after installation.

## Usage

### Command Line Interface

#### Add an idea

```bash
# Simple
idea add "Build a mobile app for tracking workouts"

# With tags and priority
idea add "Review PR #123" -t work -t urgent -p high

# With metadata
idea add "Research ML frameworks" -m '{"context": "for new project", "link": "https://..."}'
```

#### List ideas

```bash
# All ideas
idea list

# Filter by status
idea list --status todo

# Filter by priority
idea list --priority high

# Filter by tag
idea list --tag work

# Limit results
idea list --limit 10
```

#### Get next actions

```bash
# Show top 5 priority tasks
idea next

# Show top 10
idea next -l 10
```

#### Update an idea

```bash
# Update content
idea update <id> -c "Updated content"

# Change status
idea update <id> -s in-progress

# Add tags
idea update <id> --add-tag meeting --add-tag followup

# Change priority
idea update <id> -p high
```

#### Delete an idea

```bash
idea delete <id>
```

### Natural Language Slash Command (Recommended for Claude Code)

The `/idea` slash command lets you use natural language instead of remembering CLI syntax.

#### Installation

Run the setup script:
```bash
./setup_slash_command.sh
```

Or manually copy:
```bash
mkdir -p ~/.claude/commands
cp .claude/commands/idea.md ~/.claude/commands/
```

**Restart Claude Code** for the command to appear.

#### Usage Examples

```
/idea make sure we change the pin configuration on the pinion project
→ Runs: idea add "Change pin configuration on pinion project" -t pinion -p high

/idea give me pinion tasks
→ Runs: idea list --tag pinion

/idea what should I work on next?
→ Runs: idea next

/idea show me all high priority items
→ Runs: idea list --priority high

/idea mark task abc123 as done
→ Runs: idea update abc123 -s done

/idea add a reminder to review auth docs, tag it security
→ Runs: idea add "Review auth docs" -t security
```

The command intelligently:
- Extracts the core task from natural language
- Infers appropriate tags from context (project names, topics)
- Determines priority based on urgency words
- Translates actions to appropriate CLI commands

### MCP Server (Alternative for Claude Code)

#### 1. Start the MCP Server

Add to your Claude Code MCP configuration (`~/.config/claude-code/mcp_servers.json`):

```json
{
  "idea-capture": {
    "command": "python",
    "args": ["-m", "idea_capture.mcp_server"],
    "cwd": "/path/to/ToDoMCP",
    "env": {
      "COUCHDB_URL": "http://your-server:5984",
      "COUCHDB_USERNAME": "admin",
      "COUCHDB_PASSWORD": "your_password",
      "COUCHDB_DATABASE": "ideas"
    }
  }
}
```

#### 2. Use in Claude Code

Once configured, Claude Code will have access to these tools:

- `idea_add` - Add a new idea
- `idea_list` - List ideas with filtering
- `idea_get` - Get a specific idea
- `idea_update` - Update an idea
- `idea_delete` - Delete an idea
- `idea_next_actions` - Get next priority tasks
- `idea_search_by_tags` - Search by tags

Example prompts:

```
"Add an idea: Review the authentication module"

"What should I work on next?"

"Show me all high priority tasks"

"Update idea <id> to mark it as done"
```

### Claude Mobile App

The Claude mobile app can interact with your CouchDB directly via HTTP:

```
I need to add an idea to my CouchDB. Can you make a POST request to
http://my-server:5984/ideas with this content:
{"type": "idea", "content": "...", "status": "todo", ...}

Use basic auth: username=admin, password=my_password
```

## Data Schema

Each idea is stored as a CouchDB document:

```json
{
  "_id": "unique-uuid",
  "_rev": "revision-id",
  "type": "idea",
  "content": "The actual idea text",
  "tags": ["tag1", "tag2"],
  "priority": "high|medium|low",
  "status": "todo|in-progress|done|archived",
  "metadata": {
    "context": "optional context",
    "links": ["url1", "url2"]
  },
  "created": "2025-01-01T12:00:00Z",
  "updated": "2025-01-01T12:00:00Z"
}
```

## CouchDB Views

The system uses the following views for queries:

- `queries/by_status` - Filter ideas by status
- `queries/by_priority` - Filter ideas by priority
- `queries/by_tag` - Search ideas by tag
- `queries/next_actions` - Get todo items sorted by priority

These are automatically installed by `idea setup`.

## Direct CouchDB API Access

You can also interact directly with CouchDB using curl or any HTTP client:

```bash
# List all ideas
curl -u admin:password http://your-server:5984/ideas/_all_docs?include_docs=true

# Add an idea
curl -u admin:password -X POST http://your-server:5984/ideas \
  -H "Content-Type: application/json" \
  -d '{"type":"idea","content":"My idea","status":"todo","priority":"medium","tags":[]}'

# Get next actions
curl -u admin:password http://your-server:5984/ideas/_design/queries/_view/next_actions?include_docs=true
```

## Advanced Usage

### Custom Metadata

Store any additional context with your ideas:

```bash
idea add "Meeting with Sarah" -m '{
  "location": "Conference Room A",
  "attendees": ["Sarah", "John"],
  "agenda": "Q1 Planning"
}'
```

### Workflow Status Management

Track your ideas through a workflow:

```bash
# Capture idea
idea add "Implement feature X" -s todo

# Start working
idea update <id> -s in-progress

# Mark complete
idea update <id> -s done

# Archive old ideas
idea update <id> -s archived
```

### Tag-Based Organization

Organize ideas with multiple tags:

```bash
idea add "Review codebase" -t work -t code-review -t urgent
idea list --tag work
idea list --tag urgent
```

## Troubleshooting

### Connection Issues

```bash
# Test CouchDB connection
curl http://admin:password@your-server:5984/

# Should return: {"couchdb":"Welcome",...}
```

### Database Not Found

Run the setup command:

```bash
idea setup
```

### View Not Found

Reinstall design documents:

```bash
idea setup
```

## Security Notes

This is designed as a **personal system** with hardcoded credentials. For production use:

1. Use environment variables for credentials
2. Enable SSL/TLS on CouchDB
3. Implement proper authentication
4. Restrict CORS origins
5. Use CouchDB's built-in user management

## Future Enhancements

- [ ] Reminders/notifications
- [ ] Recurring ideas
- [ ] Links between ideas
- [ ] Rich text formatting
- [ ] File attachments
- [ ] Search full-text content
- [ ] Export to markdown/JSON
- [ ] Mobile-optimized web UI

## License

MIT

## Support

For issues or questions, please file an issue on GitHub.
