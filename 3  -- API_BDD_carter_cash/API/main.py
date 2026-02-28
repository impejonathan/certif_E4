from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from routers import search_router, auth_router, dimensions_router

app = FastAPI(
    title="API Carter Cash",
    description="API pour la recherche de pneus et dimensions par véhicules",
    version="1.0.0",
    docs_url="/"  # Ceci déplace la documentation Swagger à la racine
)

# Inclusion des routeurs
app.include_router(search_router.router)
app.include_router(auth_router.router)
app.include_router(dimensions_router.router)

# Redirection de /docs vers la racine (optionnel si vous voulez garder l'accès via /docs aussi)
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_redirect():
    return RedirectResponse(url="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
