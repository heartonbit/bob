import click
import logging
from .config import load_config, DEFAULT_CONFIG
from .chat import AIProvider
from ..core.test_generator import TestGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

@click.group()
def build():
    """Build commands"""
    pass

@build.command()
@click.argument('target', required=False)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def test(target, verbose):
    """Generate test code based on design"""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        logger.info("Loading configuration...")
        config = load_config()
    except click.Abort:
        logger.warning("Using default configuration")
        config = DEFAULT_CONFIG

    # Create AI provider
    logger.info("Initializing AI provider...")
    ai_provider = AIProvider()
    logger.debug(f"Using AI provider: {ai_provider.provider} with model: {ai_provider.model_name}")
    
    click.echo("Loading design ", nl=False)
    with click.progressbar(length=1) as bar:
        logger.info("Creating test generator...")
        test_generator = TestGenerator(config)
        bar.update(1)
    
    click.echo("Generating test code ", nl=False)
    with click.progressbar(length=1) as bar:
        try:
            logger.info("Starting test code generation...")
            success = test_generator.generate_test_code(target, ai_provider)
            bar.update(1)
            
            if success:
                logger.info("Test code generation completed successfully")
                click.echo("\nTest code generated successfully!")
            else:
                logger.error("Test code generation failed")
                click.echo("\nFailed to generate test code")
                
        except Exception as e:
            logger.error(f"Error during test generation: {str(e)}", exc_info=True)
            click.echo(f"\nError: {str(e)}")
            return

@build.command()
@click.argument('target', required=False)
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def docs(target, verbose):
    """Generate documentation based on design"""
    if verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        logger.info("Loading configuration...")
        config = load_config()
    except click.Abort:
        logger.warning("Using default configuration")
        config = DEFAULT_CONFIG

    # Create AI provider
    logger.info("Initializing AI provider...")
    ai_provider = AIProvider()
    logger.debug(f"Using AI provider: {ai_provider.provider} with model: {ai_provider.model_name}")
    
    click.echo("Loading design ", nl=False)
    with click.progressbar(length=1) as bar:
        logger.info("Creating test generator...")
        test_generator = TestGenerator(config)
        bar.update(1)
    
    click.echo("Generating documentation ", nl=False)
    with click.progressbar(length=1) as bar:
        try:
            logger.info("Starting documentation generation...")
            success = test_generator.generate_docs(target, ai_provider)
            bar.update(1)
            
            if success:
                logger.info("Documentation generation completed successfully")
                click.echo("\nDocumentation generated successfully!")
            else:
                logger.error("Documentation generation failed")
                click.echo("\nFailed to generate documentation")
                
        except Exception as e:
            logger.error(f"Error during documentation generation: {str(e)}", exc_info=True)
            click.echo(f"\nError: {str(e)}")
            return