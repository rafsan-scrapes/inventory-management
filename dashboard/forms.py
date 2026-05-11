from django import forms
from .models import Part


class PartForm(forms.ModelForm):
    """
    Handles all non-FK fields only.
    product_type, brand, and part_type are resolved by the view's smart-dropdown
    logic and set on the instance manually before saving — they do NOT belong here.

    product_model is a special field: it lets users edit the ProductType's
    product_model from the part form, so it's declared here (not in Meta.fields).
    """

    product_model = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. RS70F65Q1BLV"}),
        label="Product Model",
    )

    class Meta:
        model = Part
        fields = [
            "image",
            "total_new",
            "total_used",
            "size_kg",
            "model_number",
            "shelf_number",
            "column_number",
            "row_number",
            "notes",
        ]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
            "total_new": forms.NumberInput(attrs={"min": "0", "placeholder": "0"}),
            "total_used": forms.NumberInput(attrs={"min": "0", "placeholder": "0"}),
            "size_kg": forms.NumberInput(
                attrs={"min": "0", "step": "0.01", "placeholder": "e.g. 5.5"}
            ),
            "model_number": forms.TextInput(attrs={"placeholder": "e.g. WAE28468GB"}),
            "shelf_number": forms.NumberInput(
                attrs={"min": "1", "placeholder": "e.g. 2"}
            ),
            "column_number": forms.TextInput(attrs={"placeholder": "e.g. 3, right"}),
            "row_number": forms.TextInput(attrs={"placeholder": "e.g. 1, left"}),
            "notes": forms.Textarea(
                attrs={
                    "rows": "3",
                    "placeholder": "Any additional notes about condition, origin, etc.",
                }
            ),
        }
