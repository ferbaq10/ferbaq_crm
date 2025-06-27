from django.db import connection
from django.conf import settings
import time


class SQLDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG and request.path.startswith('/api/'):
            # Contar consultas antes de la request
            initial_queries = len(connection.queries)
            start_time = time.time()

            response = self.get_response(request)

            # Contar consultas después de la request
            end_time = time.time()
            final_queries = len(connection.queries)
            queries_count = final_queries - initial_queries

            if queries_count > 0:
                print(f"\n🔍 API: {request.method} {request.path}")
                print(f"📊 Consultas ejecutadas: {queries_count}")
                print(f"⏱️  Tiempo total: {(end_time - start_time) * 1000:.2f}ms")
                print("-" * 60)

                # Mostrar cada consulta
                for query in connection.queries[initial_queries:]:
                    print(f"SQL: {query['sql']}")
                    print(f"Tiempo: {query['time']}s")
                    print("-" * 40)

            return response
        else:
            return self.get_response(request)