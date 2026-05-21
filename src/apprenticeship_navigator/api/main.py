from fastapi import FastAPI
from apprenticeship_navigator.config import settings
from apprenticeship_navigator.api.routes import health

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )

    app.include_router(health.router)
    
    return app

app = create_app()


