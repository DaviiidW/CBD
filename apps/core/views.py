from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from apps.graph.models import Project, Technology
from apps.graph import queries


def home(request):
    recent_projects = Project.nodes.order_by('title').all()[:6]
    top_techs = queries.get_most_connected_technologies(6)
    cooccurrence = queries.get_technology_cooccurrence()[:5]
    return render(request, 'core/home.html', {
        'recent_projects': recent_projects,
        'top_techs': top_techs,
        'cooccurrence': cooccurrence,
    })


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})