import click
import os
import requests
from .config import load_config, DEFAULT_CONFIG

class AIProvider:
    def __init__(self, model_name):
        self.model_name = model_name
        
    def get_response(self, prompt):
        if self.model_name.startswith('gpt'):
            return self._call_openai(prompt)
        elif self.model_name.startswith('claude'):
            return self._call_anthropic(prompt)
        elif self.model_name == 'llama3':
            return self._call_ollama(prompt)
        elif self.model_name.startswith('groq'):
            return self._call_groq(prompt)
        else:
            return self._call_openai(prompt)  # default to OpenAI
    
    def _call_openai(self, prompt):
        try:
            from openai import OpenAI
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return "Error: OPENAI_API_KEY environment variable not set"
            
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model_name if self.model_name != 'chatgpt' else 'gpt-3.5-turbo',
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except ImportError:
            return "Error: OpenAI package not installed. Run 'pip install openai'"
        except Exception as e:
            return f"OpenAI API Error: {str(e)}"
    
    def _call_anthropic(self, prompt):
        try:
            import anthropic
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return "Error: ANTHROPIC_API_KEY environment variable not set"
            
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model=self.model_name,  
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            return response.content
        except ImportError:
            return "Error: Anthropic package not installed. Run 'pip install anthropic'"
        except Exception as e:
            return f"Anthropic API Error: {str(e)}"
    
    def _call_ollama(self, prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model_name,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False  # Disable streaming to get a single response
                }
            )
            
            if response.status_code == 200:
                try:
                    return response.json()['message']['content']
                except KeyError:
                    return "Error: Unexpected response format from Ollama"
            else:
                return f"Ollama API Error: {response.text}"
                
        except requests.exceptions.ConnectionError:
            return "Error: Could not connect to Ollama. Make sure Ollama is running (http://localhost:11434)"
        except Exception as e:
            return f"Ollama Error: {str(e)}"

    def _call_groq(self, prompt):
        try:
            import groq
            api_key = os.getenv('GROQ_API_KEY')
            if not api_key:
                return "Error: GROQ_API_KEY environment variable not set"
            
            client = groq.Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=self.model_name if self.model_name != 'groq' else 'mixtral-8x7b-32768',
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except ImportError:
            return "Error: Groq package not installed. Run 'pip install groq'"
        except Exception as e:
            return f"Groq API Error: {str(e)}"

@click.command()
def chat():
    """Test chat with the configured AI model"""
    try:
        try:
            config = load_config()
        except click.Abort:
            # If config file doesn't exist, use default configuration
            config = DEFAULT_CONFIG
            
        ai_model = config.get('ai_model', 'chatgpt')
        ai_provider = AIProvider(ai_model)
        
        click.echo(f"\nTesting chat with {ai_model}...")
        click.echo("Type ':exit' to end the conversation\n")
        
        while True:
            # Get user input
            user_input = click.prompt("You")
            
            if user_input.lower() == ':exit':
                break
                
            # Get response from AI model
            response = ai_provider.get_response(user_input)
            click.echo(f"\nAI: {response}\n")
            
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort() 