from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
async def root(page: int = 1, limit: int = 10):
    start = (page - 1) * limit
    end = start + limit
    with open("trademark_sample.json", "r") as f:
        data = json.load(f)
    
    return data[start: end]

@app.get("/search")
async def search(q: str, page: int = 1, limit: int = 10):
    start = (page - 1) * limit
    end = start + limit
    with open("trademark_sample.json", "r") as f:
        data = json.load(f)
    
    filtered_data = [item for item in data if q.lower() in str(item["productName"])]

    return filtered_data[start: end]