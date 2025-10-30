#!/bin/bash
# Script to create a new CouchDB user with access to the ideas database

set -e

# Load configuration
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Check for required arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: ./create_user.sh <username> <password>"
    echo ""
    echo "Example:"
    echo "  ./create_user.sh john secretpass123"
    exit 1
fi

NEW_USERNAME="$1"
NEW_PASSWORD="$2"

echo "Creating user: $NEW_USERNAME"
echo "CouchDB Server: $COUCHDB_URL"
echo ""

# Create user document
echo "1. Creating user document..."
curl -X PUT "${COUCHDB_URL}/_users/org.couchdb.user:${NEW_USERNAME}" \
  -u "${COUCHDB_USERNAME}:${COUCHDB_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"${NEW_USERNAME}\",
    \"password\": \"${NEW_PASSWORD}\",
    \"roles\": [],
    \"type\": \"user\"
  }"

echo ""
echo ""

# Grant access to ideas database
echo "2. Granting access to ${COUCHDB_DATABASE} database..."
curl -X PUT "${COUCHDB_URL}/${COUCHDB_DATABASE}/_security" \
  -u "${COUCHDB_USERNAME}:${COUCHDB_PASSWORD}" \
  -H "Content-Type: application/json" \
  -d "{
    \"admins\": {
      \"names\": [\"${COUCHDB_USERNAME}\"],
      \"roles\": []
    },
    \"members\": {
      \"names\": [\"${COUCHDB_USERNAME}\", \"${NEW_USERNAME}\"],
      \"roles\": []
    }
  }"

echo ""
echo ""
echo "✓ User created successfully!"
echo ""
echo "Credentials:"
echo "  Username: ${NEW_USERNAME}"
echo "  Password: ${NEW_PASSWORD}"
echo ""
echo "Test the connection:"
echo "  curl -u ${NEW_USERNAME}:${NEW_PASSWORD} ${COUCHDB_URL}/${COUCHDB_DATABASE}"
echo ""
echo "Or create a new .env file for this user:"
echo "  COUCHDB_URL=${COUCHDB_URL}"
echo "  COUCHDB_USERNAME=${NEW_USERNAME}"
echo "  COUCHDB_PASSWORD=${NEW_PASSWORD}"
echo "  COUCHDB_DATABASE=${COUCHDB_DATABASE}"
