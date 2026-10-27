from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import FarmForm
from .models import Farm


@login_required
def my_farm(request):
    farms = Farm.objects.filter(owner=request.user).prefetch_related('preferred_crops')
    return render(request, 'farms/my_farm.html', {
        'farms': farms,
        'active_nav': 'my_farm',
    })


@login_required
def farm_edit(request):
    farm = Farm.objects.filter(owner=request.user).first()

    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            form.save_m2m()
            messages.success(request, f"Farm '{farm.name}' saved successfully.")
            return redirect('farms:my_farm')
    else:
        form = FarmForm(instance=farm)

    return render(request, 'farms/farm_form.html', {
        'form': form,
        'farm': farm,
        'active_nav': 'my_farm',
    })