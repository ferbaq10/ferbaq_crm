from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from redis.exceptions import ConnectionError as RedisConnectionError
import logging

from purchase.models import PurchaseStatus
from catalog.models import PurchaseStatusType
from catalog.constants import OpportunityFilters, StatusIDs, CurrencyIDs

logger = logging.getLogger(__name__)

CATALOG_MODELS = ['Opportunity', 'CommercialActivity']
APP_NAME = 'opportunity'

def clear_list_cache_for(model_name, prefix="catalog"):
    try:
        cache_key = f"{prefix}_{model_name}ViewSet_list"

        print(f"🚨 Intentando invalidar cache: {cache_key}")
        cache.delete(cache_key)
        print(f"Cache invalidado: {cache_key}")
    except RedisConnectionError:
        logger.warning(f"Redis no disponible (clear cache signal): {model_name}")

def create_purchase_status_if_eligible(opportunity):
    """
    Crea PurchaseStatus automáticamente si la oportunidad cumple criterios
    """
    print(f"🔍 === EVALUANDO OPORTUNIDAD {opportunity.id}: {opportunity.name} ===")
    
    try:
        # Verificar si ya tiene PurchaseStatus
        if hasattr(opportunity, 'purchase_data') and opportunity.purchase_data:
            print(f"✅ Oportunidad {opportunity.id} YA tiene PurchaseStatus: {opportunity.purchase_data.purchase_status_type.name}")
            return
    except Exception as e:
        print(f"🔍 No tiene purchase_data (normal): {e}")
        pass  # No tiene purchase_data, continuar
    
    # ✅ VERIFICAR CRITERIOS DETALLADAMENTE
    print(f"📊 VERIFICANDO CRITERIOS:")
    print(f"   - Closing %: {opportunity.closing_percentage} (req: >= {OpportunityFilters.CLOSING_PERCENTAGE})")
    print(f"   - Status ID: {opportunity.status_opportunity_id} (req: {StatusIDs.NEGOTIATING} o {StatusIDs.WON})")
    print(f"   - Currency: {opportunity.currency_id}, Amount: {opportunity.amount}")
    
    # Verificar criterios uno por uno
    closing_ok = opportunity.closing_percentage and opportunity.closing_percentage >= OpportunityFilters.CLOSING_PERCENTAGE
    status_ok = opportunity.status_opportunity_id in [StatusIDs.NEGOTIATING, StatusIDs.WON]
    
    amount_ok = False
    if opportunity.currency_id == CurrencyIDs.USD:
        amount_ok = opportunity.amount >= OpportunityFilters.AMOUNT_USD
        print(f"   - Amount USD: {opportunity.amount} >= {OpportunityFilters.AMOUNT_USD} = {amount_ok}")
    elif opportunity.currency_id == CurrencyIDs.MN:
        amount_ok = opportunity.amount >= OpportunityFilters.AMOUNT_MN
        print(f"   - Amount MN: {opportunity.amount} >= {OpportunityFilters.AMOUNT_MN} = {amount_ok}")
    
    meets_criteria = closing_ok and status_ok and amount_ok
    
    print(f"📊 RESUMEN CRITERIOS:")
    print(f"   ✅ Closing: {closing_ok}")
    print(f"   ✅ Status: {status_ok}")
    print(f"   ✅ Amount: {amount_ok}")
    print(f"   🎯 CUMPLE TODOS: {meets_criteria}")
    
    if meets_criteria:
        try:
            print(f"🔄 Intentando crear PurchaseStatus...")
            
            # Obtener estado "Pendiente" (ID 1)
            pending_status = PurchaseStatusType.objects.get(id=1)
            print(f"✅ Estado pendiente encontrado: {pending_status.name}")
            
            # Crear PurchaseStatus
            purchase_status, created = PurchaseStatus.objects.get_or_create(
                opportunity=opportunity,
                defaults={'purchase_status_type': pending_status}
            )
            
            if created:
                print(f"🎉 PurchaseStatus CREADO automáticamente para: {opportunity.name} (ID: {opportunity.id})")
            else:
                print(f"🔍 PurchaseStatus ya existía para: {opportunity.name} (ID: {opportunity.id})")
                
        except Exception as e:
            print(f"❌ Error creando PurchaseStatus para {opportunity.name}: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Oportunidad {opportunity.id} NO cumple criterios para PurchaseStatus")
    
    print(f"🔍 === FIN EVALUACIÓN OPORTUNIDAD {opportunity.id} ===")

def register_catalog_signals():
    for model_name in CATALOG_MODELS:
        model = apps.get_model(APP_NAME, model_name)

        def make_handler(model_name):
            def handler(sender, **kwargs):
                print(f"📌 Señal post_save/post_delete activada para {model_name}")
                
                if model_name == 'Opportunity':
                    instance = kwargs.get('instance')
                    if instance:
                        print(f"🎯 EJECUTANDO verificación PurchaseStatus para oportunidad {instance.id}...")
                        create_purchase_status_if_eligible(instance)
                        
                        # ✅ LIMPIAR CACHE DE PURCHASES específicamente
                        purchase_cache_keys = [
                            "catalog_PurchaseViewSet_list",
                            "purchase_PurchaseViewSet_list",
                            "PurchaseViewSet_list"
                        ]
                        for key in purchase_cache_keys:
                            cache.delete(key)
                            print(f"🗑️ Cache PURCHASE invalidado: {key}")
                
                clear_list_cache_for(model_name)
            return handler

        handler = make_handler(model_name)

        try:
            # Testea disponibilidad de Redis al momento de registrar señales
            cache.set("signal_test", "1", timeout=1)
            post_save.connect(handler, sender=model, weak=False)
            post_delete.connect(handler, sender=model, weak=False)
        except RedisConnectionError:
            logger.warning(f"Redis no disponible al registrar señales para {model_name}. Señales omitidas.")
        except Exception as e:
            logger.error(f"Error registrando signals para {model_name}: {e}")

# ✅ SIGNAL ADICIONAL DIRECTO (por si el anterior falla)
from django.dispatch import receiver

@receiver(post_save, sender=apps.get_model('opportunity', 'Opportunity'))
def direct_purchase_status_signal(sender, instance, **kwargs):
    """Signal directo adicional para asegurar que funcione"""
    print(f"🔥 SIGNAL DIRECTO ejecutado para {instance.name} (ID: {instance.id})")
    create_purchase_status_if_eligible(instance)