import json
import secrets

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from simple_history.utils import update_change_reason

from .models import (
    ClientProjectConfiguration,
    CostCenter,
    DeliverySite,
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
            'El cuerpo debe ser JSON válido.'
        )


def _actor_username(data):

    return str(
        data.get('actor_username')
        or 'portal-ferbaq'
    ).strip()[:150]


def _history_user(username):

    if not username:
        return None

    User = get_user_model()

    return (
        User.objects
        .filter(username=username)
        .first()
    )


def _save_with_history(
    instance,
    *,
    actor_username,
    reason,
):

    user = _history_user(
        actor_username
    )

    if user is not None:
        instance._history_user = user

    instance.full_clean()
    instance.save()

    try:
        update_change_reason(
            instance,
            reason[:100],
        )
    except Exception:
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


def _reset_approved_configurations(
    *,
    cost_center_ids,
    actor_username,
    reason,
):
    """
    Si cambia un maestro utilizado por configuraciones aprobadas,
    esas configuraciones regresan a PENDING.
    """

    ids = list(
        {
            int(item)
            for item in cost_center_ids
            if item
        }
    )

    if not ids:
        return 0

    queryset = (
        ClientProjectConfiguration.objects
        .filter(
            cost_center_id__in=ids,
            is_removed=False,
            validation_status='APPROVED',
        )
    )

    total = 0

    for configuration in queryset:

        configuration.validation_status = 'PENDING'
        configuration.validated_at = None
        configuration.validated_by_username = None
        configuration.validation_comment = (
            'Validación reiniciada automáticamente '
            'por modificación de maestro comercial.'
        )

        _save_with_history(
            configuration,
            actor_username=actor_username,
            reason=reason,
        )

        total += 1

    return total


# ============================================================
# SITIOS DE ENTREGA
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def delivery_site_save(request):

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        site_id = (
            data.get('site_id')
            or None
        )

        code = str(
            data.get('code')
            or ''
        ).strip().upper()

        name = str(
            data.get('name')
            or ''
        ).strip()

        address = str(
            data.get('address')
            or ''
        ).strip()

        postal_code = str(
            data.get('postal_code')
            or ''
        ).strip()

        notes = str(
            data.get('notes')
            or ''
        ).strip()

        if not code:
            raise ValidationError(
                'El código del sitio es obligatorio.'
            )

        if not name:
            raise ValidationError(
                'El nombre del sitio es obligatorio.'
            )

        with transaction.atomic():

            duplicate_code = (
                DeliverySite.objects
                .filter(
                    code__iexact=code,
                    is_removed=False,
                )
            )

            duplicate_name = (
                DeliverySite.objects
                .filter(
                    name__iexact=name,
                    is_removed=False,
                )
            )

            if site_id:

                site = get_object_or_404(
                    DeliverySite,
                    pk=int(site_id),
                    is_removed=False,
                )

                duplicate_code = (
                    duplicate_code
                    .exclude(pk=site.pk)
                )

                duplicate_name = (
                    duplicate_name
                    .exclude(pk=site.pk)
                )

                if duplicate_code.exists():
                    raise ValidationError(
                        'Ya existe otro sitio con ese código.'
                    )

                if duplicate_name.exists():
                    raise ValidationError(
                        'Ya existe otro sitio con ese nombre.'
                    )

                changed = any([
                    site.code != code,
                    site.name != name,
                    (site.address or '') != address,
                    (site.postal_code or '') != postal_code,
                    (site.notes or '') != notes,
                ])

                site.code = code
                site.name = name
                site.address = address or None
                site.postal_code = postal_code or None
                site.notes = notes or None

                _save_with_history(
                    site,
                    actor_username=actor,
                    reason=(
                        'Sitio de entrega actualizado '
                        'desde Portal'
                    ),
                )

                created = False

                if changed:

                    cost_center_ids = list(
                        CostCenter.objects
                        .filter(
                            delivery_site=site,
                            is_removed=False,
                        )
                        .values_list(
                            'id',
                            flat=True,
                        )
                    )

                    _reset_approved_configurations(
                        cost_center_ids=cost_center_ids,
                        actor_username=actor,
                        reason=(
                            'Validación reiniciada por '
                            'cambio de sitio de entrega'
                        ),
                    )

            else:

                if duplicate_code.exists():
                    raise ValidationError(
                        'Ya existe un sitio con ese código.'
                    )

                if duplicate_name.exists():
                    raise ValidationError(
                        'Ya existe un sitio con ese nombre.'
                    )

                site = DeliverySite(
                    code=code,
                    name=name,
                    address=address or None,
                    postal_code=postal_code or None,
                    notes=notes or None,
                    is_active=True,
                )

                _save_with_history(
                    site,
                    actor_username=actor,
                    reason=(
                        'Sitio de entrega creado '
                        'desde Portal'
                    ),
                )

                created = True

        return JsonResponse(
            {
                'success': True,
                'created': created,
                'site': {
                    'id': site.pk,
                    'code': site.code,
                    'name': site.name,
                    'is_active': site.is_active,
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
                    'No fue posible guardar el sitio '
                    'por una restricción de integridad.'
                ),
                'detail': str(exc),
            },
            status=400,
        )


@csrf_exempt
@require_POST
@internal_api_required
def delivery_site_state(request):

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        site_id = int(
            data.get('site_id')
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
                'Acción no válida.'
            )

        with transaction.atomic():

            site = get_object_or_404(
                DeliverySite,
                pk=site_id,
                is_removed=False,
            )

            if action == 'deactivate':

                active_centers = (
                    CostCenter.objects
                    .filter(
                        delivery_site=site,
                        is_removed=False,
                        is_active=True,
                    )
                    .exists()
                )

                if active_centers:
                    raise ValidationError(
                        'No se puede desactivar el sitio '
                        'mientras tenga centros de costo '
                        'activos asociados.'
                    )

                site.is_active = False

                reason = (
                    'Sitio de entrega desactivado '
                    'desde Portal'
                )

            else:

                site.is_active = True

                reason = (
                    'Sitio de entrega activado '
                    'desde Portal'
                )

            _save_with_history(
                site,
                actor_username=actor,
                reason=reason,
            )

        return JsonResponse(
            {
                'success': True,
                'site_id': site.pk,
                'is_active': site.is_active,
            }
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)


# ============================================================
# CENTROS DE COSTO
# ============================================================

@csrf_exempt
@require_POST
@internal_api_required
def cost_center_save(request):

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        cost_center_id = (
            data.get('cost_center_id')
            or None
        )

        code = str(
            data.get('code')
            or ''
        ).strip().upper()

        name = str(
            data.get('name')
            or ''
        ).strip()

        delivery_site_id = int(
            data.get('delivery_site_id')
        )

        default_credit_days = int(
            data.get('default_credit_days')
        )

        notes = str(
            data.get('notes')
            or ''
        ).strip()

        if not code:
            raise ValidationError(
                'El código del centro de costo es obligatorio.'
            )

        if default_credit_days < 0:
            raise ValidationError(
                'Los días de crédito no pueden ser negativos.'
            )

        with transaction.atomic():

            site = get_object_or_404(
                DeliverySite,
                pk=delivery_site_id,
                is_removed=False,
                is_active=True,
            )

            duplicate = (
                CostCenter.objects
                .filter(
                    code__iexact=code,
                    is_removed=False,
                )
            )

            if cost_center_id:

                cost_center = get_object_or_404(
                    CostCenter,
                    pk=int(cost_center_id),
                    is_removed=False,
                )

                duplicate = (
                    duplicate
                    .exclude(pk=cost_center.pk)
                )

                if duplicate.exists():
                    raise ValidationError(
                        'Ya existe otro centro de costo '
                        'con ese código.'
                    )

                changed = any([
                    cost_center.code != code,
                    (cost_center.name or '') != name,
                    cost_center.delivery_site_id != site.pk,
                    cost_center.default_credit_days
                    != default_credit_days,
                    (cost_center.notes or '') != notes,
                ])

                cost_center.code = code
                cost_center.name = name or None
                cost_center.delivery_site = site
                cost_center.default_credit_days = (
                    default_credit_days
                )
                cost_center.notes = notes or None

                _save_with_history(
                    cost_center,
                    actor_username=actor,
                    reason=(
                        'Centro de costo actualizado '
                        'desde Portal'
                    ),
                )

                created = False

                if changed:

                    _reset_approved_configurations(
                        cost_center_ids=[
                            cost_center.pk
                        ],
                        actor_username=actor,
                        reason=(
                            'Validación reiniciada por '
                            'cambio de centro de costo'
                        ),
                    )

            else:

                if duplicate.exists():
                    raise ValidationError(
                        'Ya existe un centro de costo '
                        'con ese código.'
                    )

                cost_center = CostCenter(
                    code=code,
                    name=name or None,
                    delivery_site=site,
                    default_credit_days=(
                        default_credit_days
                    ),
                    notes=notes or None,
                    is_active=True,
                )

                _save_with_history(
                    cost_center,
                    actor_username=actor,
                    reason=(
                        'Centro de costo creado '
                        'desde Portal'
                    ),
                )

                created = True

        return JsonResponse(
            {
                'success': True,
                'created': created,
                'cost_center': {
                    'id': cost_center.pk,
                    'code': cost_center.code,
                    'name': cost_center.name,
                    'delivery_site_id': (
                        cost_center.delivery_site_id
                    ),
                    'default_credit_days': (
                        cost_center.default_credit_days
                    ),
                    'is_active': (
                        cost_center.is_active
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
                    'No fue posible guardar el centro '
                    'de costo por una restricción '
                    'de integridad.'
                ),
                'detail': str(exc),
            },
            status=400,
        )


@csrf_exempt
@require_POST
@internal_api_required
def cost_center_state(request):

    try:
        data = _json_body(request)
        actor = _actor_username(data)

        cost_center_id = int(
            data.get('cost_center_id')
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
                'Acción no válida.'
            )

        with transaction.atomic():

            cost_center = get_object_or_404(
                CostCenter.objects
                .select_related(
                    'delivery_site'
                ),
                pk=cost_center_id,
                is_removed=False,
            )

            if action == 'activate':

                if (
                    not cost_center.delivery_site
                    or
                    not cost_center.delivery_site.is_active
                    or
                    cost_center.delivery_site.is_removed
                ):
                    raise ValidationError(
                        'No se puede activar el centro '
                        'porque su sitio de entrega '
                        'está inactivo.'
                    )

                cost_center.is_active = True

                reason = (
                    'Centro de costo activado '
                    'desde Portal'
                )

            else:

                cost_center.is_active = False

                reason = (
                    'Centro de costo desactivado '
                    'desde Portal'
                )

            _save_with_history(
                cost_center,
                actor_username=actor,
                reason=reason,
            )

            _reset_approved_configurations(
                cost_center_ids=[
                    cost_center.pk
                ],
                actor_username=actor,
                reason=(
                    'Validación reiniciada por cambio '
                    'de estado de centro de costo'
                ),
            )

        return JsonResponse(
            {
                'success': True,
                'cost_center_id': (
                    cost_center.pk
                ),
                'is_active': (
                    cost_center.is_active
                ),
            }
        )

    except (
        TypeError,
        ValueError,
        ValidationError,
    ) as exc:
        return _validation_error_response(exc)