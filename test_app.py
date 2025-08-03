import uvicorn

if __name__ == "__main__":
    uvicorn.run("py_backend_logic.main:app", host="0.0.0.0", port=8000)