import os
import yaml
from pathlib import Path

class TestGenerator:
    def __init__(self, config):
        self.config = config
        self.design_file = os.path.join(os.path.dirname(__file__), '..', '..', 'bob_design.yaml')
        self.load_design()

    def load_design(self):
        """Load design from YAML file"""
        try:
            with open(self.design_file, 'r') as f:
                self.design = yaml.safe_load(f)
        except Exception as e:
            raise Exception(f"Failed to load design file: {str(e)}")

    def generate_test_code(self, target, ai_provider):
        """Generate test code based on design"""
        try:
            # Get the latest design
            latest_design = self.design['designs'][-1]
            
            # Extract design details
            objectives = latest_design.get('objectives_snapshot', [])
            user_stories = latest_design.get('user_stories_snapshot', [])
            design_spec = latest_design.get('design', '')
            
            # Prepare prompt for test generation
            prompt = f"""
            Based on the following design information, generate Python test code:

            Objectives:
            {objectives}

            User Stories:
            {user_stories}

            Design Specification:
            {design_spec}

            Please generate comprehensive test cases that cover:
            1. Unit tests for each class and method
            2. Integration tests for key interactions
            3. Edge cases and error handling
            4. Basic functionality tests

            Use pytest framework and follow best practices.
            """
            
            # Get AI response
            test_code = ai_provider.get_response(prompt)
            
            # Save the generated test code
            if test_code:
                tests_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'tests')
                os.makedirs(tests_dir, exist_ok=True)
                
                test_file = os.path.join(tests_dir, 'test_function_builder.py')
                with open(test_file, 'w') as f:
                    f.write(test_code)
                
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to generate test code: {str(e)}")

    def generate_docs(self, target, ai_provider):
        """Generate documentation based on design"""
        try:
            # Get the latest design
            latest_design = self.design['designs'][-1]
            
            # Extract design details
            objectives = latest_design.get('objectives_snapshot', [])
            user_stories = latest_design.get('user_stories_snapshot', [])
            design_spec = latest_design.get('design', '')
            
            # Prepare prompt for documentation generation
            prompt = f"""
            Based on the following design information, generate comprehensive documentation:

            Objectives:
            {objectives}

            User Stories:
            {user_stories}

            Design Specification:
            {design_spec}

            Please generate:
            1. Overview and architecture documentation
            2. API documentation for each class and method
            3. Usage examples
            4. Installation and setup instructions
            5. Troubleshooting guide

            Use Markdown format.
            """
            
            # Get AI response
            docs = ai_provider.get_response(prompt)
            
            # Save the generated documentation
            if docs:
                docs_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs')
                os.makedirs(docs_dir, exist_ok=True)
                
                doc_file = os.path.join(docs_dir, 'function_builder.md')
                with open(doc_file, 'w') as f:
                    f.write(docs)
                
                return True
            
            return False
            
        except Exception as e:
            raise Exception(f"Failed to generate documentation: {str(e)}")