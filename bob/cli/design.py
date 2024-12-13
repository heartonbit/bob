import click
import yaml
import os
from datetime import datetime
from .chat import AIProvider
from .objectives import load_objectives
from .user_stories import load_user_stories
from .config import load_config, DEFAULT_CONFIG

DESIGN_FILE = 'bob_design.yaml'

def load_design():
    """Load existing design from file"""
    if os.path.exists(DESIGN_FILE):
        try:
            with open(DESIGN_FILE, 'r') as f:
                return yaml.safe_load(f) or {"designs": [], "created_at": "", "updated_at": ""}
        except yaml.YAMLError:
            return {"designs": [], "created_at": "", "updated_at": ""}
    return {"designs": [], "created_at": "", "updated_at": ""}

def represent_str_multiline(dumper, data):
    """Custom representer for multiline strings"""
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

def save_design(design_data):
    """Save design to file with multiline format"""
    yaml.add_representer(str, represent_str_multiline)
    with open(DESIGN_FILE, 'w') as f:
        yaml.dump(design_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, indent=2)

@click.command()
@click.option('--interactive/--no-interactive', default=True, help='Enable/disable interactive mode')
def design(interactive):
    """Design classes and functions based on objectives and user stories"""
    try:
        config = load_config()
    except click.Abort:
        config = DEFAULT_CONFIG
        
    ai_model = config.get('ai_model', 'chatgpt')
    ai_provider = AIProvider(ai_model)
    
    try:
        with click.progressbar(length=2, label='Loading project data') as bar:
            objectives_data = load_objectives()
            objectives_list = objectives_data.get('objectives', [])
            bar.update(1)
            
            stories_data = load_user_stories()
            user_stories_list = stories_data.get('user_stories', [])
            bar.update(1)
        
        if not objectives_list:
            click.echo("No objectives found. Please add objectives first.")
            return
            
        if not user_stories_list:
            click.echo("No user stories found. Please generate user stories first.")
            return
            
    except Exception as e:
        click.echo(f"Error loading data: {str(e)}")
        return

    # Create context from objectives and user stories
    context = "Here are the project objectives:\n"
    for idx, obj in enumerate(objectives_list, 1):
        title = obj.get('title', 'Untitled')
        description = obj.get('description', 'No description')
        context += f"{idx}. {title}: {description}\n"
    
    context += "\nHere are the user stories:\n"
    for story_group in user_stories_list:
        stories = story_group.get('stories', '')
        context += f"{stories}\n"
        # Include any refinements
        for refinement in story_group.get('refined_stories', []):
            context += f"Refined version:\n{refinement.get('refined_result', '')}\n"
    
    prompt = (
        "You are a software architect helping to design classes and their functions. "
        "Based on the objectives and user stories, propose a clean and maintainable design.\n\n"
        f"{context}\n"
        "Please provide:\n"
        "1. A list of proposed classes with their responsibilities\n"
        "2. For each class, list the key methods/functions with:\n"
        "   - Method signature\n"
        "   - Brief description\n"
        "   - Parameters and return types\n"
        "   - Any important notes about implementation\n"
        "3. Key relationships between classes\n"
        "4. Any design patterns that would be beneficial\n\n"
        "Focus on creating a modular and extensible design that fulfills the objectives and user stories."
    )
    
    with click.progressbar(length=1, label='Generating design') as bar:
        response = ai_provider.get_response(prompt)
        bar.update(1)
    
    click.echo("\nGenerated Design:")
    click.echo(response)
    
    # Load existing design or create new structure
    design_data = load_design()
    if not design_data['created_at']:
        design_data['created_at'] = datetime.now().isoformat()
    
    # Create new design entry
    new_design = {
        "generated_at": datetime.now().isoformat(),
        "objectives_snapshot": objectives_list,
        "user_stories_snapshot": [story.get('stories') for story in user_stories_list],
        "design": response,
        "refined_designs": []
    }
    
    if interactive:
        while click.confirm("\nWould you like to refine this design?"):
            refinement = click.prompt("What would you like to clarify or modify?")
            with click.progressbar(length=1, label='Refining design') as bar:
                response = ai_provider.get_response(
                    f"Previous design:\n{response}\n\nRefine based on this feedback: {refinement}"
                )
                bar.update(1)
            click.echo("\nUpdated Design:")
            click.echo(response)
            new_design["refined_designs"].append({
                "refinement_prompt": refinement,
                "refined_result": response,
                "refined_at": datetime.now().isoformat()
            })
    
    # Add new design to the data
    design_data['designs'].append(new_design)
    design_data['updated_at'] = datetime.now().isoformat()
    
    # Save to file
    with click.progressbar(length=1, label='Saving design') as bar:
        save_design(design_data)
        bar.update(1)
    
    click.echo(f"\nDesign has been saved to {DESIGN_FILE}")
    click.echo("\nNote: You can manually edit the design in the following ways:")
    click.echo("1. Edit the YAML file directly: " + os.path.abspath(DESIGN_FILE))
    click.echo("2. The file structure is:")
    click.echo("   - designs: List of all generated designs")
    click.echo("     - generated_at: Timestamp of generation")
    click.echo("     - objectives_snapshot: Objectives used for generation")
    click.echo("     - user_stories_snapshot: User stories used for generation")
    click.echo("     - design: The generated design")
    click.echo("     - refined_designs: List of any refinements made")
    click.echo("3. Feel free to modify the design while maintaining the YAML structure")
    click.echo("4. You can also use the interactive refinement option to let AI help with modifications") 