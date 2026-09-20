"""
Publish the EU AI Act Normative Triples Benchmark Dataset to Hugging Face Datasets Hub.
Repository: gitmodelmujtaba/eu-ai-act-normative-triples
"""

from pathlib import Path
from huggingface_hub import HfApi

PROJECT_DIR = Path(__file__).resolve().parent
BENCHMARK_DIR = PROJECT_DIR / "data" / "benchmarks"

def deploy_dataset():
    api = HfApi()
    user_info = api.whoami()
    username = user_info["name"]
    repo_id = f"{username}/eu-ai-act-normative-triples"

    print(f"Creating / verifying Hugging Face Dataset: {repo_id}...")
    try:
        api.create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            exist_ok=True,
            private=False,
        )
        print(f"Dataset repo {repo_id} verified.")
    except Exception as e:
        print(f"Note on create_repo: {e}")

    # Preserve generated publication-grade dataset README card if present
    readme_path = BENCHMARK_DIR / "README.md"
    if not readme_path.exists():
        dataset_readme = f"""---
license: cdla-permissive-2.0
task_categories:
- text-classification
- feature-extraction
language:
- en
tags:
- legal
- eu-ai-act
- knowledge-graph
- deontic-logic
size_categories:
- n<1K
---
# EU AI Act Normative Triples
"""
        readme_path.write_text(dataset_readme, encoding="utf-8")

    print(f"Uploading benchmark data to {repo_id}...")
    commit_info = api.upload_folder(
        folder_path=str(BENCHMARK_DIR),
        repo_id=repo_id,
        repo_type="dataset",
        commit_message="Publish EU AI Act Normative Triples and Ground-Truth Benchmark",
    )
    print(f"Successfully published dataset to Hugging Face Hub!")
    print(f"Dataset URL: https://huggingface.co/datasets/{repo_id}")
    print(f"Commit: {commit_info}")

if __name__ == "__main__":
    deploy_dataset()
