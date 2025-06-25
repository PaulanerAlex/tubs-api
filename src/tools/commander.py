# TODO: rename file

import subprocess
import sys
import os
from tools.logger import Logger

def run_shell_command(command, capture_exit_code_3=False):
    """
    Run a shell command and return the output.
    """
    log = Logger(__name__)
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        output = result.stdout.strip()
        from config.config import DEBUG_MODE
        if DEBUG_MODE:
            log.debug(f"Command '{command}' executed successfully. output: {output}")
        return output
    except subprocess.CalledProcessError as e:
        if e.returncode == 3 and capture_exit_code_3:
            log.info(f"Command '{command}' executed successfully.")
            return ''
        log.error(f"Command '{command}' failed with error: {e}")
        return None

def restart_program(args=None):
    """
    Restart the current program.
    `args` is a string list of command line arguments to pass to the restarted program.
    """

    if args is None:
        args = sys.argv

    # Get the current Python interpreter
    python = sys.executable

    # Restart the program using the same interpreter and arguments
    os.execv(python, [python] + args)

    # If execv fails, exit the program
    sys.exit(1)