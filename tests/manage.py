#!/usr/bin/env python
import os
import sys

from pathlib import Path


# Add the project directory to the Python system path to enable importing of project modules
sys.path.append(Path(__file__).resolve().parent.parent.__str__())


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
