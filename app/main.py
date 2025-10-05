from fastapi import FastAPI

# from app.middleware.error_handler import ApiErrorHandler
# from app.api.v1.routers import api_router
# from app.core.config import settings

app = FastAPI()
# app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)
# app.add_middleware(ApiErrorHandler)


# app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "OK"}
