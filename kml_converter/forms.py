from django import forms

class XYForm(forms.Form):
    x = forms.FloatField(label='Y')
    y = forms.FloatField(label='X')
