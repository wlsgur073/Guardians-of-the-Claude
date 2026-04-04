from fastapi import FastAPI

app = FastAPI(title="MyApp")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
