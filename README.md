# FERBAQ CRM

Este proyecto forma parte del sistema CRM de FERBAQ. Proporciona una API REST para gestionar catálogos como UDN, células de trabajo, grupos empresariales, divisiones, ciudades y más.

---

## 📁 Estructura del Proyecto
```bash
ferbaq_crm/
├── catalog/               # Módulo para catálogos de datos maestros (ciudades, UDN, divisiones, etc.)
│   ├── models.py          # Definición de modelos de base de datos relacionados con catálogos
│   ├── serializers.py     # Serializadores DRF para exponer modelos como JSON
│   ├── forms.py           # Formularios Django para uso en admin u otros
│   ├── catalog_viewsets.py        # Lógica de vistas con ViewSets (API REST)
│   ├── urls.py            # Rutas del módulo catalog
│   ├── tests.py           # Pruebas unitarias del módulo
│   └── admin.py           # Registro de modelos en el panel de administración
├── client/                # Gestión de clientes
│   ├── models.py          # Modelos relacionados con clientes
│   ├── serializers.py     # Serializadores DRF para clientes
│   ├── forms.py           # Formularios de clientes
│   ├── catalog_viewsets.py        # API REST para clientes
│   ├── urls.py            # Rutas del módulo
│   ├── tests.py           # Pruebas unitarias
│   └── admin.py           # Configuración del admin para clientes
├── contact/               # Gestión de contactos asociados a clientes u oportunidades
│   ├── models.py
│   ├── serializers.py
│   ├── forms.py
│   ├── catalog_viewsets.py
│   ├── urls.py
│   ├── tests.py
│   └── admin.py
├── core/                  # Configuración central del proyecto
│   ├── settings.py        # Configuración principal de Django
│   ├── urls.py            # Enrutamiento principal del proyecto
│   └── ...                # Otros archivos como wsgi.py, asgi.py, etc.
├── objetive/              # Módulo para definir objetivos comerciales
│   ├── models.py
│   ├── serializers.py
│   ├── forms.py
│   ├── catalog_viewsets.py
│   ├── urls.py
│   ├── tests.py
│   └── admin.py
├── opportunity/           # Gestión de oportunidades comerciales
│   ├── models.py
│   ├── serializers.py
│   ├── forms.py
│   ├── catalog_viewsets.py
│   ├── urls.py
│   ├── tests.py
│   └── admin.py
├── project/               # Módulo para la gestión de proyectos derivados de oportunidades
│   ├── models.py
│   ├── serializers.py
│   ├── forms.py
│   ├── catalog_viewsets.py
│   ├── urls.py
│   ├── tests.py
│   └── admin.py
├── manage.py              # Script principal para comandos Django (runserver, migrate, etc.)
├── activar.ps1.py         # Script auxiliar para activar entorno virtual en PowerShell
├── pyproject.toml         # Archivo de configuración de dependencias (Poetry)
├── envExample             # Archivo de ejemplo para variables de entorno
└── README.md              # Documentación general del proyecto

```

---

## 🧱 Patrones utilizados

- **ViewSet Base Reutilizable**  
  `AuthenticatedModelViewSet` permite reutilizar lógica común para múltiples modelos que requieren autenticación y permisos, reduciendo código duplicado.

- **DRY (Don’t Repeat Yourself)**  
  Se centraliza la lógica de `queryset` para permitir compatibilidad con managers como `all_objects` en modelos con borrado lógico.

- **Convención sobre Configuración**  
  Cada `ViewSet` solo define su `model` y `serializer_class`, apoyándose en la lógica heredada.

---

## ⚙️ Instalación del Proyecto

Requisitos previos:
- Python 3.10 o superior
- PostgreSQL o base de datos compatible
- pipenv o virtualenv (opcional pero recomendado)
- Poetry instalado
- Instalado el git
- Creada llave ssh y registrada en github para la clonación del proyecto

### Instalar Poetry

1. Abre PowerShell (como administrador recomendado)
Puedes buscar "PowerShell", hacer clic derecho y elegir “Ejecutar como administrador”.

2. Ejecuta el siguiente comando
```bash
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```
3. Agrega Poetry al PATH (si no lo hace automáticamente)
Después de la instalación, añade esta línea a tu archivo de perfil ($PROFILE) o ejecuta directamente:
```bash
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$env:USERPROFILE\AppData\Roaming\Python\Scripts", "User")
```
4. Verifica la instalación
```bash
poetry --version
```
### 1. Clonar el repositorio
Abrir carpeta donde se va a descargar el repositorio y abrir terminal par que se situe dentro de esa carpeta

```bash
    git clone git@github.com:ferbaq10/ferbaq_crm.git
    cd ferbaq_crm
```

### 2. Crear entorno virtual y activarlo
```bash
poetry install
```

y ejecutar si se utiliza Windows
```bash
  .\activar.ps
```

Si no se quiere utilizar poetry:

```bash
    python -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate     # Windows
```

### 3. Instalar dependencias
Esta parte es igual si no se va a utilizar poetry
```bash
    pip install -r requirements.txt
```
## Configuración y ejecución

### 1. Configurar variables de entorno
Crea un archivo .env en la raíz del proyecto:

```bash
# Para desarrollo
DEBUG=True
CORS_ALLOW_ALL_ORIGINS=True

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=5432

# CORS - Permisivo para desarrollo
CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000
```

### 2. Migraciones y carga inicial
```bash
    python manage.py migrate
```

###  3. Crear superusuario

Si la base de datos es local, ya que si se utiliza la base de datos de desarrollo, ya no es necesario realizar migración
```bash
    python manage.py migrate
```
Si se usa la base de datos de desarrollo, el usuario es admin:admin

### 4. Ejecutar servidor de desarrollo
```bash
    python manage.py runserver
```

### 5. Ejecutar Redis de manera local
Agregar la siguiente configuración en el archivo .env
```bash
  REDIS_HOST=127.0.0.1
  REDIS_PORT=6379
  REDIS_DB=1
```

Abrir un terminal y situarse en la raíz del proyecto y ejecutar:
```bash
  docker-compose up -d
```

Deberías ver un contenedor llamado local-redis expuesto en el puerto 6379 con el siguiente comando:

```bash
  docker ps
```

### Ejecutar el worker

Ejecutar el worker para que ejecute tareas asíncronas para proyecto local en Windows:
```bash
  python run_simple_worker.py
```

Para correr en linux
```bash
  python manage.py rqworker default
```

