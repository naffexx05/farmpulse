from django import forms
from .models import Crop, Farm


class FarmForm(forms.ModelForm):
    """Edit or create a Farm. Owner is set by the view, not the form."""

    preferred_crops = forms.ModelMultipleChoiceField(
        queryset=Crop.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'accent-leaf w-4 h-4 rounded',
        }),
        required=False,
        label='Preferred crops',
    )

    class Meta:
        model = Farm
        fields = [
            'name',
            'location_description',
            'total_land_ha',
            'cultivated_land_ha',
            'irrigation_type',
            'water_notes',
            'soil_type',
            'soil_notes',
            'seasonal_budget_mwk',
            'available_labour_persons',
            'labour_notes',
            'preferred_crops',
        ]
        widgets = {
            'name':                 forms.TextInput(attrs={'class': 'fp-input'}),
            'location_description': forms.TextInput(attrs={'class': 'fp-input'}),
            'total_land_ha':        forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'cultivated_land_ha':   forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'irrigation_type':      forms.Select(attrs={'class': 'fp-input'}),
            'water_notes':          forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
            'soil_type':            forms.Select(attrs={'class': 'fp-input'}),
            'soil_notes':           forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
            'seasonal_budget_mwk':  forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'available_labour_persons': forms.NumberInput(attrs={'class': 'fp-input', 'min': '0'}),
            'labour_notes':         forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
        }