
from fastapi import FastAPI
from app.routers import posts, users, auth, vote

app = FastAPI()

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)


@app.get("/")
def root():
    return {"message": "Welcome to my Social Media API"}
