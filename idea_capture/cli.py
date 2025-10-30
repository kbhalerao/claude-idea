"""Command-line interface for idea capture."""

import click
import json
from .db import db
from .models import JournalIdea
from .config import config


@click.group()
def main():
    """Idea Capture - Simple idea management with CouchDB."""
    try:
        config.validate()
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('content')
@click.option('--tags', '-t', multiple=True, help='Tags for the idea')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium')
@click.option('--status', '-s', type=click.Choice(['todo', 'in-progress', 'done', 'archived']), default='todo')
@click.option('--metadata', '-m', help='Additional metadata as JSON string')
def add(content, tags, priority, status, metadata):
    """Add a new idea."""

    meta = {}
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError:
            click.echo("Invalid JSON metadata", err=True)
            raise click.Abort()

    idea = JournalIdea(
        content=content,
        tags=[*tags],  # Convert tuple to list without using list()
        priority=priority,
        status=status,
        metadata=meta
    )

    try:
        created = db.create_idea(idea)
        click.echo(f"Created idea: {created._id}")
        _display_idea(created)
    except Exception as e:
        click.echo(f"Error creating idea: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--limit', '-l', type=int, help='Maximum number of ideas to return')
@click.option('--skip', '-s', type=int, default=0, help='Number of ideas to skip')
@click.option('--status', type=click.Choice(['todo', 'in-progress', 'done', 'archived']), help='Filter by status')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), help='Filter by priority')
@click.option('--tag', help='Filter by tag')
def list(limit, skip, status, priority, tag):
    """List ideas. Can combine filters (e.g., --status todo --priority high)."""
    try:
        # Handle compound queries using optimized views
        if status and priority:
            ideas = db.get_by_status_and_priority(status, priority)
        elif tag and status:
            ideas = db.get_by_tag_and_status(tag, status)
        elif tag and priority:
            # No dedicated view for this, filter in Python
            ideas = db.search_by_tags(tag)
            ideas = [i for i in ideas if i.priority == priority]
        elif status:
            ideas = db.get_by_status(status)
        elif priority:
            ideas = db.get_by_priority(priority)
        elif tag:
            ideas = db.search_by_tags(tag)
        else:
            ideas = db.list_ideas(limit=limit, skip=skip)

        if not ideas:
            click.echo("No ideas found")
            return

        # Apply limit if specified for filtered results
        if limit and (status or priority or tag):
            ideas = ideas[:limit]

        for idea in ideas:
            _display_idea(idea)
            click.echo()
    except Exception as e:
        click.echo(f"Error listing ideas: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('idea_id')
def get(idea_id):
    """Get a specific idea by ID."""
    try:
        idea = db.get_idea(idea_id)
        if not idea:
            click.echo(f"Idea not found: {idea_id}", err=True)
            raise click.Abort()

        _display_idea(idea, detailed=True)
    except Exception as e:
        click.echo(f"Error getting idea: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('idea_id')
@click.option('--content', '-c', help='New content')
@click.option('--tags', '-t', multiple=True, help='New tags (replaces existing)')
@click.option('--add-tag', multiple=True, help='Add tags (keeps existing)')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']))
@click.option('--status', '-s', type=click.Choice(['todo', 'in-progress', 'done', 'archived']))
def update(idea_id, content, tags, add_tag, priority, status):
    """Update an existing idea."""
    try:
        idea = db.get_idea(idea_id)
        if not idea:
            click.echo(f"Idea not found: {idea_id}", err=True)
            raise click.Abort()

        if content:
            idea.content = content
        if tags:
            idea.tags = [*tags]
        if add_tag:
            idea.tags.extend(add_tag)
            idea.tags = [*set(idea.tags)]  # Remove duplicates
        if priority:
            idea.priority = priority
        if status:
            idea.status = status

        updated = db.update_idea(idea)
        click.echo(f"Updated idea: {updated._id}")
        _display_idea(updated)
    except Exception as e:
        click.echo(f"Error updating idea: {e}", err=True)
        raise click.Abort()


@main.command()
@click.argument('idea_id')
@click.confirmation_option(prompt='Are you sure you want to delete this idea?')
def delete(idea_id):
    """Delete an idea."""
    try:
        idea = db.get_idea(idea_id)
        if not idea:
            click.echo(f"Idea not found: {idea_id}", err=True)
            raise click.Abort()

        if db.delete_idea(idea._id, idea._rev):
            click.echo(f"Deleted idea: {idea_id}")
        else:
            click.echo(f"Failed to delete idea: {idea_id}", err=True)
    except Exception as e:
        click.echo(f"Error deleting idea: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option('--limit', '-l', type=int, default=5, help='Maximum number of actions to return')
def next(limit):
    """Get next actions (todo items sorted by priority)."""
    try:
        ideas = db.get_next_actions()
        if not ideas:
            click.echo("No pending actions found")
            return

        click.echo(f"Next {min(limit, len(ideas))} action(s):\n")
        for idea in ideas[:limit]:
            _display_idea(idea)
            click.echo()
    except Exception as e:
        click.echo(f"Error getting next actions: {e}", err=True)
        raise click.Abort()


@main.command()
def tags():
    """List all tags with usage counts."""
    try:
        all_tags = db.get_all_tags()
        if not all_tags:
            click.echo("No tags found")
            return

        click.echo("Tags (sorted by usage):\n")
        # Sort by count descending
        sorted_tags = sorted(all_tags.items(), key=lambda x: x[1], reverse=True)
        for tag, count in sorted_tags:
            click.echo(f"  #{tag:<30} {count} idea(s)")
    except Exception as e:
        click.echo(f"Error listing tags: {e}", err=True)
        raise click.Abort()


@main.command()
def stats():
    """Show statistics about your ideas."""
    try:
        from idea_capture.config import config
        import requests

        # Get counts by status
        result = requests.get(
            f"{config.url}/{config.database}/_design/queries/_view/by_status",
            params={"group": "true"},
            auth=config.auth
        )
        status_counts = {row["key"]: row["value"] for row in result.json().get("rows", [])}

        # Get counts by priority
        result = requests.get(
            f"{config.url}/{config.database}/_design/queries/_view/by_priority",
            params={"group": "true"},
            auth=config.auth
        )
        priority_counts = {row["key"]: row["value"] for row in result.json().get("rows", [])}

        # Display statistics
        click.echo("📊 Idea Statistics\n")

        click.echo("By Status:")
        for status in ['todo', 'in-progress', 'done', 'archived']:
            count = status_counts.get(status, 0)
            if count > 0:
                emoji = {'todo': '☐', 'in-progress': '⏳', 'done': '✓', 'archived': '📦'}
                click.echo(f"  {emoji[status]} {status:<15} {count}")

        click.echo("\nBy Priority:")
        for priority in ['high', 'medium', 'low']:
            count = priority_counts.get(priority, 0)
            if count > 0:
                emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                click.echo(f"  {emoji[priority]} {priority:<15} {count}")

        # Get total tags
        all_tags = db.get_all_tags()
        total_tags = len(all_tags)
        click.echo(f"\n🏷️  Total unique tags: {total_tags}")

    except Exception as e:
        click.echo(f"Error getting statistics: {e}", err=True)
        raise click.Abort()


@main.command()
def setup():
    """Set up the database and install design documents."""
    try:
        click.echo("Setting up database...")
        db.ensure_database()
        click.echo(f"Database '{config.database}' is ready")

        click.echo("Installing design documents...")
        db.install_design_docs()
        click.echo("Design documents installed")

        click.echo("\nSetup complete!")
    except Exception as e:
        click.echo(f"Error during setup: {e}", err=True)
        raise click.Abort()


def _display_idea(idea: JournalIdea, detailed: bool = False):
    """Display an idea in a formatted way."""
    status_emoji = {
        'todo': '☐',
        'in-progress': '⏳',
        'done': '✓',
        'archived': '📦'
    }
    priority_emoji = {
        'high': '🔴',
        'medium': '🟡',
        'low': '🟢'
    }

    click.echo(f"{status_emoji.get(idea.status, '?')} {priority_emoji.get(idea.priority, '')} {idea.content}")
    click.echo(f"   ID: {idea._id}")

    if idea.tags:
        tags_str = ', '.join(f"#{tag}" for tag in idea.tags)
        click.echo(f"   Tags: {tags_str}")

    if detailed:
        click.echo(f"   Status: {idea.status}")
        click.echo(f"   Priority: {idea.priority}")
        click.echo(f"   Created: {idea.created}")
        click.echo(f"   Updated: {idea.updated}")
        if idea.metadata:
            click.echo(f"   Metadata: {json.dumps(idea.metadata, indent=2)}")


if __name__ == '__main__':
    main()
