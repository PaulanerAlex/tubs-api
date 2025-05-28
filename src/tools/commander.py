# TODO: rename file

import subprocess
import sys
import os

def run_shell_command(command):
    """
    Run a shell command and return the output.
    """
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # TODO: change following to logger
        print(f"Command '{command}' failed with error: {e.stderr.strip()}")
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