import os
from langchain_core.prompts import ChatPromptTemplate
from langfuse import Langfuse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import re

# Load environment variables from .env if present
load_dotenv()

# Setup Langfuse client from env vars
langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
langfuse_host = os.getenv("LANGFUSE_HOST")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Debug: Print credential status (without exposing actual keys)
print("=== Langfuse Configuration Debug ===")
print(f"LANGFUSE_PUBLIC_KEY: {'✓ Set' if langfuse_public_key else '✗ Not set'}")
print(f"LANGFUSE_SECRET_KEY: {'✓ Set' if langfuse_secret_key else '✗ Not set'}")
print(f"LANGFUSE_HOST: {langfuse_host if langfuse_host else '✗ Not set'}")
print(f"OPENAI_API_KEY: {'✓ Set' if openai_api_key else '✗ Not set'}")
print("=====================================")

# Validate credentials before initializing Langfuse
if not langfuse_public_key or not langfuse_secret_key:
    raise ValueError("Missing Langfuse credentials. Please set LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY environment variables.")

if not langfuse_host:
    langfuse_host = "https://cloud.langfuse.com"  # Default to cloud Langfuse
    print(f"Using default Langfuse host: {langfuse_host}")

langfuse = Langfuse(
    public_key=langfuse_public_key,
    secret_key=langfuse_secret_key,
    host=langfuse_host
)

def convert_langfuse_to_langchain_format(langfuse_prompt):
    """
    Convert Langfuse's {{variable}} format to LangChain's {variable} format
    """
    # Replace {{variable}} with {variable}
    converted = re.sub(r'\{\{([^}]+)\}\}', r'{\1}', langfuse_prompt)
    return converted

def test_langfuse_connection():
    """Test the Langfuse connection by trying to fetch a simple prompt"""
    try:
        print("Testing Langfuse connection...")
        # Try to get a simple prompt to test the connection
        prompt_obj = langfuse.get_prompt("Generate pair exercise")
        print("✅ Langfuse connection successful!")
        
        # Debug info
        print(f"Original prompt (first 100 chars): {repr(prompt_obj.prompt[:100])}")
        converted = convert_langfuse_to_langchain_format(prompt_obj.prompt)
        print(f"Converted prompt (first 100 chars): {repr(converted[:100])}")
        
        return True
    except Exception as e:
        print(f"❌ Langfuse connection failed: {e}")
        return False

def generate_pair_exercice(target_phone, confused_phones, target_language, native_language):
    try:
        prompt_obj = langfuse.get_prompt("Generate pair exercise")
        # Extract the actual prompt text and convert format - THIS WAS MISSING!
        prompt_text = convert_langfuse_to_langchain_format(prompt_obj.prompt)  # ✅ FIXED: Apply conversion
        
        print(f"Original Langfuse prompt (first 200 chars): {repr(prompt_obj.prompt[:200])}")
        print(f"Converted prompt (first 200 chars): {repr(prompt_text[:200])}")
        
        input_variables = {
            "target_phone": target_phone,
            "confused_phones": confused_phones,
            "target_language": target_language,
            "native_language": native_language
        }
        
        # Debug: Show variables
        langchain_vars = re.findall(r'\{([^}]+)\}', prompt_text)
        print(f"Variables expected by LangChain: {langchain_vars}")
        print(f"Variables provided: {list(input_variables.keys())}")
        
        # Check for issues
        unique_vars = list(set(langchain_vars))
        print(f"Unique variables expected: {unique_vars}")
        
        missing = set(unique_vars) - set(input_variables.keys())
        extra = set(input_variables.keys()) - set(unique_vars)
        
        if missing:
            print(f"⚠️ Missing variables: {missing}")
        if extra:
            print(f"⚠️ Extra variables: {extra}")
        
        response = run_langfuse_prompt(prompt_text, input_variables, "gpt-3.5-turbo", temperature=0.2)
        return response
    except Exception as e:
        print(f"Error while fetching prompt 'Generate pair exercise': {e}")
        raise

def run_langfuse_prompt(prompt_template, input_variables, model, temperature=0.2):
    """
    Given a LangChain prompt template, a dict of input_variables, and an LLM name,
    format the prompt, execute it with OpenAI via LangChain, and return the LLM response.

    Args:
        prompt_template (str): The prompt string with variable placeholders (e.g., "Hello, {name}")
        input_variables (dict): Dict mapping variable names to user input for the prompt
        model (str): Name of the LLM to use (e.g., "gpt-3.5-turbo")
        temperature (float): Temperature parameter for LLM generation

    Returns:
        str: The AI response content
    """

    try:
        # Build the prompt with LangChain using the provided template and variables
        prompt = ChatPromptTemplate.from_template(prompt_template)
        messages = prompt.format_messages(**input_variables)
        print("✅ Prompt formatting successful!")
    except Exception as e:
        print(f"❌ Prompt formatting failed: {e}")
        template_vars = re.findall(r'\{([^}]+)\}', prompt_template)
        provided_vars = list(input_variables.keys())
        print(f"Template expects: {template_vars}")
        print(f"You provided: {provided_vars}")
        missing = set(template_vars) - set(provided_vars)
        extra = set(provided_vars) - set(template_vars)
        if missing:
            print(f"Missing variables: {missing}")
        if extra:
            print(f"Extra variables: {extra}")
        
        # Debug: Show problematic parts of the template
        print(f"Template content preview:")
        print(repr(prompt_template[:500]))
        raise

    try:
        # Initialize the LLM via LangChain with OpenAI
        llm = ChatOpenAI(model=model, temperature=temperature, openai_api_key=openai_api_key)
        # Generate the response by passing messages
        response = llm.invoke(messages)
        print("✅ OpenAI LLM generated response.")
        return response.content
    except Exception as e:
        print(f"❌ Error during OpenAI LLM generation: {e}")
        raise


if __name__ == "__main__":
    # Test connection first
    if not test_langfuse_connection():
        print("\n🔧 Troubleshooting steps:")
        print("1. Check your Langfuse credentials in your environment variables")
        print("2. Verify you're using the correct host URL")
        print("3. Make sure your credentials are for the right environment (dev/prod)")
        print("4. Check if your credentials have expired")
        print("5. Verify the prompt name 'Generate pair exercise' exists in your Langfuse project")
        exit(1)
    
    target_phone = "b"
    confused_phones = ["p", "b"]
    target_language = "French"
    native_language = "English"
    
    try:
        response = generate_pair_exercice(target_phone, confused_phones, target_language, native_language)
        print("\n=== Response ===")
        print(response)
    except Exception as e:
        print(f"\n❌ Final error: {e}")