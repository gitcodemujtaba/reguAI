"""
Deploy ReguAI to Hugging Face Spaces.
Uploads code, schemas, SHACL shapes, datasets, and app.py to gitmodelmujtaba/reguai-engine.
"""

import os
from pathlib import Path
from huggingface_hub import HfApi

PROJECT_DIR = Path(__file__).resolve().parent

def deploy():
    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/reguai-engine"
    
    print(f"Creating / verifying Hugging Face Space: {repo_id}...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            exist_ok=True,
            private=False,
        )
        print(f"Space {repo_id} created or verified.")
    except Exception as e:
        print(f"Note on create_repo: {e}")

    print(f"Uploading files from {PROJECT_DIR} to Space {repo_id}...")
    
    ignore_patterns = [
        ".venv/**",
        ".git/**",
        ".pytest_cache/**",
        "**/__pycache__/**",
        "*.pyc",
        "deploy_to_hf.py",
        "portfolio_card_snippet.ts",
    ]

    commit_info = api.upload_folder(
        folder_path=str(PROJECT_DIR),
        repo_id=repo_id,
        repo_type="space",
        commit_message="Deploy ReguAI: Neuro-Symbolic AI GRC & Automated Conformity Assessment Engine",
        ignore_patterns=ignore_patterns,
    )

    space_url = f"https://huggingface.co/spaces/{repo_id}"
    print(f"\nSuccessfully deployed to Hugging Face Spaces!")
    print(f"URL: {space_url}")
    print(f"Commit: {commit_info}")

if __name__ == "__main__":
    deploy()
