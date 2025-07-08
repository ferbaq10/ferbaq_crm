import os
import sys
import time
import django

from redis import Redis
from rq import Queue
from decouple import config

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
django.setup()

# Configuración Redis
REDIS_HOST = config('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_DB = int(config('REDIS_DB', default='1'))

redis_conn = Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
queue = Queue('default', connection=redis_conn)

print("🔄 Worker manual ejecutando tareas en cola 'default'...")

while True:
    job_ids = queue.job_ids
    if not job_ids:
        time.sleep(2)
        continue

    for job_id in job_ids:
        job = queue.fetch_job(job_id)
        if job is None:
            continue

        print(f"🛠️ Ejecutando job {job.id} ({job.func_name})...")
        try:
            result = job.perform()
            job.delete()
            print(f"✅ Completado job {job.id} → {result}")
        except Exception as e:
            print(f"❌ Error en job {job.id}: {e}")

    time.sleep(1)