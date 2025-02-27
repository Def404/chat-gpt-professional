from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.post("/api/addition")
async def addition(a: int, b: int):
    return {"result": a + b}

@app.post("/api/subtraction")
async def subtraction(a: int, b: int):
    return {"result": a - b}

@app.post("/api/multiplication")
async def multiplication(a: int, b: int):
    return {"result": a * b}

@app.post("/api/division")
async def division(a: int, b: int):
    return {"result": a / b}