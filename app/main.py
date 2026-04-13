from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Screening Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to the AI Resume Screening Service",
        "docs": "/docs",
        "health": "/health"
    }
