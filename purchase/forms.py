from django import forms
from purchase.models import PurchaseStatus


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = PurchaseStatus
        fields = [
            'purchase_status_type', 'opportunity'
        ]