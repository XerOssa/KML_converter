from django.shortcuts import render, redirect
from django.conf import settings


def main(request):
    context = {}
    return render(request, 'main.html', context)