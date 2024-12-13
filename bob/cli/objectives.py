import click
import yaml
import os
from datetime import datetime

OBJECTIVES_FILE = 'bob_objectives.yaml'

def load_objectives():
    """Load existing objectives from file"""
    if os.path.exists(OBJECTIVES_FILE):
        try:
            with open(OBJECTIVES_FILE, 'r') as f:
                return yaml.safe_load(f) or {"objectives": [], "created_at": "", "updated_at": ""}
        except yaml.YAMLError:
            return {"objectives": [], "created_at": "", "updated_at": ""}
    return {"objectives": [], "created_at": "", "updated_at": ""}

def represent_str_multiline(dumper, data):
    """Custom representer for multiline strings"""
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def save_objectives(objectives):
    """Save objectives to file with multiline format"""
    yaml.add_representer(str, represent_str_multiline)
    with open(OBJECTIVES_FILE, 'w') as f:
        yaml.dump(objectives, f, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

@click.group()
def objectives():
    """Manage project objectives"""
    pass

@objectives.command()
def list():
    """List all project objectives"""
    data = load_objectives()
    if not data['objectives']:
        click.echo("No objectives defined yet.")
        return

    click.echo("\nProject Objectives:")
    click.echo("------------------")
    for idx, obj in enumerate(data['objectives'], 1):
        click.echo(f"\n{idx}. {obj['title']}")
        click.echo(f"   Description: {obj['description']}")
        click.echo(f"   Priority: {obj['priority']}")
        click.echo(f"   Added: {obj['added_at']}")

@objectives.command()
@click.option('--file', '-f', type=click.Path(exists=True), help='YAML file containing objectives')
def add(file):
    """Add objectives interactively or from a file"""
    data = load_objectives()
    
    if not data['created_at']:
        data['created_at'] = datetime.now().isoformat()

    if file:
        # Add objectives from file
        try:
            with open(file, 'r') as f:
                file_data = yaml.safe_load(f)
                
            if not isinstance(file_data, list):
                click.echo("Error: File must contain a list of objectives")
                return

            for obj in file_data:
                if not all(k in obj for k in ('title', 'description', 'priority')):
                    click.echo("Error: Each objective must have title, description, and priority")
                    return
                if obj['priority'].lower() not in ['high', 'medium', 'low']:
                    click.echo("Error: Priority must be high, medium, or low")
                    return

                new_objective = {
                    "title": obj['title'],
                    "description": obj['description'],
                    "priority": obj['priority'].lower(),
                    "added_at": datetime.now().isoformat()
                }
                data['objectives'].append(new_objective)

            click.echo(f"Added {len(file_data)} objectives from file")

        except yaml.YAMLError:
            click.echo("Error: Invalid YAML file")
            return
        except Exception as e:
            click.echo(f"Error reading file: {str(e)}")
            return
    else:
        # Interactive input mode
        while True:
            title = click.prompt('Objective title (or :done to finish)')
            
            if title.lower() == ':done':
                break

            description = click.prompt('Description')
            priority = click.prompt(
                'Priority level',
                type=click.Choice(['high', 'medium', 'low'], case_sensitive=False)
            )

            new_objective = {
                "title": title,
                "description": description,
                "priority": priority.lower(),
                "added_at": datetime.now().isoformat()
            }

            data['objectives'].append(new_objective)
            click.echo(f"\nObjective '{title}' added successfully!")
            
            if not click.confirm('\nAdd another objective?'):
                break

    data['updated_at'] = datetime.now().isoformat()
    save_objectives(data)
    click.echo("\nAll objectives have been saved!")

@objectives.command()
@click.argument('index', type=int)
def remove(index):
    """Remove an objective by its index"""
    data = load_objectives()
    
    if not data['objectives']:
        click.echo("No objectives to remove.")
        return
    
    try:
        idx = index - 1  # Convert to 0-based index
        removed = data['objectives'].pop(idx)
        data['updated_at'] = datetime.now().isoformat()
        save_objectives(data)
        click.echo(f"\nRemoved objective: {removed['title']}")
    except IndexError:
        click.echo(f"Error: No objective found at index {index}")

@objectives.command()
def clear():
    """Remove all objectives"""
    if not click.confirm("Are you sure you want to remove all objectives?"):
        click.echo("Operation cancelled.")
        return
    
    if os.path.exists(OBJECTIVES_FILE):
        os.remove(OBJECTIVES_FILE)
        click.echo("All objectives have been removed.")
    else:
        click.echo("No objectives file found.") 