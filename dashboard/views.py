from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Part
from .forms import PartForm

# Create your views here.


@login_required
def index(request):
    items = Part.objects.all()

    context = {
        "items": items,
    }

    return render(request, "dashboard/index.html", context=context)


@login_required
def part(request):
    if request.method == "POST":
        form = PartForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard-index")
    else:
        form = PartForm()
    context = {
        "form": form,
    }
    return render(request, "dashboard/add_part.html", context=context)


@login_required
def edit_part(request, pk):
    item = Part.objects.get(id=pk)
    if request.method == "POST":
        form = PartForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard-index')
    else:
        form = PartForm(instance=item)
    context = {
        "form": form,
    }
    return render(request, "dashboard/edit_part.html", context=context)
