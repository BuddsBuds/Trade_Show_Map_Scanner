from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import file_routes

app = FastAPI(
    title="TradeShow Scout - File Processor",
    description="Service for processing trade show floor plan files",
    version="0.1.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(file_routes.router, prefix="/api/v1", tags=["files"])