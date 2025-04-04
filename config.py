import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://myuser:mypass@localhost:5432/mydatabase"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SAFRS_API_DOCS = True
    SAFRS_API_DOCS_URL = os.environ.get("SAFRS_API_DOCS_URL", "/api/swagger.html")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 8080))
