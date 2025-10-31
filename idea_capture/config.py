"""Configuration management for CouchDB connection."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in current working directory first, then in home directory
load_dotenv(Path.cwd() / '.env')
load_dotenv(Path.home() / '.env')


class Config:
    """Configuration for CouchDB connection."""

    def __init__(self):
        self.url = os.getenv('COUCHDB_URL', 'http://localhost:5984')
        self.username = os.getenv('COUCHDB_USERNAME')
        self.password = os.getenv('COUCHDB_PASSWORD')
        self.database = os.getenv('COUCHDB_DATABASE', 'ideas')

    @property
    def auth(self):
        """Return tuple of (username, password) for requests."""
        if self.username and self.password:
            return (self.username, self.password)
        return None

    @property
    def db_url(self):
        """Return full database URL."""
        return f"{self.url}/{self.database}"

    def validate(self):
        """Validate that required configuration is present."""
        if not self.username or not self.password:
            raise ValueError(
                "CouchDB credentials not configured. "
                "Please create a .env file with COUCHDB_USERNAME and COUCHDB_PASSWORD"
            )


# Global config instance
config = Config()
