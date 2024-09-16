import openai
import json
import os
import re
import tempfile
import subprocess
from openai import OpenAI
import traceback
from app import globals, globals_mut, inference, log
from app import utils as apputils
from app.api.manage import ProjectApiManager
from app.model import common
from app.model.register import register_all_models
from app.post_process import (
    extract_organize_and_form_input,
    get_final_patch_path,
    organize_and_form_input,
    reextract_organize_and_form_inputs,
)
from app.raw_tasks import RawGithubTask, RawLocalTask, RawSweTask, RawTask
from app.task import Task


def generate_test_code(task: RawTask) -> str:
    """
    Generate test code for a task using GPT-4.
    """
    # Prepare the prompt for GPT-4
    setup_info = task.setup_info
    task_info = task.task_info
    prompt = generate_reproduce_prompt(setup_info, task_info)

    # Define your OpenAI API key
    api_key = os.getenv('OPENAI_KEY')
    
    # Get the generated instructions from GPT-4
    generated_code = get_reproduce_instruction(prompt, api_key)
    
    return generated_code

def extract_code_block(text: str) -> str:
    """
    Extract the actual code block from the provided text.
    Assumes that code blocks are surrounded by triple backticks (```).
    """
    # Regular expression to match code blocks
    match = re.search(r'```(python|bash)?\n(.*?)\n```', text, re.DOTALL)
    if match:
        return match.group(2).strip()  # Extract the code part
    else:
        return text.strip()  # If no code block found, return text as-is

def run_test_code(text: str) -> str:
    """
    Extract and execute the code from the provided text.
    Determines if the extracted code is Python or Shell script and executes it accordingly.
    Returns traceback as a string if execution fails, otherwise returns None.
    """

    code = extract_code_block(text)
    temp_file = None

    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.sh') as temp_file:
            temp_file.write(code.encode())
            temp_file.close()
            
        # Execute the temporary file using os.system
        result = os.system(f'bash {temp_file.name}')
            
        if result != 0:
            raise Exception(f'Shell script execution failed with exit code {result}')
            
        print("Script executed successfully")
        return None
    
    except Exception as e:
        # Return the traceback as a string if execution fails
        return traceback.format_exc()
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)

def generate_reproduce_prompt(setup_info: dict, task_info: dict) -> str:
    """
    Generate a prompt for GPT-4 to create test instructions.
    """
    prompt = (
        "You are a highly skilled assistant tasked with reproducing a software engineering task. "
        "Here is the task information you need to use:\n\n"
        f"Setup Information:\n{json.dumps(setup_info, indent=2)}\n\n"
        f"Task Information:\n{json.dumps(task_info, indent=2)}\n\n"
        "Based on the above information, please provide a detailed and executable code snippet "
        "that can reproduce this task. Include all necessary setup commands, configurations, and code to run."
        "Please output only the executable code without other prompts, consolidating the code snippets into one shell file."
        "Remember output pure code snippets."
    )
    return prompt



def get_reproduce_instruction(prompt: str, api_key: str) -> str:
    """
    Get the reproduction instructions from GPT-4.
    """
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1500,  # Adjust as needed
        temperature=0.5
    )
    
    result = response.choices[0].message.content
    return result


