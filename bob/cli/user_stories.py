import click
import yaml
import os
from datetime import datetime
from .chat import AIProvider
from .objectives import load_objectives
from .config import load_config, DEFAULT_CONFIG

USERSTORIES_FILE = 'bob_userstories.yaml'

def load_user_stories():
    """Load existing user stories from file"""
    if os.path.exists(USERSTORIES_FILE):
        try:
            with open(USERSTORIES_FILE, 'r') as f:
                return yaml.safe_load(f) or {"user_stories": [], "created_at": "", "updated_at": ""}
        except yaml.YAMLError:
            return {"user_stories": [], "created_at": "", "updated_at": ""}
    return {"user_stories": [], "created_at": "", "updated_at": ""}

def represent_str_multiline(dumper, data):
    """Custom representer for multiline strings"""
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def save_user_stories(stories_data):
    """Save user stories to file with multiline format"""
    yaml.add_representer(str, represent_str_multiline)
    with open(USERSTORIES_FILE, 'w') as f:
        yaml.dump(stories_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

@click.command()
@click.option('--interactive/--no-interactive', default=True, help='Enable/disable interactive mode')
def user_stories(interactive):
    """Generate user stories based on completed objectives"""
    try:
        config = load_config()
    except click.Abort:
        config = DEFAULT_CONFIG
        
    ai_model = config.get('ai_model', 'chatgpt')
    ai_provider = AIProvider(ai_model)
    
    try:
        with click.progressbar(length=1, label='Loading objectives') as bar:
            data = load_objectives()
            objectives_list = data.get('objectives', [])
            bar.update(1)
        
        if not objectives_list:
            click.echo("No objectives found.")
            return
            
    except Exception as e:
        click.echo(f"Error loading objectives: {str(e)}")
        return

    # Create context from objectives
    objectives_context = "Here are the objectives:\n"
    for idx, obj in enumerate(objectives_list, 1):
        title = obj.get('title', 'Untitled')
        description = obj.get('description', 'No description')
        objectives_context += f"{idx}. {title}: {description}\n"
    
    prompt = (
        "You are a product manager helping to create user stories from objectives. "
        "Each user story should follow the format: 'As a [type of user], I want [goal] so that [benefit]'.\n\n"
        f"{objectives_context}\n"
        "Please generate user stories based on these objectives. "
        "Focus on the value delivered to different types of users. "
        "Return the user stories as a numbered list."
    )
    
    with click.progressbar(length=1, label='Generating user stories') as bar:
        response = ai_provider.get_response(prompt)
        bar.update(1)
    
    click.echo("\nGenerated User Stories:")
    click.echo(response)
    
    # Load existing user stories or create new structure
    stories_data = load_user_stories()
    if not stories_data['created_at']:
        stories_data['created_at'] = datetime.now().isoformat()
    
    # Create new user stories entry
    new_stories = {
        "generated_at": datetime.now().isoformat(),
        "objectives_snapshot": objectives_list,
        "stories": response,
        "refined_stories": []
    }
    
    if interactive:
        while click.confirm("\nWould you like to refine these user stories?"):
            refinement = click.prompt("What would you like to clarify or modify?")
            with click.progressbar(length=1, label='Refining user stories') as bar:
                response = ai_provider.get_response(
                    f"Previous user stories:\n{response}\n\nRefine based on this feedback: {refinement}"
                )
                bar.update(1)
            click.echo("\nUpdated User Stories:")
            click.echo(response)
            new_stories["refined_stories"].append({
                "refinement_prompt": refinement,
                "refined_result": response,
                "refined_at": datetime.now().isoformat()
            })
    
    # Add new stories to the data
    stories_data['user_stories'].append(new_stories)
    stories_data['updated_at'] = datetime.now().isoformat()
    
    # Save to file
    with click.progressbar(length=1, label='Saving user stories') as bar:
        save_user_stories(stories_data)
        bar.update(1)
    
    click.echo(f"\nUser stories have been saved to {USERSTORIES_FILE}")
    click.echo("\nNote: You can manually edit the user stories in the following ways:")
    click.echo("1. Edit the YAML file directly: " + os.path.abspath(USERSTORIES_FILE))
    click.echo("2. The file structure is:")
    click.echo("   - user_stories: List of all generated stories")
    click.echo("     - generated_at: Timestamp of generation")
    click.echo("     - objectives_snapshot: Objectives used for generation")
    click.echo("     - stories: The generated user stories")
    click.echo("     - refined_stories: List of any refinements made")
    click.echo("3. Feel free to modify the stories or add new ones while maintaining the YAML structure")
    click.echo("4. You can also use the interactive refinement option to let AI help with modifications") 