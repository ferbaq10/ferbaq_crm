FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar gunicorn explícitamente
RUN pip install gunicorn

# Copiar código de la aplicación
COPY . .

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/static /app/media

# Ejecutar collectstatic (opcional, para Django)
RUN python manage.py collectstatic --noinput || echo "No static files to collect"

# Exponer puerto
EXPOSE 8000

# Comando para ejecutar la aplicación (CORREGIDO: core.wsgi en lugar de ferbaq_crm.wsgi)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "core.wsgi:application"]