"""CouchDB database operations."""

import json
import requests
from typing import Optional
from .config import config
from .models import JournalIdea


class CouchDBClient:
    """Client for interacting with CouchDB."""

    def __init__(self):
        self.config = config
        self.session = requests.Session()
        if self.config.auth:
            self.session.auth = self.config.auth

    def _request(self, method: str, path: str, **kwargs):
        """Make HTTP request to CouchDB."""
        url = f"{self.config.url}/{path}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}

    def ensure_database(self):
        """Create database if it doesn't exist."""
        try:
            self._request("GET", self.config.database)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                self._request("PUT", self.config.database)
            else:
                raise

    def create_idea(self, idea: JournalIdea) -> JournalIdea:
        """Create a new idea."""
        self.ensure_database()
        doc = idea.to_dict()
        result = self._request("POST", self.config.database, json=doc)
        idea._id = result["id"]
        idea._rev = result["rev"]
        return idea

    def get_idea(self, idea_id: str) -> Optional[JournalIdea]:
        """Get an idea by ID."""
        try:
            doc = self._request("GET", f"{self.config.database}/{idea_id}")
            return JournalIdea.from_dict(doc)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def update_idea(self, idea: JournalIdea) -> JournalIdea:
        """Update an existing idea."""
        idea.update_timestamp()
        doc = idea.to_dict()
        result = self._request("PUT", f"{self.config.database}/{idea._id}", json=doc)
        idea._rev = result["rev"]
        return idea

    def delete_idea(self, idea_id: str, rev: str) -> bool:
        """Delete an idea."""
        try:
            self._request("DELETE", f"{self.config.database}/{idea_id}?rev={rev}")
            return True
        except requests.HTTPError:
            return False

    def list_ideas(self, limit: Optional[int] = None, skip: int = 0) -> list[JournalIdea]:
        """List all ideas."""
        params = {
            "include_docs": "true",
            "skip": skip,
        }
        if limit:
            params["limit"] = limit

        result = self._request("GET", f"{self.config.database}/_all_docs", params=params)
        ideas = []
        for row in result.get("rows", []):
            doc = row.get("doc")
            if doc and doc.get("type") == "idea":
                ideas.append(JournalIdea.from_dict(doc))
        return ideas

    def query_view(self, design_doc: str, view_name: str, **params) -> list[JournalIdea]:
        """Query a CouchDB view."""
        params["include_docs"] = "true"
        result = self._request(
            "GET", f"{self.config.database}/_design/{design_doc}/_view/{view_name}", params=params
        )
        ideas = []
        for row in result.get("rows", []):
            doc = row.get("doc")
            if doc:
                ideas.append(JournalIdea.from_dict(doc))
        return ideas

    def get_by_status(self, status: str) -> list[JournalIdea]:
        """Get ideas by status."""
        return self.query_view("queries", "by_status", key=f'"{status}"')

    def get_by_priority(self, priority: str) -> list[JournalIdea]:
        """Get ideas by priority."""
        return self.query_view("queries", "by_priority", key=f'"{priority}"')

    def get_next_actions(self) -> list[JournalIdea]:
        """Get next actions (todo items sorted by priority)."""
        return self.query_view("queries", "next_actions")

    def search_by_tags(self, tag: str) -> list[JournalIdea]:
        """Search ideas by tag."""
        return self.query_view("queries", "by_tag", key=f'"{tag}"')

    def get_by_status_and_priority(self, status: str, priority: str) -> list[JournalIdea]:
        """Get ideas by status and priority using compound key."""
        priority_order = {"high": 1, "medium": 2, "low": 3}
        key = [status, priority_order.get(priority, 4)]
        return self.query_view("queries", "by_status_and_priority", key=json.dumps(key))

    def get_by_tag_and_status(self, tag: str, status: str) -> list[JournalIdea]:
        """Get ideas by tag and status using compound key."""
        key = [tag, status]
        return self.query_view("queries", "by_tag_and_status", key=json.dumps(key))

    def get_all_tags(self) -> dict[str, int]:
        """Get all unique tags with usage counts."""
        result = self._request(
            "GET", f"{self.config.database}/_design/queries/_view/all_tags", params={"group": "true"}
        )
        return {row["key"]: row["value"] for row in result.get("rows", [])}

    def get_metadata_keys(self) -> dict[str, int]:
        """Get all metadata keys with usage counts."""
        result = self._request(
            "GET", f"{self.config.database}/_design/queries/_view/metadata_keys", params={"group": "true"}
        )
        return {row["key"]: row["value"] for row in result.get("rows", [])}

    def install_design_docs(self):
        """Install design documents for views."""
        design_doc = {
            "_id": "_design/queries",
            "views": {
                # Simple views with null values - rely on include_docs for efficiency
                "by_status": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            emit(doc.status, null);
                        }
                    }
                    """,
                    "reduce": "_count"
                },
                "by_priority": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            emit(doc.priority, null);
                        }
                    }
                    """,
                    "reduce": "_count"
                },
                "by_tag": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.tags) {
                            for (var i = 0; i < doc.tags.length; i++) {
                                emit(doc.tags[i], null);
                            }
                        }
                    }
                    """,
                    "reduce": "_count"
                },
                "next_actions": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.status === 'todo') {
                            var priority_order = {high: 1, medium: 2, low: 3};
                            emit(priority_order[doc.priority] || 4, null);
                        }
                    }
                    """
                },
                # Compound key views for multi-criteria filtering
                "by_status_and_priority": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            var priority_order = {high: 1, medium: 2, low: 3};
                            emit([doc.status, priority_order[doc.priority] || 4], null);
                        }
                    }
                    """
                },
                "by_tag_and_status": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.tags) {
                            for (var i = 0; i < doc.tags.length; i++) {
                                emit([doc.tags[i], doc.status], null);
                            }
                        }
                    }
                    """
                },
                # Fauxton-friendly view with formatted display
                "formatted_list": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            var priority_emoji = {high: '🔴', medium: '🟡', low: '🟢'};
                            var status_emoji = {todo: '☐', 'in-progress': '⏳', done: '✓', archived: '📦'};
                            var priority_order = {high: 1, medium: 2, low: 3};

                            var tags_display = '';
                            if (doc.tags && doc.tags.length > 0) {
                                tags_display = doc.tags.map(function(t) { return '#' + t; }).join(', ');
                            }

                            var display = status_emoji[doc.status] + ' ' +
                                         priority_emoji[doc.priority] + ' ' +
                                         doc.content;

                            if (tags_display) {
                                display += ' [' + tags_display + ']';
                            }

                            // Emit with priority order as key for sorting, display string as value
                            emit([priority_order[doc.priority] || 4, doc.created], {
                                display: display,
                                id: doc._id,
                                content: doc.content,
                                priority: doc.priority,
                                status: doc.status,
                                tags: doc.tags || [],
                                created: doc.created,
                                updated: doc.updated
                            });
                        }
                    }
                    """
                },
                # All metadata keys for filtering options
                "metadata_keys": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.metadata) {
                            for (var key in doc.metadata) {
                                if (doc.metadata.hasOwnProperty(key)) {
                                    emit(key, doc.metadata[key]);
                                }
                            }
                        }
                    }
                    """,
                    "reduce": "_count"
                },
                # All unique tags for autocomplete/filtering
                "all_tags": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.tags) {
                            for (var i = 0; i < doc.tags.length; i++) {
                                emit(doc.tags[i], 1);
                            }
                        }
                    }
                    """,
                    "reduce": "_sum"
                },
            },
        }

        self.ensure_database()
        try:
            # Try to get existing design doc to preserve _rev
            existing = self._request("GET", f"{self.config.database}/_design/queries")
            design_doc["_rev"] = existing["_rev"]
        except requests.HTTPError:
            pass

        self._request("PUT", f"{self.config.database}/_design/queries", json=design_doc)


# Global client instance
db = CouchDBClient()
