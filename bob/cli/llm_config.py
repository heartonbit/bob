import click
import json
import os
from pathlib import Path

DEFAULT_LLM_CONFIG = {
    "max_test_retries": 3,
    "ai_provider": "openai",
    "providers": {
        "openai": {
            "model": "gpt-4",
            "api_key": ""
        },
        "ollama": {
            "model": "llama2",
            "api_key": "",
            "ollama_base_url": "http://localhost:11434"
        },
        "anthropic": {
            "model": "claude-3-sonnet",
            "api_key": ""
        },
        "groq": {
            "model": "mixtral-8x7b-32768",
            "api_key": ""
        }
    }
}

def get_config_path():
    """Get the path to the LLM config file"""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'llm_config.json')

def load_llm_config():
    """Load LLM configuration from llm_config.json"""
    config_path = get_config_path()
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_LLM_CONFIG.copy()
    except Exception as e:
        click.echo(f"Error loading LLM config: {str(e)}")
        return DEFAULT_LLM_CONFIG.copy()

def save_llm_config(config):
    """Save LLM configuration to llm_config.json"""
    config_path = get_config_path()
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        click.echo(f"Error saving LLM config: {str(e)}")
        return False

@click.group()
def llm():
    """Manage LLM configuration"""
    pass

@llm.command()
def init():
    """Initialize LLM configuration with defaults"""
    if save_llm_config(DEFAULT_LLM_CONFIG):
        click.echo("LLM configuration initialized with defaults")
    else:
        click.echo("Failed to initialize LLM configuration")

@llm.command()
@click.argument('provider')
@click.argument('key')
@click.argument('value')
def set(provider, key, value):
    """Set a configuration value for a provider"""
    config = load_llm_config()
    
    if provider not in config['providers']:
        click.echo(f"Unknown provider: {provider}")
        return
    
    if key not in config['providers'][provider]:
        click.echo(f"Unknown configuration key: {key}")
        return
    
    config['providers'][provider][key] = value
    if save_llm_config(config):
        click.echo(f"Updated {provider}.{key} = {value}")
    else:
        click.echo("Failed to save configuration")

@llm.command()
@click.argument('provider', required=False)
def get(provider):
    """Get current LLM configuration"""
    config = load_llm_config()
    
    if provider:
        if provider not in config['providers']:
            click.echo(f"Unknown provider: {provider}")
            return
        click.echo(f"\n{provider} configuration:")
        for key, value in config['providers'][provider].items():
            # Mask API keys for security
            if key == 'api_key':
                value = value[:8] + '...' if value else ''
            click.echo(f"  {key}: {value}")
    else:
        click.echo("\nCurrent configuration:")
        click.echo(f"Active provider: {config['ai_provider']}")
        click.echo(f"Max test retries: {config['max_test_retries']}")
        click.echo("\nProviders:")
        for provider, settings in config['providers'].items():
            click.echo(f"\n{provider}:")
            for key, value in settings.items():
                # Mask API keys for security
                if key == 'api_key':
                    value = value[:8] + '...' if value else ''
                click.echo(f"  {key}: {value}")

@llm.command()
@click.argument('provider')
def use(provider):
    """Set the active LLM provider"""
    config = load_llm_config()
    
    if provider not in config['providers']:
        click.echo(f"Unknown provider: {provider}")
        return
    
    config['ai_provider'] = provider
    if save_llm_config(config):
        click.echo(f"Now using {provider} as the active provider")
    else:
        click.echo("Failed to update active provider")

@llm.command()
def test():
    """Test the current LLM configuration"""
    config = load_llm_config()
    provider = config['ai_provider']
    provider_config = config['providers'][provider]
    
    click.echo(f"Testing {provider} configuration...")
    
    # Basic validation
    if not provider_config.get('api_key'):
        click.echo("Error: API key not configured")
        return
    
    if not provider_config.get('model'):
        click.echo("Error: Model not configured")
        return
    
    if provider == 'ollama':
        if not provider_config.get('ollama_base_url'):
            click.echo("Error: Ollama base URL not configured")
            return
    
    click.echo("Configuration appears valid")
    click.echo("Use 'bob chat' to test actual API connectivity") 