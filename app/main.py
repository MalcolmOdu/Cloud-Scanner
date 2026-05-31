from fastapi import FastAPI
from app.api.routes import health, scans

app = FastAPI (
    title = "Cloud Misconfiguration Scanner",
    description = "Scans AWS accounts for security misconfigurations.",
    version = "0.1.0"
)

app.include_router(health.router)
app.include_router(scans.router)