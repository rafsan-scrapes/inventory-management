from django import forms
from .models import PartType, Brand, ProductType, Part


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = [
            "product_type",
            "brand",
            "part_type",
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
