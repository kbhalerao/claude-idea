# Direct CouchDB API Examples

These examples show how to interact directly with CouchDB using curl or any HTTP client. This is useful for:
- Claude mobile app integration
- Custom scripts
- Direct API testing
- Understanding the underlying data structure

Replace `localhost:5984` with your server URL and update credentials as needed.

## Authentication

All requests use HTTP Basic Authentication:

```bash
# Format
curl -u username:password http://server:5984/...

# With environment variables
export COUCH_URL="http://localhost:5984"
export COUCH_AUTH="admin:secretpass"
```

## Database Operations

### Check Server Status

```bash
curl -u $COUCH_AUTH $COUCH_URL/
```

Response:
```json
{"couchdb":"Welcome","version":"3.3.3"}
```

### List All Databases

```bash
curl -u $COUCH_AUTH $COUCH_URL/_all_dbs
```

### Create Database

```bash
curl -u $COUCH_AUTH -X PUT $COUCH_URL/ideas
```

### Get Database Info

```bash
curl -u $COUCH_AUTH $COUCH_URL/ideas
```

## Document Operations (CRUD)

### Create an Idea (POST)

```bash
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas \
  -H "Content-Type: application/json" \
  -d '{
    "type": "idea",
    "content": "Build a mobile app for tracking habits",
    "tags": ["mobile", "health"],
    "priority": "high",
    "status": "todo",
    "metadata": {},
    "created": "2025-01-15T10:00:00Z",
    "updated": "2025-01-15T10:00:00Z"
  }'
```

Response:
```json
{"ok":true,"id":"abc123...","rev":"1-xyz456..."}
```

### Create with Custom ID (PUT)

```bash
curl -u $COUCH_AUTH \
  -X PUT $COUCH_URL/ideas/my-custom-id \
  -H "Content-Type: application/json" \
  -d '{
    "type": "idea",
    "content": "Custom ID example",
    "status": "todo",
    "priority": "medium",
    "tags": []
  }'
```

### Read an Idea (GET)

```bash
curl -u $COUCH_AUTH $COUCH_URL/ideas/abc123
```

Response:
```json
{
  "_id": "abc123",
  "_rev": "1-xyz456",
  "type": "idea",
  "content": "Build a mobile app for tracking habits",
  "tags": ["mobile", "health"],
  "priority": "high",
  "status": "todo"
}
```

### Update an Idea (PUT)

```bash
# Get current document first to get _rev
DOC=$(curl -s -u $COUCH_AUTH $COUCH_URL/ideas/abc123)
REV=$(echo $DOC | jq -r '._rev')

# Update with new _rev
curl -u $COUCH_AUTH \
  -X PUT $COUCH_URL/ideas/abc123 \
  -H "Content-Type: application/json" \
  -d "{
    \"_rev\": \"$REV\",
    \"type\": \"idea\",
    \"content\": \"Updated content\",
    \"status\": \"done\",
    \"priority\": \"high\",
    \"tags\": [\"mobile\", \"health\"]
  }"
```

### Delete an Idea (DELETE)

```bash
# Get _rev first
DOC=$(curl -s -u $COUCH_AUTH $COUCH_URL/ideas/abc123)
REV=$(echo $DOC | jq -r '._rev')

# Delete
curl -u $COUCH_AUTH -X DELETE "$COUCH_URL/ideas/abc123?rev=$REV"
```

## Query Operations

### List All Ideas

```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_all_docs?include_docs=true"
```

With limit and skip:
```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_all_docs?include_docs=true&limit=10&skip=0"
```

### Filter by Status (using view)

```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_status?key=\"todo\"&include_docs=true"
```

Other statuses:
```bash
# In progress
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_status?key=\"in-progress\"&include_docs=true"

# Done
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_status?key=\"done\"&include_docs=true"
```

### Filter by Priority

```bash
# High priority
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_priority?key=\"high\"&include_docs=true"

# Medium priority
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_priority?key=\"medium\"&include_docs=true"
```

### Search by Tag

```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_tag?key=\"work\"&include_docs=true"
```

### Get Next Actions

```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/next_actions?include_docs=true&limit=5"
```

## Bulk Operations

### Bulk Insert

```bash
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas/_bulk_docs \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      {
        "type": "idea",
        "content": "First idea",
        "status": "todo",
        "priority": "high",
        "tags": []
      },
      {
        "type": "idea",
        "content": "Second idea",
        "status": "todo",
        "priority": "medium",
        "tags": ["work"]
      }
    ]
  }'
```

### Bulk Update/Delete

```bash
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas/_bulk_docs \
  -H "Content-Type: application/json" \
  -d '{
    "docs": [
      {
        "_id": "abc123",
        "_rev": "1-xyz",
        "type": "idea",
        "content": "Updated",
        "status": "done"
      },
      {
        "_id": "def456",
        "_rev": "2-abc",
        "_deleted": true
      }
    ]
  }'
```

## Using with Claude Mobile

Ask Claude mobile to make these requests for you:

```
Can you add an idea to my CouchDB database?

URL: http://my-server.com:5984/ideas
Method: POST
Auth: Basic (username: admin, password: mypass)
Body:
{
  "type": "idea",
  "content": "Research new authentication methods",
  "status": "todo",
  "priority": "high",
  "tags": ["security", "research"],
  "created": "2025-01-15T14:30:00Z",
  "updated": "2025-01-15T14:30:00Z"
}
```

Or to query:

```
Can you get my next actions from CouchDB?

URL: http://my-server.com:5984/ideas/_design/queries/_view/next_actions?include_docs=true&limit=5
Method: GET
Auth: Basic (username: admin, password: mypass)

Then format the results nicely for me.
```

## Advanced Queries

### Find with Selector (Mango Query)

```bash
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas/_find \
  -H "Content-Type: application/json" \
  -d '{
    "selector": {
      "type": "idea",
      "status": "todo",
      "priority": "high"
    },
    "limit": 10,
    "sort": [{"created": "desc"}]
  }'
```

### Complex Query

```bash
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas/_find \
  -H "Content-Type: application/json" \
  -d '{
    "selector": {
      "type": "idea",
      "$or": [
        {"priority": "high"},
        {"status": "in-progress"}
      ]
    }
  }'
```

## Export/Import

### Export All Ideas

```bash
curl -u $COUCH_AUTH "$COUCH_URL/ideas/_all_docs?include_docs=true" > ideas_backup.json
```

### Import from Backup

```bash
# Extract just the docs
cat ideas_backup.json | jq '{docs: [.rows[].doc]}' > import.json

# Import
curl -u $COUCH_AUTH \
  -X POST $COUCH_URL/ideas/_bulk_docs \
  -H "Content-Type: application/json" \
  -d @import.json
```

## Tips

### Using jq for Pretty Output

```bash
curl -s -u $COUCH_AUTH $COUCH_URL/ideas/_all_docs?include_docs=true | jq '.'
```

### Extract Just Content

```bash
curl -s -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/next_actions?include_docs=true" \
  | jq -r '.rows[].doc | "\(.priority) - \(.content)"'
```

### Count Ideas by Status

```bash
curl -s -u $COUCH_AUTH "$COUCH_URL/ideas/_design/queries/_view/by_status?group=true" \
  | jq '.rows[] | {status: .key, count: .value}'
```

## Error Handling

### Common Error Responses

**401 Unauthorized**
```json
{"error":"unauthorized","reason":"Name or password is incorrect."}
```
→ Check your credentials

**404 Not Found**
```json
{"error":"not_found","reason":"Database does not exist."}
```
→ Create database or check name

**409 Conflict**
```json
{"error":"conflict","reason":"Document update conflict."}
```
→ Get latest _rev and retry

**400 Bad Request**
```json
{"error":"bad_request","reason":"invalid UTF-8 JSON"}
```
→ Check JSON syntax

## Security Notes

For production:
1. Use HTTPS instead of HTTP
2. Don't put credentials in URLs or scripts
3. Use CouchDB's `_users` database for proper auth
4. Enable CORS only for trusted origins
5. Use per-database authentication

## References

- [CouchDB HTTP API Docs](https://docs.couchdb.org/en/stable/api/index.html)
- [CouchDB Guide](https://docs.couchdb.org/en/stable/intro/index.html)
