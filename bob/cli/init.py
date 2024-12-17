# bob/cli/init.py

import os
import json
import click
from datetime import datetime

def get_available_providers():
    """Get list of available AI providers from llm_config.json"""
    try:
        with open('llm_config.json', 'r') as f:
            llm_config = json.load(f)
            return list(llm_config.get('providers', {}).keys())
    except:
        return ['ollama']  # Default if config not found

DEFAULT_CONFIG = {
    "project_name": "",
    "created_at": "",
    "version": "0.1.0", 
    "description": "",
    "author": "",
    "max_test_retries": 3,
    "ai_provider": "ollama",
    "language": "python",
    "platform": "linux"
}

DEFAULT_STRUCTURE = [
    "src/",
    "src/__init__.py", 
    "tests/",
    "tests/__init__.py",
    "docs/",
    "requirements.txt",
    "README.md",
    ".gitignore",
    "bob_config.json"
]

def create_directory_structure(base_path, structure):
    """Create the default directory structure for the project."""
    for path in structure:
        full_path = os.path.join(base_path, path)
        if path.endswith('/'):
            os.makedirs(full_path, exist_ok=True)
        else:
            # Create parent directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            # Create empty file
            open(full_path, 'a').close()

def create_gitignore():
    """Create a default .gitignore file."""
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Bob specific
bob_config.json
    """
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())

def create_readme(project_name, description):
    """Create a README.md file with basic project information."""
    readme_content = f"""# {project_name}

{description}

## Installation

bash

pip install -r requirements.txt


## Usage

[Add usage instructions here]

## Development

[Add development instructions here]

## License

[Add license information here]
"""
    with open('README.md', 'w') as f:
        f.write(readme_content)

@click.command()
@click.option('--name', prompt='Project name', help='Name of the project')
@click.option('--description', prompt='Project description', help='Brief description of the project')
@click.option('--author', prompt='Author name', help='Name of the project author')
@click.option('--ai-provider', type=click.Choice(get_available_providers()), prompt='AI provider', help='AI provider to use')
def init(name, description, author, ai_provider):
    """Initialize a new Bob project."""
    
    # Check if directory is empty
    if os.listdir('.'):
        if not click.confirm('Directory is not empty. Continue anyway?'):
            click.echo('Aborted.')
            return

    try:
        # Create project configuration
        config = DEFAULT_CONFIG.copy()
        config.update({
            "project_name": name,
            "description": description,
            "author": author,
            "ai_provider": ai_provider,
            "created_at": datetime.now().isoformat()
        })

        # Create directory structure
        create_directory_structure('.', DEFAULT_STRUCTURE)
        
        # Create bob_config.json
        with open('bob_config.json', 'w') as f:
            json.dump(config, f, indent=4)

        # Create .gitignore
        create_gitignore()
        
        # Create README.md
        create_readme(name, description)
        
        # Create empty requirements.txt
        open('requirements.txt', 'a').close()

        click.echo(f"""
Project '{name}' has been initialized successfully!

Created files and directories:
- Project configuration (bob_config.json)
- Source directory (src/)
- Test directory (tests/)
- Documentation directory (docs/)
- Requirements file (requirements.txt)
- README.md
- .gitignore

Next steps:
1. Define project objectives: bob objectives
2. Create user stories: bob stories
3. Design classes: bob design
        """)

    except Exception as e:
        click.echo(f"Error initializing project: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    init()