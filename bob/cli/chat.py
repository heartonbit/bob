import click
import requests
from .llm_config import load_llm_config

class AIProvider:
    def __init__(self, model_name=None):
        self.llm_config = load_llm_config()
        
        # Get provider from config
        self.provider = self.llm_config.get('ai_provider', 'openai')
        
        # Get provider-specific configuration
        provider_config = self.llm_config.get('providers', {}).get(self.provider, {})
        self.api_key = provider_config.get('api_key')
        
        # Use passed model_name if provided, otherwise use from config
        self.model_name = model_name or provider_config.get('model')
        
        if self.provider == 'ollama':
            self.ollama_base_url = provider_config.get('ollama_base_url', 'http://localhost:11434')
        elif self.provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        elif self.provider == 'anthropic':
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        elif self.provider == 'groq':
            from groq import Groq
            self.client = Groq(api_key=self.api_key)

    def list_models(self):
        """List available models from provider"""
        try:
            if self.provider == 'ollama':
                response = requests.get(f"{self.ollama_base_url}/api/tags")
                response.raise_for_status()
                return response.json().get('models', [])
            # Add model listing for other providers if needed
            return []
        except requests.exceptions.RequestException as e:
            click.echo(f"API Error: {str(e)}")
            if hasattr(e.response, 'text'):
                click.echo(f"Response details: {e.response.text}")
            return []

    def get_response(self, prompt):
        """Get response from AI model"""
        try:
            if self.provider == 'ollama':
                response = requests.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7
                        }
                    }
                )
                response.raise_for_status()
                return response.json().get('response', '')
                
            elif self.provider == 'openai':
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}]
                )
                return completion.choices[0].message.content
                
            elif self.provider == 'anthropic':
                message = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content
                
            elif self.provider == 'groq':
                chat_completion = self.client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=self.model_name,
                )
                return chat_completion.choices[0].message.content
                
            else:
                click.echo(f"Unsupported AI provider: {self.provider}")
                return ""
                
        except requests.exceptions.RequestException as e:
            click.echo(f"API Error: {str(e)}")
            if hasattr(e.response, 'text'):
                click.echo(f"Response details: {e.response.text}")
            return ""
        except Exception as e:
            click.echo(f"Error: {str(e)}")
            return ""

@click.command()
@click.argument('message', required=False)
@click.option('--list-models', is_flag=True, help='List available models')
def chat(message, list_models):
    """Chat with AI assistant. If no message is provided, starts interactive mode."""
    ai_provider = AIProvider()
    provider_config = ai_provider.llm_config.get('providers', {}).get(ai_provider.provider, {})
    model_name = provider_config.get('model', 'unknown')
    
    if list_models:
        models = ai_provider.list_models()
        if models:
            click.echo("Available models:")
            for model in models:
                click.echo(f"- {model}")
        else:
            click.echo("No models available or unable to fetch models")
        return
    
    if message:
        # Single message mode
        response = ai_provider.get_response(message)
        click.echo(response)
    else:
        # Interactive mode
        click.echo(f"Starting chat with {model_name} ({ai_provider.provider})")
        click.echo("Type 'exit' or 'quit' to end")
        click.echo("----------------------------------------")
        
        while True:
            # Get user input
            message = click.prompt("\nYou", prompt_suffix="> ")
            
            # Check for exit command
            if message.lower() in ['exit', 'quit']:
                click.echo("\nEnding chat session.")
                break
                
            # Get and display AI response
            click.echo("\nAI", nl=False)
            with click.progressbar(length=1, label='thinking') as bar:
                response = ai_provider.get_response(message)
                bar.update(1)
            click.echo("> " + response)