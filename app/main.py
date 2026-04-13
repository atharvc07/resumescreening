from fastapi import FastAPI
from .api import routes
from .database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Screening Service")
app.include_router(routes.router)
