from django import forms

class XYForm(forms.Form):
    x = forms.FloatField(label='X')
    y = forms.FloatField(label='Y')



class DepositForm(forms.Form):
    deposit = forms.IntegerField(label="Total deposit (PLN)")

