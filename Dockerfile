# Usa una imagen base de Python 3.12 (versión slim para menor tamaño)
FROM python:3.12-slim

# Establece el directorio de trabajo
WORKDIR /app

# Copia el archivo de requerimientos y lo instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Expone el puerto (por defecto 8084, se puede parametrizar con variable de entorno)
EXPOSE ${PORT}

# Establece variables de entorno con valores por defecto
ENV DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydatabase
ENV PORT=8080
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV HOST=0.0.0.0
ENV BASE_URL=https://inventory-service-190711226672.us-central1.run.app

# Comando para iniciar la aplicación
CMD ["python", "app.py"]
