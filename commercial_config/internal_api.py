import json
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from simple_history.utils import update_change_reason

from catalog.models import UDN, WorkCell
from client.models import Client
from project.models import Project

from .models import (
    CostCenter,
    ClientProjectConfiguration,
    ClientProjectRoute,
    ClientProjectRouteWorkCell,
)


# ============================================================
# SEGURIDAD
# ============================================================

def _configured_api_key():
    return str(
        getattr(
            settings,
            'PORTAL_COMMERCIAL_CONFIG_API_KEY',
            '',
        )
        or ''
    ).strip()


def _request_api_key(request):
    return str(
        request.headers.get(
            'X-Portal-Api-Key',
            '',
        )
        or ''
    ).strip()


def _authorized(request):
    expected = _configured_api_key()
    received = _request_api_key(request)

    if not expected or not received:
        return False

    return secrets.compare_digest(
        expected,
        received,
    )


def internal_api_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not _authorized(request):
            return JsonResponse(
                {
                    'success': False,
                    'error': 'No autorizado.',
                },
                status=401,
            )

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapper


# ============================================================
# HELPERS
# ============================================================

def _json_body(request):
    try:
        raw = request.body.decode('utf-8')

        if not raw:
            return {}

        data = json.loads(raw)

        if not isinstance(data, dict):
            raise ValueError()

        return data

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        ValueError,
    ):
        raise ValidationError(
            'El cuerpo de la solicitud debe ser JSON válido.'
        )


def _actor_username(data):
    actor = str(
        data.get('actor_username')
        or 'portal-ferbaq'
    ).strip()

    return actor[:150]


def _history_user(actor_username):
    User = get_user_model()

    return (
        User.objects
        .filter(username=actor_username)
        .first()
    )


def _save_with_history(
    instance,
    *,
    actor_username,
    reason,
):
    """
    Guarda usando el modelo REAL del CRM.

    simple_history genera el registro histórico porque
    estamos usando los modelos administrados del CRM,
    no los wrappers managed=False del Portal.
    """

    history_user = _history_user(
        actor_username
    )

    if history_user:
        instance._history_user = history_user

    instance.full_clean()
    instance.save()

    try:
        update_change_reason(
            instance,
            reason[:100],
        )
    except Exception:
        # El guardado principal nunca debe fallar únicamente
        # porque no pudo asignarse history_change_reason.
        pass

    return instance


def _validation_error_response(exc):
    if hasattr(exc, 'message_dict'):
        error = exc.message_dict
    elif hasattr(exc, 'messages'):
        error = exc.messages
    else:
        error = str(exc)

    return JsonResponse(
        {
            'success': False,
            'error': error,
        },
        status=400,
    )


def _get_configuration(configuration_id):
    return get_object_or_404(
        ClientProjectConfiguration.objects.select_related(
            'client',
            'project',
            'cost_center',
            'cost_center__delivery_site',
        ),
        pk=configuration_id,
        is_removed=False,
    )


def _reset_validation_if_needed(
    configuration,
    *,
    actor_username,
    reason,
):
    """
    Una configuración aprobada que cambia comercialmente
    debe volver a PENDING.

    Evita mantener como APPROVED algo que ya fue modificado.
    """

    if (
        configuration.validation_status
        != 'APPROVED'
    ):
        return

    configuration.validation_status = 'PENDING'
    configuration.validated_at = None
    configuration.validated_by_username = None
    configuration.validation_comment = (
        'Validación reiniciada automáticamente '
        'por modificación de configuración.'
    )

    _save_with_history(
        configuration,
        actor_username=actor_username,
        reason=reason,
    )


# ============================================================
# CONFIGURACIÓN CLIENTE + PROYECTO
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def configuration_save(request):
    """
    Crear o editar configuración comercial.

    CREAR:
    {
        "client_id": 52,
        "project_id": 78,
        "cost_center_id": 1,
        "client_cost_center": "ABC",
        "actor_username": "usuario.portal"
    }

    EDITAR:
    {
        "configuration_id": 1,
        "client_id": 52,
        "project_id": 78,
        "cost_center_id": 1,
        "client_cost_center": "ABC",
        "actor_username": "usuario.portal"
    }

    Cliente y Proyecto se consideran identidad de la
    configuración y no se cambian después de creada.
    """

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        configuration_id = (
            data.get('configuration_id')
        )

        client_id = int(
            data.get('client_id')
        )

        project_id = int(
            data.get('project_id')
        )

        cost_center_id = int(
            data.get('cost_center_id')
        )

        client_cost_center = str(
            data.get('client_cost_center')
            or ''
        ).strip()

        with transaction.atomic():
            client = get_object_or_404(
                Client,
                pk=client_id,
                is_removed=False,
            )

            project = get_object_or_404(
                Project,
                pk=project_id,
                is_removed=False,
            )

            cost_center = get_object_or_404(
                CostCenter.objects.select_related(
                    'delivery_site'
                ),
                pk=cost_center_id,
                is_removed=False,
                is_active=True,
                delivery_site__is_removed=False,
                delivery_site__is_active=True,
            )

            # ==================================================
            # EDICIÓN
            # ==================================================

            if configuration_id:
                configuration = (
                    _get_configuration(
                        int(configuration_id)
                    )
                )

                if (
                    configuration.client_id
                    != client.pk
                    or
                    configuration.project_id
                    != project.pk
                ):
                    return JsonResponse(
                        {
                            'success': False,
                            'error': (
                                'Cliente y Proyecto no pueden '
                                'cambiarse en una configuración '
                                'existente. Cree una nueva '
                                'configuración.'
                            ),
                        },
                        status=400,
                    )

                changed = (
                    configuration.cost_center_id
                    != cost_center.pk
                    or
                    (
                        configuration.client_cost_center
                        or ''
                    )
                    != client_cost_center
                )

                configuration.cost_center = (
                    cost_center
                )

                configuration.client_cost_center = (
                    client_cost_center or None
                )

                _save_with_history(
                    configuration,
                    actor_username=actor,
                    reason=(
                        'Configuración comercial '
                        'actualizada desde Portal'
                    ),
                )

                if changed:
                    _reset_validation_if_needed(
                        configuration,
                        actor_username=actor,
                        reason=(
                            'Validación reiniciada por '
                            'edición comercial'
                        ),
                    )

                created = False

            # ==================================================
            # NUEVA
            # ==================================================

            else:
                duplicate = (
                    ClientProjectConfiguration.objects
                    .filter(
                        client=client,
                        project=project,
                        cost_center=cost_center,
                        is_removed=False,
                    )
                    .first()
                )

                if duplicate:
                    return JsonResponse(
                        {
                            'success': False,
                            'error': (
                                'Ya existe una configuración '
                                'para ese Cliente, Proyecto y '
                                'Centro de costo.'
                            ),
                            'configuration_id': (
                                duplicate.pk
                            ),
                        },
                        status=400,
                    )

                configuration = (
                    ClientProjectConfiguration(
                        client=client,
                        project=project,
                        cost_center=cost_center,
                        client_cost_center=(
                            client_cost_center
                            or None
                        ),
                        validation_status='PENDING',
                        is_active=True,
                    )
                )

                _save_with_history(
                    configuration,
                    actor_username=actor,
                    reason=(
                        'Configuración comercial creada '
                        'desde Portal'
                    ),
                )

                created = True

        return JsonResponse(
            {
                'success': True,
                'created': created,
                'configuration': {
                    'id': configuration.pk,
                    'client_id': (
                        configuration.client_id
                    ),
                    'project_id': (
                        configuration.project_id
                    ),
                    'cost_center_id': (
                        configuration.cost_center_id
                    ),
                    'client_cost_center': (
                        configuration.client_cost_center
                    ),
                    'validation_status': (
                        configuration.validation_status
                    ),
                    'is_active': (
                        configuration.is_active
                    ),
                },
            },
            status=201 if created else 200,
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)

    except IntegrityError as exc:
        return JsonResponse(
            {
                'success': False,
                'error': (
                    'La operación viola una restricción '
                    'de integridad del CRM.'
                ),
                'detail': str(exc),
            },
            status=400,
        )


# ============================================================
# APROBAR / RECHAZAR / ACTIVAR / DESACTIVAR
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def configuration_state(request):
    """
    {
        "configuration_id": 1,
        "action": "approve",
        "comment": "Validada",
        "actor_username": "usuario.portal"
    }

    action:
    - approve
    - reject
    - activate
    - deactivate
    """

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        configuration_id = int(
            data.get('configuration_id')
        )

        action = str(
            data.get('action')
            or ''
        ).strip().lower()

        comment = str(
            data.get('comment')
            or ''
        ).strip()

        allowed_actions = {
            'approve',
            'reject',
            'activate',
            'deactivate',
        }

        if action not in allowed_actions:
            raise ValidationError(
                'Acción no válida.'
            )

        with transaction.atomic():
            configuration = (
                _get_configuration(
                    configuration_id
                )
            )

            # ==================================================
            # APROBAR
            # ==================================================

            if action == 'approve':
                if not configuration.is_active:
                    raise ValidationError(
                        'No se puede aprobar una '
                        'configuración inactiva.'
                    )

                cost_center = (
                    configuration.cost_center
                )

                if (
                    not cost_center.is_active
                    or cost_center.is_removed
                ):
                    raise ValidationError(
                        'El centro de costo no está activo.'
                    )

                if (
                    not cost_center.delivery_site
                    or
                    not cost_center.delivery_site.is_active
                    or
                    cost_center.delivery_site.is_removed
                ):
                    raise ValidationError(
                        'El sitio de entrega no está activo.'
                    )

                active_routes = list(
                    ClientProjectRoute.objects
                    .filter(
                        configuration=configuration,
                        is_removed=False,
                        is_active=True,
                    )
                )

                if not active_routes:
                    raise ValidationError(
                        'La configuración necesita al menos '
                        'una ruta operativa activa antes de '
                        'ser aprobada.'
                    )

                for route in active_routes:
                    has_cells = (
                        ClientProjectRouteWorkCell.objects
                        .filter(
                            route=route,
                            is_removed=False,
                            is_active=True,
                        )
                        .exists()
                    )

                    if not has_cells:
                        raise ValidationError(
                            (
                                f'La ruta {route.pk} '
                                'no tiene células autorizadas.'
                            )
                        )

                configuration.validation_status = (
                    'APPROVED'
                )

                configuration.validated_at = (
                    timezone.now()
                )

                configuration.validated_by_username = (
                    actor
                )

                configuration.validation_comment = (
                    comment
                    or 'Configuración aprobada.'
                )

                reason = (
                    'Configuración comercial aprobada '
                    'desde Portal'
                )

            # ==================================================
            # RECHAZAR
            # ==================================================

            elif action == 'reject':
                if not comment:
                    raise ValidationError(
                        'Debe indicar el motivo del rechazo.'
                    )

                configuration.validation_status = (
                    'REJECTED'
                )

                configuration.validated_at = (
                    timezone.now()
                )

                configuration.validated_by_username = (
                    actor
                )

                configuration.validation_comment = (
                    comment
                )

                reason = (
                    'Configuración comercial rechazada '
                    'desde Portal'
                )

            # ==================================================
            # DESACTIVAR
            # ==================================================

            elif action == 'deactivate':
                configuration.is_active = False

                reason = (
                    'Configuración comercial desactivada '
                    'desde Portal'
                )

            # ==================================================
            # ACTIVAR
            # ==================================================

            else:
                configuration.is_active = True

                # Reactivar exige nueva revisión.
                configuration.validation_status = (
                    'PENDING'
                )

                configuration.validated_at = None
                configuration.validated_by_username = None

                configuration.validation_comment = (
                    'Reactivada. Pendiente de nueva '
                    'validación.'
                )

                reason = (
                    'Configuración comercial reactivada '
                    'desde Portal'
                )

            _save_with_history(
                configuration,
                actor_username=actor,
                reason=reason,
            )

        return JsonResponse(
            {
                'success': True,
                'configuration_id': (
                    configuration.pk
                ),
                'validation_status': (
                    configuration.validation_status
                ),
                'is_active': (
                    configuration.is_active
                ),
            }
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)


# ============================================================
# CREAR / EDITAR RUTA
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def route_save(request):
    """
    Crear:
    {
        "configuration_id": 1,
        "udn_id": 2,
        "work_cell_ids": [4, 7],
        "notes": "",
        "actor_username": "usuario.portal"
    }

    Editar:
    {
        "route_id": 2,
        "configuration_id": 1,
        "udn_id": 2,
        "work_cell_ids": [4, 7],
        "notes": "",
        "actor_username": "usuario.portal"
    }

    IMPORTANTE:
    No validamos cell.udn == route.udn.
    La autorización cruzada entre UDN está permitida.
    """

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        route_id = data.get('route_id')

        configuration_id = int(
            data.get('configuration_id')
        )

        udn_id = int(
            data.get('udn_id')
        )

        raw_cell_ids = (
            data.get('work_cell_ids')
            or []
        )

        if not isinstance(raw_cell_ids, list):
            raise ValidationError(
                'work_cell_ids debe ser una lista.'
            )

        cell_ids = []

        for value in raw_cell_ids:
            cell_id = int(value)

            if cell_id not in cell_ids:
                cell_ids.append(cell_id)

        if not cell_ids:
            raise ValidationError(
                'Seleccione al menos una célula '
                'autorizada para la ruta.'
            )

        notes = str(
            data.get('notes')
            or ''
        ).strip()

        with transaction.atomic():
            configuration = (
                _get_configuration(
                    configuration_id
                )
            )

            if not configuration.is_active:
                raise ValidationError(
                    'No se pueden editar rutas de una '
                    'configuración inactiva.'
                )

            udn = get_object_or_404(
                UDN,
                pk=udn_id,
                is_removed=False,
            )

            work_cells = list(
                WorkCell.objects
                .filter(
                    pk__in=cell_ids,
                    is_removed=False,
                )
                .order_by('name')
            )

            found_ids = {
                cell.pk
                for cell in work_cells
            }

            missing_ids = (
                set(cell_ids)
                - found_ids
            )

            if missing_ids:
                raise ValidationError(
                    (
                        'Una o más células no existen: '
                        + ', '.join(
                            str(x)
                            for x
                            in sorted(missing_ids)
                        )
                    )
                )

            # ==================================================
            # EDITAR RUTA
            # ==================================================

            if route_id:
                route = get_object_or_404(
                    ClientProjectRoute,
                    pk=int(route_id),
                    configuration=configuration,
                    is_removed=False,
                )

                duplicate = (
                    ClientProjectRoute.objects
                    .filter(
                        configuration=configuration,
                        udn=udn,
                        is_removed=False,
                        is_active=True,
                    )
                    .exclude(pk=route.pk)
                    .exists()
                )

                if duplicate:
                    raise ValidationError(
                        'Ya existe una ruta activa para '
                        'esa UDN en esta configuración.'
                    )

                route.udn = udn
                route.notes = notes or None

                _save_with_history(
                    route,
                    actor_username=actor,
                    reason=(
                        'Ruta comercial actualizada '
                        'desde Portal'
                    ),
                )

                created = False

            # ==================================================
            # NUEVA RUTA
            # ==================================================

            else:
                duplicate = (
                    ClientProjectRoute.objects
                    .filter(
                        configuration=configuration,
                        udn=udn,
                        is_removed=False,
                        is_active=True,
                    )
                    .exists()
                )

                if duplicate:
                    raise ValidationError(
                        'Ya existe una ruta activa para '
                        'esa UDN en esta configuración.'
                    )

                route = ClientProjectRoute(
                    configuration=configuration,
                    udn=udn,
                    notes=notes or None,
                    is_active=True,
                )

                _save_with_history(
                    route,
                    actor_username=actor,
                    reason=(
                        'Ruta comercial creada '
                        'desde Portal'
                    ),
                )

                created = True

            # ==================================================
            # CÉLULAS AUTORIZADAS
            # ==================================================

            current_assignments = {
                item.work_cell_id: item
                for item in (
                    ClientProjectRouteWorkCell.objects
                    .filter(
                        route=route,
                        is_removed=False,
                    )
                )
            }

            # Desactivar las que ya no fueron elegidas.
            for cell_id, assignment in (
                current_assignments.items()
            ):
                should_be_active = (
                    cell_id in found_ids
                )

                if (
                    assignment.is_active
                    != should_be_active
                ):
                    assignment.is_active = (
                        should_be_active
                    )

                    _save_with_history(
                        assignment,
                        actor_username=actor,
                        reason=(
                            'Autorización de célula '
                            'actualizada desde Portal'
                        ),
                    )

            # Crear/reactivar seleccionadas.
            for work_cell in work_cells:
                assignment = (
                    current_assignments.get(
                        work_cell.pk
                    )
                )

                if assignment:
                    if not assignment.is_active:
                        assignment.is_active = True

                        _save_with_history(
                            assignment,
                            actor_username=actor,
                            reason=(
                                'Célula reactivada '
                                'en ruta desde Portal'
                            ),
                        )

                    continue

                assignment = (
                    ClientProjectRouteWorkCell(
                        route=route,
                        work_cell=work_cell,
                        is_active=True,
                    )
                )

                _save_with_history(
                    assignment,
                    actor_username=actor,
                    reason=(
                        'Célula agregada a ruta '
                        'desde Portal'
                    ),
                )

            # ==================================================
            # LEGACY TRANSITORIO
            # ==================================================
            #
            # Route es la autoridad.
            # Estos campos se mantienen sincronizados únicamente
            # para compatibilidad con código viejo del CRM/Portal.
            # ==================================================

            if hasattr(
                configuration,
                'udn_id',
            ):
                configuration.udn = udn

            if (
                hasattr(
                    configuration,
                    'work_cell_id',
                )
                and work_cells
            ):
                configuration.work_cell = (
                    work_cells[0]
                )

            _save_with_history(
                configuration,
                actor_username=actor,
                reason=(
                    'Compatibilidad legacy sincronizada '
                    'desde ruta comercial'
                ),
            )

            _reset_validation_if_needed(
                configuration,
                actor_username=actor,
                reason=(
                    'Validación reiniciada por '
                    'modificación de ruta'
                ),
            )

        return JsonResponse(
            {
                'success': True,
                'created': created,
                'route': {
                    'id': route.pk,
                    'configuration_id': (
                        route.configuration_id
                    ),
                    'udn_id': route.udn_id,
                    'udn_name': route.udn.name,
                    'work_cell_ids': [
                        cell.pk
                        for cell in work_cells
                    ],
                    'is_active': route.is_active,
                },
            },
            status=201 if created else 200,
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)

    except IntegrityError as exc:
        return JsonResponse(
            {
                'success': False,
                'error': (
                    'La ruta viola una restricción '
                    'de integridad.'
                ),
                'detail': str(exc),
            },
            status=400,
        )


# ============================================================
# ACTIVAR / DESACTIVAR RUTA
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def route_state(request):
    """
    {
        "route_id": 2,
        "action": "deactivate",
        "actor_username": "usuario.portal"
    }
    """

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        route_id = int(
            data.get('route_id')
        )

        action = str(
            data.get('action')
            or ''
        ).strip().lower()

        if action not in {
            'activate',
            'deactivate',
        }:
            raise ValidationError(
                'Acción de ruta no válida.'
            )

        with transaction.atomic():
            route = get_object_or_404(
                ClientProjectRoute.objects
                .select_related(
                    'configuration',
                    'udn',
                ),
                pk=route_id,
                is_removed=False,
            )

            configuration = (
                route.configuration
            )

            if action == 'activate':
                duplicate = (
                    ClientProjectRoute.objects
                    .filter(
                        configuration=configuration,
                        udn=route.udn,
                        is_removed=False,
                        is_active=True,
                    )
                    .exclude(pk=route.pk)
                    .exists()
                )

                if duplicate:
                    raise ValidationError(
                        'Ya existe otra ruta activa '
                        'para esa UDN.'
                    )

                has_cells = (
                    ClientProjectRouteWorkCell.objects
                    .filter(
                        route=route,
                        is_removed=False,
                        is_active=True,
                    )
                    .exists()
                )

                if not has_cells:
                    raise ValidationError(
                        'No se puede activar una ruta '
                        'sin células autorizadas.'
                    )

                route.is_active = True

                reason = (
                    'Ruta comercial activada '
                    'desde Portal'
                )

            else:
                route.is_active = False

                reason = (
                    'Ruta comercial desactivada '
                    'desde Portal'
                )

            _save_with_history(
                route,
                actor_username=actor,
                reason=reason,
            )

            _reset_validation_if_needed(
                configuration,
                actor_username=actor,
                reason=(
                    'Validación reiniciada por cambio '
                    'de estado de ruta'
                ),
            )

        return JsonResponse(
            {
                'success': True,
                'route_id': route.pk,
                'is_active': route.is_active,
                'configuration_id': (
                    configuration.pk
                ),
                'configuration_status': (
                    configuration.validation_status
                ),
            }
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)


# ============================================================
# HEALTH CHECK
# ============================================================

def health(request):
    if not _authorized(request):
        return JsonResponse(
            {
                'success': False,
                'error': 'No autorizado.',
            },
            status=401,
        )

    return JsonResponse(
        {
            'success': True,
            'service': (
                'commercial-config-internal-api'
            ),
        }
    )