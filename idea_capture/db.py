"""CouchDB database operations."""

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

    def install_design_docs(self):
        """Install design documents for views."""
        design_doc = {
            "_id": "_design/queries",
            "views": {
                "by_status": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            emit(doc.status, doc);
                        }
                    }
                    """
                },
                "by_priority": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea') {
                            emit(doc.priority, doc);
                        }
                    }
                    """
                },
                "by_tag": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.tags) {
                            for (var i = 0; i < doc.tags.length; i++) {
                                emit(doc.tags[i], doc);
                            }
                        }
                    }
                    """
                },
                "next_actions": {
                    "map": """
                    function(doc) {
                        if (doc.type === 'idea' && doc.status === 'todo') {
                            var priority_order = {high: 1, medium: 2, low: 3};
                            emit(priority_order[doc.priority] || 4, doc);
                        }
                    }
                    """
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
