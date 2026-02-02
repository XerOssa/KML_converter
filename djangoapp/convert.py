# djangoapp/convert.py
from django.shortcuts import render
from .forms import XYForm
from pyproj import Proj, transform

proj_2000 = Proj(init='epsg:2178')
proj_wgs84 = Proj(init='epsg:4326')

def convert_view(request):
    result = None
    if request.method == 'POST':
        form = XYForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data['x']
            y = form.cleaned_data['y']
            lat, lon = transform(proj_2000, proj_wgs84, x, y)
            lon = round(lon, 5)
            lat = round(lat, 5)
            result = f"{lon},{lat}"
    else:
        form = XYForm()

    return render(request, 'djangoapp/main.html', {'form': form, 'result': result})
