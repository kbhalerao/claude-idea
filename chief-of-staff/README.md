# Chief of Staff API

Personal AI Assistant Platform - Document and context management API.

## Overview

Chief of Staff (CoS) is a multi-tenant, context-aware personal AI assistant platform. It provides:

- **Document management**: Ideas, tasks, notes, and context snapshots
- **Project-aware capture**: Auto-tags from Claude Code's context
- **Priority queue**: Smart ordering by priority and due dates
- **Multi-tenant**: Scope-per-user isolation in Couchbase

## Quick Start

### Prerequisites

- Python 3.11+
- Couchbase Server (with `chief_of_staff` bucket configured)
- uv (recommended) or pip

### Installation

```bash
# Clone and install
cd chief-of-staff
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your Couchbase credentials
```

### Running

```bash
# Development
uv run uvicorn cos.main:app --reload

# Production
uv run uvicorn cos.main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker-compose up -d
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/cos/health` | GET | Health check |
| `/api/cos/docs` | POST | Create document |
| `/api/cos/docs` | GET | List documents (with filters) |
| `/api/cos/docs/{id}` | GET | Get single document |
| `/api/cos/docs/{id}` | PATCH | Update document |
| `/api/cos/docs/{id}` | DELETE | Delete document |
| `/api/cos/docs/next` | GET | Priority queue |
| `/api/cos/docs/inbox` | GET | Inbox items |
| `/api/cos/docs/due` | GET | Tasks due soon |
| `/api/cos/tags` | GET | All tags with counts |
| `/api/cos/stats` | GET | Statistics |
| `/api/cos/context` | GET | Latest context snapshot |
| `/api/cos/context` | POST | Save context snapshot |
| `/api/cos/projects/{name}/docs` | GET | Project documents |
| `/api/cos/projects/{name}/recent` | GET | Recent project activity |

## Configuration

Environment variables (prefix with `COS_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `COUCHBASE_HOST` | `macstudio.local` | Couchbase server host |
| `COUCHBASE_USERNAME` | `Administrator` | Couchbase username |
| `COUCHBASE_PASSWORD` | (required) | Couchbase password |
| `COUCHBASE_BUCKET` | `chief_of_staff` | Bucket name |
| `DEFAULT_USER` | `kaustubh` | Default user for development |
| `DEBUG` | `false` | Enable debug mode |

## Couchbase Setup

Create the bucket and indexes:

```sql
-- Create indexes (run in Query workbench)
CREATE INDEX idx_doc_type ON `chief_of_staff`.`user_kaustubh`.`documents`(doc_type);
CREATE INDEX idx_status_priority ON `chief_of_staff`.`user_kaustubh`.`documents`(status, priority);
CREATE INDEX idx_project ON `chief_of_staff`.`user_kaustubh`.`documents`(source.project);
CREATE INDEX idx_tags ON `chief_of_staff`.`user_kaustubh`.`documents`(DISTINCT ARRAY t FOR t IN tags END);
CREATE INDEX idx_due_date ON `chief_of_staff`.`user_kaustubh`.`documents`(due_date) WHERE doc_type = "task";
CREATE INDEX idx_updated ON `chief_of_staff`.`user_kaustubh`.`documents`(updated_at);
```

## Testing

```bash
uv run pytest
```

## License

Private - Internal use only
