import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/inventory')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SAFRS_API_DOCS = True
    SAFRS_API_DOCS_URL = os.environ.get("SAFRS_API_DOCS_URL", "/api/swagger.html")
    HOST = os.getenv('HOST', '0.0.0.0')
    HOST_SWAGGER = os.getenv('HOST_SWAGGER', 'inventory-service-190711226672.us-central1.run.app')
    PORT = int(os.getenv('PORT', 8080))
    PORT_SWAGGER = int(os.getenv('PORT_SWAGGER', 443))
    BASE_URL = os.getenv('BASE_URL', 'https://inventory-service-190711226672.us-central1.run.app')
