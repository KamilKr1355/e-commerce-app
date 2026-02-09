from fastapi import FastAPI

app = FastAPI(title="E-commerce app")


@app.get("/")
async def root():
    return {"message": "Hello World"}