# TODO: rename file

import subprocess


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