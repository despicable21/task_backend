from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routes import router 


app = FastAPI(title="Task Backend")

#подключение метрик
Instrumentator().instrument(app).expose(app)

#подключение из routes.py
app.include_router(router)

#тестовый. нет await(async def для единообразия)
@app.get("/")
async def root():
    return {"message": "test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)