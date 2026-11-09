class StatusIDs:
    SEND = 3
    NEGOTIATING = 4
    TO_CLOSE = 7  # 'Por cerrar' (va después de Negociando y antes de Ganada/Perdida)
    WON = 5
    LOST = 6

class CurrencyIDs:
    MN = 1
    USD = 2

class OpportunityFilters:
    CLOSING_PERCENTAGE = 80
    AMOUNT_MN = 250000
    AMOUNT_USD = 13000

class StatusPurchaseTypeIDs:
    PENDING = 1