from fastapi import FastAPI
from routes.chat import router as chat_router
from routes.ingestion import router as ingestion_router
from routes.dashboard import router as dashboard_router
from routes.health import router as health_router

app = FastAPI(
    title="Investor Intelligence API",
    version="1.0.0"
)

# Register ingestion API endpoints
app.include_router(
    ingestion_router,
    prefix="/api",
    tags=["Ingestion"]
)

# Register interactive chat RAG endpoints
app.include_router(
    chat_router,
    prefix="/api",
    tags=["Chat"]
)

# Register dashboard / metrics endpoints
app.include_router(
    dashboard_router,
    prefix="/api",
    tags=["Dashboard"]
)

# Register system health check endpoints
app.include_router(
    health_router,
    tags=["Health"]
)

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI server locally on port 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)