import uvicorn
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routes import router
from settings import settings

app = FastAPI(title="Task Backend")

#подключение метрик
Instrumentator().instrument(app).expose(app)

#подключение из routes.py
app.include_router(router)

#тестовый
@app.get("/")
async def root():
    return {"message": "test"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT)
