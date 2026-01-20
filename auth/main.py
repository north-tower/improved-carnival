from fastapi import FastAPI
from database import engine, Base
from routers import auth

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="User Authentication API",
    description="FastAPI authentication system with JWT tokens",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router)


@app.get("/")
async def root():
    return {
        "message": "Authentication API is running",
        "version": "1.0.0",
        "endpoints": {
            "signup": "/auth/signup",
            "login": "/auth/login",
            "current_user": "/auth/me",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
