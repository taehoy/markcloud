from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
async def root():
    with open("trademark_sample.json", "r") as f:
        data = json.load(f)
    return data