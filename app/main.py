from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router

from app.db.session import SessionLocal
from app.db.db_seed import seed_users

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    db = SessionLocal()
    try:
        seed_users(db)   # ❌ žádné await
    finally:
        db.close()

    yield

app = FastAPI(
    title="WorkSphere API",
    description="Scans, Works, ...",
    version="1.0.0",
    docs_url="/docs",        # Swagger
    redoc_url="/redoc",      # ReDoc
    openapi_url="/openapi.json",
    lifespan=lifespan
)

origins = [
    "http://localhost:5173",  # FE dev server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
