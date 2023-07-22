from fastapi import FastAPI

app = FastAPI(title='BrandPlus API')


@app.get("/")
async def root():
    return {"message": "Hello World"}
