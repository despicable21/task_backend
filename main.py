#!/usr/bin/env python3

import uvicorn
import configparser
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from routes import router 

config = configparser.ConfigParser()
config.read('config.ini')
host = config.get('server', 'host')
port = config.getint('server', 'port')


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
    
    uvicorn.run(app, host=host, port=port)