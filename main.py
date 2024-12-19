from fastapi import FastAPI
from pydantic import BaseModel
from celery.result import AsyncResult
from celery_app import analyze_pr_task
import redis

app = FastAPI()

redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

class PRDetails(BaseModel):
    repo: str
    pr_number: int

@app.post("/analyze-pr")
def analyze_pr(pr_details: PRDetails):
    task = analyze_pr_task.delay(pr_details.repo, pr_details.pr_number)
    return {"task_id": task.id}

@app.get("/status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {"status": task_result.status}

@app.get("/results/{task_id}")
def get_results(task_id: str):
    results = redis_client.get(f"task_results:{task_id}")
    if results:
        return {"results": results}
    return {"error": "Results not found or task not complete"}
