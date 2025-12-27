from django import forms

class XYForm(forms.Form):
    x = forms.FloatField(label='Y')
    y = forms.FloatField(label='X')


class AssetForm(forms.Form):
    bitcoin = forms.FloatField()
    altcoin = forms.FloatField()
    silver = forms.FloatField()
    mwig40 = forms.FloatField()
    tsmc = forms.FloatField()
    cameco = forms.FloatField()
