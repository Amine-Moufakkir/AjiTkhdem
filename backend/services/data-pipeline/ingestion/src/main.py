from fastapi import FastAPI

app = FastAPI(title="AjiTkhdem - Ingestion API")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Hello World from Ingestion Service!"}