"""Configuración completa desde Crédito, sin alterar las APIs comerciales existentes.

La petición es reintentable: una combinación existente y aprobada se reutiliza,
jamás se sobrescribe. Rutas/células nuevas y aprobación son una transacción.
"""
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from client.models import Client
from project.models import Project
from catalog.models import UDN, WorkCell
from .models import CostCenter, ClientProjectConfiguration, ClientProjectRoute, ClientProjectRouteWorkCell
from .internal_api import internal_api_required, _json_body, _actor_username, _save_with_history, _validation_error_response


def _rutas_validas(config):
    """Solo rutas activas con al menos una célula autorizada."""
    rows = (ClientProjectRoute.objects.filter(
        configuration=config, is_removed=False, is_active=True,
        work_cell_assignments__is_removed=False,
        work_cell_assignments__is_active=True,
        work_cell_assignments__work_cell__is_removed=False,
    ).distinct().order_by('id'))
    return [{'id': x.pk, 'udn_id': x.udn_id} for x in rows]


@csrf_exempt
@require_POST
@internal_api_required
def credit_configuration_complete(request):
    """Crear o reutilizar cliente+proyecto+CC, con rutas y células.

    Se invoca con la clave interna del Portal; el actor se atribuye en auditoría.
    No concede permisos públicos, ni modifica configuraciones existentes.
    """
    try:
        data = _json_body(request)
        actor = _actor_username(data)
        client_id, project_id, cc_id = (int(data[k]) for k in
                                        ('client_id', 'project_id', 'cost_center_id'))
        rows = data.get('routes')
        if not isinstance(rows, list) or not 1 <= len(rows) <= 25:
            raise ValidationError('Debe indicar entre 1 y 25 rutas.')
        parsed = []
        seen_udns = set()
        for row in rows:
            if not isinstance(row, dict):
                raise ValidationError('Ruta inválida.')
            udn_id = int(row['udn_id'])
            raw_cells = row.get('work_cell_ids')
            if not isinstance(raw_cells, list) or not 1 <= len(raw_cells) <= 100:
                raise ValidationError('Cada ruta necesita células autorizadas.')
            cells = [int(x) for x in raw_cells]
            if udn_id in seen_udns or len(set(cells)) != len(cells):
                raise ValidationError('UDN o células duplicadas.')
            seen_udns.add(udn_id)
            parsed.append((udn_id, cells))
        ccc = str(data.get('client_cost_center') or '').strip()
        if len(ccc) > 150:
            raise ValidationError('El centro de costo del cliente supera 150 caracteres.')
        with transaction.atomic():
            client = get_object_or_404(Client, pk=client_id, is_removed=False)
            project = get_object_or_404(Project, pk=project_id, is_removed=False)
            cc = get_object_or_404(
                CostCenter, pk=cc_id, is_removed=False, is_active=True,
                delivery_site__is_removed=False, delivery_site__is_active=True)
            if not client.projects.filter(pk=project_id).exists():
                raise ValidationError('Proyecto no pertenece al cliente.')
            # Reintento: el primer guardado CRM pudo haber funcionado aunque
            # el Portal fallara antes de crear su snapshot.
            existing = (ClientProjectConfiguration.objects.select_for_update()
                .filter(client=client, project=project, cost_center=cc,
                        is_removed=False).first())
            if existing:
                routes = _rutas_validas(existing)
                if not (existing.is_active and
                        existing.validation_status == 'APPROVED' and routes):
                    return JsonResponse({'success': False, 'error':
                        'Existe configuración, pero no está aprobada y operativa. Revise CRM.',
                        'configuration_id': existing.pk}, status=409)
                matching = [r for r in routes if r['udn_id'] in seen_udns]
                if not matching:
                    return JsonResponse({'success': False, 'error':
                        'La configuración existente no tiene la UDN solicitada; seleccione una ruta vigente.'}, status=409)
                return JsonResponse({'success': True, 'configuration_id': existing.pk,
                    'routes': matching, 'created': False, 'validation_status': 'APPROVED'})
            for udn_id, cell_ids in parsed:
                if not UDN.objects.filter(pk=udn_id, is_removed=False).exists():
                    raise ValidationError('UDN inválida.')
                if WorkCell.objects.filter(pk__in=cell_ids, is_removed=False).count() != len(cell_ids):
                    raise ValidationError('Hay células inválidas.')
            cfg = ClientProjectConfiguration(client=client, project=project,
                cost_center=cc, client_cost_center=ccc or None,
                is_active=True, validation_status='PENDING')
            _save_with_history(cfg, actor_username=actor, reason='Alta Crédito')
            created_routes = []
            for udn_id, cell_ids in parsed:
                route = ClientProjectRoute(configuration=cfg, udn_id=udn_id, is_active=True)
                _save_with_history(route, actor_username=actor, reason='Ruta Crédito')
                created_routes.append({'id': route.pk, 'udn_id': udn_id})
                for cell_id in cell_ids:
                    cell = ClientProjectRouteWorkCell(route=route, work_cell_id=cell_id, is_active=True)
                    _save_with_history(cell, actor_username=actor, reason='Célula Crédito')
            cfg.validation_status = 'APPROVED'
            cfg.validated_at = timezone.now()
            cfg.validated_by_username = actor
            cfg.validation_comment = 'Configuración completada por Crédito desde Portal FERBAQ.'
            _save_with_history(cfg, actor_username=actor, reason='Validación Crédito')
            return JsonResponse({'success': True, 'configuration_id': cfg.pk,
                'routes': created_routes, 'created': True,
                'validation_status': 'APPROVED'})
    except (KeyError, TypeError, ValueError, ValidationError) as exc:
        return _validation_error_response(exc)
    except IntegrityError:
        return JsonResponse({'success': False, 'error':
            'Se detectó una operación concurrente. Recargue para seleccionar la configuración creada.'}, status=409)
