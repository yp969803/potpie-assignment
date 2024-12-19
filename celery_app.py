from celery import Celery
import redis
from ai_agent import analyze_code
import requests
from typing import List
import os

from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_URL ="https://api.github.com"


celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

@celery_app.task
def analyze_pr_task(repo: str, pr_number: int):

    code_files = fetch_pr_code(repo, pr_number)

    analysis_results = analyze_code(code_files)

    task_id = analyze_pr_task.request.id
    redis_client.set(f"task_results:{task_id}", str(analysis_results))
    return analysis_results

def fetch_pr_code(repo: str, pr_number: int) -> List[str]:
  
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    files_url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/files"
    response = requests.get(files_url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Failed to fetch PR files: {response.json()}")

    files_data = response.json()

    code_files = []
    for file in files_data:
        if file["status"] == "modified" or file["status"] == "added":
            raw_url = file["raw_url"]
            raw_response = requests.get(raw_url, headers=headers)
            if raw_response.status_code == 200:
                code_files.append(raw_response.text)
            else:
                print(f"Failed to fetch file content for {file['filename']}.")

    return code_files