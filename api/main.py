from fastapi import FastAPI

from api.routes import health, insights, recommendations, sessions, users

app = FastAPI(
    title="Healthy Aging AI API",
    description="Reusable API for profiles, check-ins, recommendations, scoring, sessions, and insights.",
    version="1.0.0",
)

for router in [health.router, users.router, recommendations.router, sessions.router, insights.router]:
    app.include_router(router)
