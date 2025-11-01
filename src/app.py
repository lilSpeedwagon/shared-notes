import fastapi

import src.api.pastes

app = fastapi.FastAPI(
    title="Shared Notes API",
    description="A simple notes sharing service",
    version='0.1.0',
)

# Include API routers
app.include_router(src.api.pastes.router)


@app.get('/')
async def root():
    return {'message': "Shared Notes API"}


@app.get('/healthz')
async def health_check():
    """Health check endpoint for monitoring and deployment readiness."""
    return {'status': 'healthy'}
