import os
import json
import click

DEFAULT_CONFIG_PATH = 'bob_config.json'

DEFAULT_CONFIG = {
    "ai_model": "chatgpt",
    "max_test_retries": 3
}

def load_config():
    """Load configuration from bob_config.json"""
    if not os.path.exists(DEFAULT_CONFIG_PATH):
        click.echo("No configuration file found. Please run 'bob init' first.", err=True)
        raise click.Abort()
    
    try:
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            config = json.load(f)
            # Ensure default values exist
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except json.JSONDecodeError:
        click.echo("Error: Invalid configuration file format.", err=True)
        raise click.Abort()

def save_config(config):
    """Save configuration to bob_config.json"""
    try:
        with open(DEFAULT_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        click.echo(f"Error saving configuration: {str(e)}", err=True)
        raise click.Abort()

@click.group()
def config():
    """Configure Bob settings"""
    pass

@config.command()
def show():
    """Show current configuration"""
    config = load_config()
    click.echo("\nCurrent Configuration:")
    click.echo("-------------------")
    for key, value in config.items():
        click.echo(f"{key}: {value}")

@config.command()
@click.option('--ai-model', 
              type=click.Choice(['chatgpt', 'gpt-4', 'gpt-3.5-turbo', 'claude-3.5-sonnet', 'llama3']), 
              help='AI model to use')
@click.option('--max-retries', type=int, help='Maximum number of test retries')
def set(ai_model, max_retries):
    """Set configuration values"""
    config = load_config()
    
    if ai_model is None and max_retries is None:
        click.echo("No configuration values provided. Use --help for usage information.")
        return

    changes_made = False
    
    if ai_model is not None:
        config['ai_model'] = ai_model
        changes_made = True
        click.echo(f"AI model set to: {ai_model}")
    
    if max_retries is not None:
        if max_retries < 1:
            click.echo("Error: max-retries must be at least 1", err=True)
            return
        config['max_test_retries'] = max_retries
        changes_made = True
        click.echo(f"Maximum test retries set to: {max_retries}")
    
    if changes_made:
        save_config(config)
        click.echo("Configuration updated successfully!")

@config.command()
def reset():
    """Reset configuration to default values"""
    if not click.confirm("Are you sure you want to reset all configuration to default values?"):
        click.echo("Reset cancelled.")
        return
    
    config = load_config()
    config.update(DEFAULT_CONFIG)
    save_config(config)
    click.echo("Configuration reset to default values.")