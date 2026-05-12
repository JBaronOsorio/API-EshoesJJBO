# Imagen base oficial de Python en versión slim para reducir el tamaño final
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar primero solo el archivo de dependencias para aprovechar el cache
# de capas de Docker. Si requirements.txt no cambia, esta capa se reutiliza
# y no se reinstalan las dependencias en cada build.
COPY requirements.txt .

# Instalar dependencias sin guardar cache de pip para mantener la imagen liviana
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente al contenedor
COPY . .

# Crear el directorio de datos para la base de datos SQLite
RUN mkdir -p /app/data

# Exponer el puerto en el que corre la aplicación
EXPOSE 8000

# Comando de inicio: uvicorn apuntando al módulo principal de FastAPI
CMD ["uvicorn", "src.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]