from django import forms
from django.core.exceptions import ValidationError
from .models import Crop, Farm, Season, Planting, SeasonReview


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
            'name': forms.TextInput(attrs={'class': 'fp-input'}),
            'location_description': forms.TextInput(attrs={'class': 'fp-input'}),
            'total_land_ha': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'cultivated_land_ha': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'irrigation_type': forms.Select(attrs={'class': 'fp-input'}),
            'water_notes': forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
            'soil_type': forms.Select(attrs={'class': 'fp-input'}),
            'soil_notes': forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
            'seasonal_budget_mwk': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0'}),
            'available_labour_persons': forms.NumberInput(attrs={'class': 'fp-input', 'min': '0'}),
            'labour_notes': forms.Textarea(attrs={'class': 'fp-input', 'rows': 3}),
        }


class SeasonForm(forms.ModelForm):
    """Create or edit a growing season for a farm."""

    class Meta:
        model = Season
        fields = ['name', 'start_date', 'end_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'fp-input', 'placeholder': 'e.g. 2024/25 Rainy Season'}),
            'start_date': forms.DateInput(attrs={'class': 'fp-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'fp-input', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'fp-input', 'rows': 3, 'placeholder': 'Key weather events, dry spells, or season observations...'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be on or after start date.')
        return cleaned_data


class PlantingForm(forms.ModelForm):
    """Create or edit a single crop planting within a season."""

    class Meta:
        model = Planting
        fields = [
            'season',
            'crop',
            'area_ha',
            'planting_date',
            'harvest_date',
            'yield_kg',
            'production_cost_mwk',
            'selling_price_mwk_per_kg',
            'revenue_mwk',
            'notes',
        ]
        widgets = {
            'season': forms.Select(attrs={'class': 'fp-input'}),
            'crop': forms.Select(attrs={'class': 'fp-input'}),
            'area_ha': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0.01', 'placeholder': 'e.g. 1.20'}),
            'planting_date': forms.DateInput(attrs={'class': 'fp-input', 'type': 'date'}),
            'harvest_date': forms.DateInput(attrs={'class': 'fp-input', 'type': 'date'}),
            'yield_kg': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0', 'placeholder': 'e.g. 2400'}),
            'production_cost_mwk': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0', 'placeholder': 'e.g. 210000'}),
            'selling_price_mwk_per_kg': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0', 'placeholder': 'e.g. 350'}),
            'revenue_mwk': forms.NumberInput(attrs={'class': 'fp-input', 'step': '0.01', 'min': '0', 'placeholder': 'e.g. 840000'}),
            'notes': forms.Textarea(attrs={'class': 'fp-input', 'rows': 3, 'placeholder': 'Seed variety, fertilizer used, pest notes, selling market...'}),
        }

    def __init__(self, *args, farm=None, **kwargs):
        super().__init__(*args, **kwargs)
        if farm:
            self.fields['season'].queryset = Season.objects.filter(farm=farm)
            self.fields['crop'].queryset = Crop.objects.all().order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        planting_date = cleaned_data.get('planting_date')
        harvest_date = cleaned_data.get('harvest_date')
        area_ha = cleaned_data.get('area_ha')

        if planting_date and harvest_date and harvest_date < planting_date:
            self.add_error('harvest_date', 'Harvest date must be on or after planting date.')

        if area_ha is not None and area_ha <= 0:
            self.add_error('area_ha', 'Planted area must be greater than 0 hectares.')

        return cleaned_data


class SeasonReviewForm(forms.ModelForm):
    """Create or update qualitative review, satisfaction, and lessons learned for a season."""

    class Meta:
        model = SeasonReview
        fields = [
            'associated_plan',
            'overall_satisfaction',
            'lessons_learned',
            'weather_assessment',
            'market_assessment',
        ]
        widgets = {
            'associated_plan': forms.Select(attrs={'class': 'fp-input'}),
            'overall_satisfaction': forms.Select(attrs={'class': 'fp-input'}),
            'lessons_learned': forms.Textarea(attrs={
                'class': 'fp-input', 'rows': 4,
                'placeholder': 'What worked well? What agronomic tactics succeeded or failed (e.g. planting dates, seed variety, spacing)?'
            }),
            'weather_assessment': forms.Textarea(attrs={
                'class': 'fp-input', 'rows': 3,
                'placeholder': 'Rainfall patterns, dry spell duration, temperature anomalies, flood or heat impact.'
            }),
            'market_assessment': forms.Textarea(attrs={
                'class': 'fp-input', 'rows': 3,
                'placeholder': 'Prices realized, buyer access (ADMARC, local vendors, aggregators), payment terms.'
            }),
        }

    def __init__(self, *args, farm=None, **kwargs):
        super().__init__(*args, **kwargs)
        if farm:
            from planner.models import Plan
            self.fields['associated_plan'].queryset = Plan.objects.filter(farm=farm).order_by('-created_at')
            self.fields['associated_plan'].empty_label = "— None / Not Linked —"
