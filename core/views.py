from django.shortcuts import render


def home(request):
    return render(request, 'home.html', {'active_nav': 'overview'})


def design_preview(request):
    return render(request, 'design_preview.html', {'active_nav': 'design_preview'})