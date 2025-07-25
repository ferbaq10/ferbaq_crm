# FERBAQ CRM

Este proyecto forma parte del sistema CRM de FERBAQ. Proporciona una API REST para gestionar catálogos como UDN, células de trabajo, grupos empresariales, divisiones, ciudades y más.

## 📁 Estructura del Proyecto
```bash
ferbaq_crm/
├── activar.ps1                 # Script para activar entorno virtual en PowerShell
├── activity_log/               # Módulo para el registro de actividades
│   ├── admin.py               # Configuración del admin para activity_log
│   ├── apps.py                # Configuración del módulo
│   ├── forms.py               # Formularios para activity_log
│   ├── __init__.py            
│   ├── models.py              # Modelos de base de datos
│   ├── serializers.py         # Serializadores DRF
│   ├── services/              # Lógica de negocio y servicios relacionados
│   │   ├── activity_log_service.py
│   │   ├── factories.py
│   │   ├── __init__.py
│   │   └── interfaces.py
│   ├── tests.py               # Pruebas unitarias
│   ├── urls.py                # Rutas API
│   └── viewsets.py            # Vistas basadas en ViewSets
├── catalog/                   # Catálogos de datos maestros (ciudades, UDN, divisiones, etc.)
│   ├── admin.py               
│   ├── apps.py                
│   ├── constants.py           # Constantes usadas en catalog
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── signals.py             # Señales Django
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets/              # Vistas para APIs relacionadas con catalog
│       ├── base.py
│       ├── catalog_viewsets.py
│       └── __init__.py
├── client/                    # Gestión de clientes
│   ├── admin.py               
│   ├── apps.py                
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── services/              # Lógica de negocio para clientes
│   │   ├── user_service.py
│   │   ├── factories.py
│   │   ├── __init__.py
│   │   └── interfaces.py
│   ├── signals.py             
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── contact/                   # Gestión de contactos (clientes, oportunidades)
│   ├── admin.py               
│   ├── apps.py                
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── services/              # Servicios relacionados con contactos
│   │   ├── contact_service.py
│   │   ├── factories.py
│   │   ├── __init__.py
│   │   └── interfaces.py
│   ├── signals.py             
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── core/                      # Configuración central del proyecto
│   ├── apps.py                
│   ├── asgi.py               
│   ├── di.py                 # Configuración de inyección de dependencias
│   ├── __init__.py            
│   ├── modules.py            
│   ├── serializers/          # Serializadores comunes
│   │   ├── cache_mixin.py    
│   │   └── __init__.py       
│   ├── settings.py           # Configuración Django
│   ├── urls.py               # Enrutamiento principal
│   ├── utils/                # Utilidades varias
│   │   ├── __init__.py       
│   │   └── signals.py        
│   └── wsgi.py               
├── docker-compose.yml         # Configuración Docker Compose
├── envExample                 # Ejemplo de archivo .env
├── manage.py                  # Script principal Django (runserver, migrate, etc.)
├── middleware/                # Middleware personalizado
│   ├── __init__.py           
│   └── sql_debug.py           
├── objetive/                  # Objetivos comerciales
│   ├── admin.py               
│   ├── apps.py                
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── signals.py             
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── opportunity/              # Oportunidades comerciales
│   ├── admin.py               
│   ├── apps.py                
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── services/              # Servicios relacionados
│   │   ├── factories.py
│   │   ├── interfaces.py
│   │   └── opportunity_service.py
│   ├── sharepoint.py          # Integración con SharePoint
│   ├── signals.py             
│   ├── tasks.py               # Tareas asíncronas
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── poetry.lock               # Archivo de bloqueo de dependencias Poetry
├── project/                  # Gestión de proyectos derivados
│   ├── admin.py               
│   ├── apps.py                
│   ├── forms.py               
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── services/              # Servicios de proyecto
│   │   ├── factories.py
│   │   ├── __init__.py
│   │   ├── interfaces.py
│   │   └── project_service.py
│   ├── signals.py             
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── purchase/                 # Compras y adquisiciones
│   ├── admin.py               
│   ├── apps.py                
│   ├── __init__.py            
│   ├── models.py              
│   ├── serializers.py         
│   ├── services/              # Servicios de compras
│   │   ├── factories.py
│   │   ├── interfaces.py
│   │   └── purchase_service.py
│   ├── signals.py             
│   ├── tests.py               
│   ├── urls.py                
│   └── viewsets.py            
├── pyproject.toml             # Configuración de dependencias (Poetry)
├── README para k8s.md                  # Documentación general del proyecto
├── run_simple_worker.py       # Script para ejecución de worker simple
└── users/                    # Gestión de usuarios y autenticación
    ├── admin.py              
    ├── apps.py               
    ├── __init__.py           
    ├── models.py             
    ├── serializers.py        
    ├── tests.py              
    ├── urls.py               
    └── viewsets.py          
```

## 🧱 Patrones utilizados

- **ViewSet Base Reutilizable**  
  `AuthenticatedModelViewSet` permite reutilizar lógica común para múltiples modelos que requieren autenticación y permisos, reduciendo código duplicado.

- **DRY (Don’t Repeat Yourself)**  
  Se centraliza la lógica de `queryset` para permitir compatibilidad con managers como `all_objects` en modelos con borrado lógico.

- **Convención sobre Configuración**  
  Cada `ViewSet` solo define su `model` y `serializer_class`, apoyándose en la lógica heredada.
- **Inyección de Dependencias**  
  Utiliza un contenedor de inyección de dependencias para desacoplar la lógica de negocio de la implementación concreta, facilitando pruebas y mantenimiento.
- **Separación de Preocupaciones**  
  Cada módulo tiene una responsabilidad clara: `catalog` para datos maestros, `client` para clientes, `contact` para contactos, etc. Esto mejora la mantenibilidad y escalabilidad del proyecto.
- **Servicios y Factories**  
- **Patrón Observer**
    Es un patrón de diseño de comportamiento que permite que un objeto (el sujeto) notifique a otros objetos (observadores) cuando ocurre un cambio en su estado.
    Los observadores se registran para recibir actualizaciones o eventos, y son notificados automáticamente.
- **Middleware Personalizado**
   Es un patrón arquitectónico/interceptor que permite interceptar y procesar peticiones y respuestas de forma centralizada.

- **Tareas Asíncronas con Redis**
    Aplica el patrón Producer-Consumer (Productor-Consumidor), donde el productor pone tareas en una cola y el consumidor (worker) las procesa.

- **Configuración de Entorno (.env)**
    Es una práctica relacionada con el patrón External Configuration, que consiste en separar la configuración del código para mayor flexibilidad.

- **Pruebas Unitarias**
   No es un patrón, pero es una buena práctica fundamental para el desarrollo.

- **Docker y Docker Compose**
   Es una herramienta de contenedorización y orquestación, no un patrón, aunque soporta patrones de despliegue (como microservicios).

- **Configuración de Seguridad**
   Incluye varios patrones de seguridad (por ejemplo, autenticación, autorización), pero en sí es una categoría de buenas prácticas.

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

### Actualizar àrbol de la estructura del proyecto

ejecutar el siguiente comando en la raíz del proyecto:
Este es un comando que genera un archivo `estructura_actual.txt` con la estructura del proyecto, excluyendo ciertos archivos y directorios como `__pycache__`, archivos `.pyc`, bases de datos SQLite, archivos de entorno, logs, egg-info, node_modules y migraciones.
Se necesita tener ubuntu y el comando instalado para su ejecución.

```bash
  tree -I '__pycache__|*.pyc|*.sqlite3|*.env|*.log|*.egg-info|node_modules|migrations' -L 3 > estructura_actual.txt
```

Luego debe copiar la estructura generada en el archivo `estructura_actual.txt` y pegarla en el archivo `README.md` en la sección de estructura del proyecto.

### Actualizar lista de librerias
Para actualizar la lista de librerías ejecutar el siguiente comando:

```bash
  poetry export -f requirements.txt --output requirements.txt --without-hashes
```

Para comprobar que ya no esta en .env

```bash
kubectl exec -it deployment/backend-dev -n dev -- find /app -name ".env"
```

Para comproabr si sigue en la imagen el .env
```bash
 docker run --rm -it ferbaq-crm-backend sh -c "find /app -name .env"
 ```



## 🚀 PASOS MANUALES PARA DESPLEGAR DJANGO + REDIS + POSTGRES EN EC2:

### PASO 1: Conectarte por SSH
```bash
  ssh -i "TU-CLAVE.pem" ubuntu@IP_PUBLICA
```
Puede que no se conecte por ssh si la instancia creada no tiene el rol con el permiso AmazonSSMManagedInstanceCore
Se debe crear un rol y asignarle este rol si no lo tiene

Además para tener acceso en el grupo de seguridad debe tener una regla de entrada con el ip registrado.

### PASO 2: 🧱 Instalar dependencias del sistema

```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y git python3 python3-pip python3-venv build-essential \
    libpq-dev redis-server nginx
```

### PASO 3: Clonar el proyecto desde GitHub

```bash
  cd /var/www/
  sudo git clone git@github.com:ferbaq10/ferbaq_crm.git ferbaq_crm_backend
  sudo chown -R $USER:$USER ferbaq_crm_backend
  cd ferbaq_crm_backend
```

### PASO 4: Configurar entorno virtual
```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
```

### PASO 5: Configurar variables de entorno (Django + DB)
Para crear el archivo de configuración, guiarse por las variables que se encuentran en envExample
o las configuraciones propias
```bash
  nano .env
```

### PASO 6: Migraciones, superusuario y archivos estáticos
```bash
  source venv/bin/activate
  python manage.py migrate
  python manage.py createsuperuser
  python manage.py collectstatic
```