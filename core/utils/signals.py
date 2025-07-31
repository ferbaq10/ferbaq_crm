import os
import sys

def should_skip_signal_registration():
    """
    Determina si deben omitirse los registros de signals.
    Evita registrar señales en comandos administrativos
    o en el proceso secundario del autoreloader de runserver.
    """
    skip_commands = {
        'makemigrations',
        'migrate',
        'showmigrations',
        'collectstatic',
        'shell',
        'check',
        'test',
    }

    if any(cmd in sys.argv for cmd in skip_commands):
        return True

    # Evitar ejecución duplicada por runserver (autoreload)
    if os.environ.get('RUN_MAIN') != 'true':
        return True

    return False
