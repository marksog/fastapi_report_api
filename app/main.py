from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import auth, potentials, workers

# Create all database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(potentials.router)
# app.include_router(disciples.router)
app.include_router(workers.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Report Application API"}