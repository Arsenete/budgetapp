from django import forms
from .models import *

class budgetForm(forms.ModelForm):
    class Meta:
        model = Valeur_budget
        fields = ['budget_initial']  # Les champs que vous souhaitez inclure dans le formulaire