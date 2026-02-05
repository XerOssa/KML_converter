from django.shortcuts import render
from .forms import XYForm
from pyproj import Transformer

transformer = Transformer.from_crs(
    "EPSG:2178",  # PUWG 2000
    "EPSG:4326",  # WGS84
    always_xy=True
)

def convert_view(request):
    result = None

    if request.method == "POST":
        form = XYForm(request.POST)
        if form.is_valid():
            x = form.cleaned_data["x"]
            y = form.cleaned_data["y"]

            lon, lat = transformer.transform(y, x)

            lat = round(lat, 5)
            lon = round(lon, 5)

            # TU decydujesz o kolejności prezentacji
            result = f"{lat}, {lon}"

    else:
        form = XYForm()

    return render(
        request,
        "djangoapp/main.html",
        {"form": form, "result": result}
    )
