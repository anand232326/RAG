from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database.create_table import create_tables
from database.postgres_sql import create_database
from routes.chat import router as chat_router
from routes.ingestion import router as ingestion_router
from routes.dashboard import router as dashboard_router
from routes.health import router as health_router

app = FastAPI(
    title="Investor Intelligence API",
    version="1.0.0"
)

frontend_dist = Path(__file__).parent / "frontend" / "dist"
frontend_assets = frontend_dist / "assets"
if frontend_assets.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=frontend_assets),
        name="frontend-assets"
    )


@app.on_event("startup")
def startup_event() -> None:
    create_database()
    create_tables()


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


@app.get("/", include_in_schema=False)
def frontend() -> FileResponse:
    index_file = frontend_dist / "index.html"
    if not index_file.is_file():
        raise FileNotFoundError(
            "Frontend build is missing. Build it with `cd frontend && npm run build`."
        )
    return FileResponse(index_file)


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI server locally on port 8080
    uvicorn.run(app, host="0.0.0.0", port=8080)