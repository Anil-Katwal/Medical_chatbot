import os
from pathlib import Path  
import logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]:%(message)s:')
list_of_files=[
    "src/__init__.py",
    "src/helper.py",
    "src/prompt.py"
    ".env",
    "setup.py",
    "app.py",
    "research/trials.ipynb"
]
for filepath in list_of_files:
    file_path = Path(filepath)
    dir_path = file_path.parent

    # Create directory if it doesn't exist
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {dir_path}")

    # Create file if it doesn't exist or is empty
    if not file_path.exists() or file_path.stat().st_size == 0:
        file_path.touch()
        logging.info(f"Created file: {file_path}")
    else:
        logging.info(f"File already exists: {file_path}")