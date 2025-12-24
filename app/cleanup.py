import os
import shutil
from pathlib import Path

def clean_project_artifacts(root_dir):
    """
    Cleans up project artifacts including __pycache__, .idea, .DS_Store,
    build directories, and log files.
    
    Args:
        root_dir (str): The root directory of the project.
    """
    root = Path(root_dir)
    
    if not root.exists():
        print(f"Root directory {root_dir} does not exist.")
        return

    # 1. Remove __pycache__ directories recursively
    print("Cleaning __pycache__ directories...")
    for p in root.rglob('__pycache__'):
        if p.is_dir():
            try:
                shutil.rmtree(p)
                print(f"Removed: {p}")
            except Exception as e:
                print(f"Error removing {p}: {e}")

    # 2. Remove .idea directory
    idea_dir = root / '.idea'
    if idea_dir.exists() and idea_dir.is_dir():
        try:
            shutil.rmtree(idea_dir)
            print(f"Removed: {idea_dir}")
        except Exception as e:
            print(f"Error removing {idea_dir}: {e}")

    # 3. Remove .DS_Store files recursively
    print("Cleaning .DS_Store files...")
    for p in root.rglob('.DS_Store'):
        if p.is_file():
            try:
                os.remove(p)
                print(f"Removed: {p}")
            except Exception as e:
                print(f"Error removing {p}: {e}")

    # 4. Remove build artifacts (build, dist)
    for artifact in ['build', 'dist']:
        artifact_path = root / artifact
        if artifact_path.exists() and artifact_path.is_dir():
            try:
                shutil.rmtree(artifact_path)
                print(f"Removed: {artifact_path}")
            except Exception as e:
                print(f"Error removing {artifact_path}: {e}")
                
    # 5. Remove app.log
    log_file = root / 'app.log'
    if log_file.exists():
        try:
            os.remove(log_file)
            print(f"Removed: {log_file}")
        except Exception as e:
            print(f"Error removing {log_file}: {e}")

    print("Cleanup complete.")
