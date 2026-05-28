import json
import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .models import Technology, Project, TECH_TYPES, PROJECT_TYPES
from . import queries
from .forms import TechnologyForm, ProjectForm, TechRelationForm


def global_graph(request):
    data = queries.get_full_graph_data()
    return render(request, 'graph/global_graph.html', {'graph_data': json.dumps(data)})


def technology_list(request):
    technologies = Technology.nodes.order_by('name').all()
    top = queries.get_most_connected_technologies(10)
    cooccurrence = queries.get_technology_cooccurrence()
    return render(request, 'graph/technology_list.html', {
        'technologies': technologies,
        'top_technologies': top,
        'cooccurrence': cooccurrence,
        'tech_types': TECH_TYPES,
    })


def technology_detail(request, slug):
    try:
        tech = Technology.nodes.get(slug=slug)
    except Technology.DoesNotExist:
        messages.error(request, 'Technology not found.')
        return redirect('technology_list')

    compatible = queries.get_compatible_technologies(slug)
    alternatives = queries.get_alternative_technologies(slug)
    projects = tech.used_by.all()
    subgraph = _build_tech_subgraph(tech)

    return render(request, 'graph/technology_detail.html', {
        'tech': tech,
        'compatible': compatible,
        'alternatives': alternatives,
        'projects': projects,
        'subgraph': json.dumps(subgraph),
    })


def project_list(request):
    projects = Project.nodes.order_by('title').all()
    return render(request, 'graph/project_list.html', {
        'projects': projects,
        'project_types': PROJECT_TYPES,
    })


def project_detail(request, slug):
    try:
        project = Project.nodes.get(slug=slug)
    except Project.DoesNotExist:
        messages.error(request, 'Project not found.')
        return redirect('project_list')

    technologies = project.uses.all()
    tech_slugs = [t.slug for t in technologies]
    related = []
    if len(tech_slugs) >= 2:
        related = queries.get_projects_by_technologies(tech_slugs[:3])
        related = [p for p in related if p['slug'] != slug][:5]

    subgraph = _build_project_subgraph(project, technologies)

    return render(request, 'graph/project_detail.html', {
        'project': project,
        'technologies': technologies,
        'related': related,
        'subgraph': json.dumps(subgraph),
    })


@login_required
def add_technology(request):
    if request.method == 'POST':
        form = TechnologyForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            slug = _slugify(data['name'])
            if Technology.nodes.get_or_none(slug=slug):
                messages.error(request, f'Technology "{data["name"]}" already exists.')
            else:
                Technology(
                    name=data['name'], slug=slug,
                    description=data['description'],
                    url=data['url'], tech_type=data['tech_type'],
                ).save()
                messages.success(request, f'Technology "{data["name"]}" added!')
                return redirect('technology_list')
    else:
        form = TechnologyForm()
    return render(request, 'graph/add_technology.html', {'form': form})


@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            slug = _slugify(data['title'])
            if Project.nodes.get_or_none(slug=slug):
                messages.error(request, f'Project "{data["title"]}" already exists.')
            else:
                project = Project(
                    title=data['title'], slug=slug,
                    description=data['description'],
                    url=data['url'], project_type=data['project_type'],
                    author_username=request.user.username,
                ).save()
                for tech_slug in data['technologies']:
                    tech = Technology.nodes.get_or_none(slug=tech_slug)
                    if tech:
                        project.uses.connect(tech, {'purpose': ''})
                messages.success(request, f'Project "{data["title"]}" added!')
                return redirect('project_detail', slug=slug)
    else:
        form = ProjectForm()
    return render(request, 'graph/add_project.html', {'form': form})


@login_required
def add_tech_relation(request):
    if request.method == 'POST':
        form = TechRelationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            tech_a = Technology.nodes.get_or_none(slug=data['tech_a'])
            tech_b = Technology.nodes.get_or_none(slug=data['tech_b'])
            if not tech_a or not tech_b:
                messages.error(request, 'One or both technologies not found.')
            elif tech_a.uid == tech_b.uid:
                messages.error(request, 'Cannot relate a technology to itself.')
            else:
                rel_type = data['relation_type']
                if rel_type == 'compatible_with':
                    tech_a.compatible_with.connect(tech_b)
                elif rel_type == 'depends_on':
                    tech_a.depends_on.connect(tech_b)
                elif rel_type == 'alternative_to':
                    tech_a.alternative_to.connect(tech_b)
                elif rel_type == 'extends':
                    tech_a.extends.connect(tech_b)
                messages.success(request, f'{tech_a.name} —[{rel_type}]→ {tech_b.name} created!')
                return redirect('technology_detail', slug=data['tech_a'])
    else:
        form = TechRelationForm()
    return render(request, 'graph/add_tech_relation.html', {'form': form})


def find_path(request):
    result = None
    error = None
    slug_a = request.GET.get('from', '')
    slug_b = request.GET.get('to', '')
    technologies = Technology.nodes.order_by('name').all()

    if slug_a and slug_b:
        if slug_a == slug_b:
            error = 'Choose two different technologies.'
        else:
            path = queries.find_path_between_technologies(slug_a, slug_b)
            if path:
                result = path
            else:
                error = 'No path found between these technologies (max depth: 6).'

    return render(request, 'graph/find_path.html', {
        'technologies': technologies,
        'result': result,
        'error': error,
        'slug_a': slug_a,
        'slug_b': slug_b,
    })


def filter_projects(request):
    tech_slugs = request.GET.getlist('techs')
    technologies = Technology.nodes.order_by('name').all()
    results = []
    if tech_slugs:
        results = queries.get_projects_by_technologies(tech_slugs)
    return render(request, 'graph/filter_projects.html', {
        'technologies': technologies,
        'results': results,
        'selected': tech_slugs,
    })


def graph_data_api(request):
    data = queries.get_full_graph_data()
    return JsonResponse(data)


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text


def _build_tech_subgraph(tech) -> dict:
    from neomodel import db

    results, _ = db.cypher_query(
        """
        MATCH (t:Technology {slug: $slug})
        MATCH (t)-[r]-(n)
        RETURN 
            labels(n)[0] AS label,
            COALESCE(n.uid, n.name) AS id,
            CASE 
                WHEN n:Technology THEN n.name 
                WHEN n:Project THEN n.title 
                WHEN n:TechnologyVersion THEN n.name 
                WHEN n:Tag THEN n.name 
            END AS name,
            CASE 
                WHEN n:Technology THEN n.tech_type 
                WHEN n:Project THEN n.project_type 
                WHEN n:TechnologyVersion THEN 'version' 
                WHEN n:Tag THEN 'tag'
            END AS subtype,
            COALESCE(n.slug, n.name) AS slug,
            type(r) AS rel_type,
            startNode(r) = t AS is_outgoing
        """,
        {'slug': tech.slug}
    )

    nodes = [{'id': tech.uid, 'label': tech.name, 'type': 'technology', 'subtype': tech.tech_type, 'main': True, 'slug': tech.slug}]
    edges = []
    seen = {tech.uid}

    for row in results:
        node_label, node_id, name, subtype, slug, rel_type, is_outgoing = row
        
        if node_label == 'Technology':
            node_type = 'technology'
        elif node_label == 'Project':
            node_type = 'project'
        elif node_label == 'TechnologyVersion':
            node_type = 'version'
        elif node_label == 'Tag':
            node_type = 'tag'
        else:
            node_type = 'other'
            
        if node_id not in seen:
            nodes.append({
                'id': node_id,
                'label': name,
                'type': node_type,
                'subtype': subtype,
                'main': False,
                'slug': slug
            })
            seen.add(node_id)
            
        rel_label = rel_type
        if rel_type == 'COMPATIBLE_WITH':
            rel_label = 'compatible_with'
        elif rel_type == 'DEPENDS_ON':
            rel_label = 'depends_on'
        elif rel_type == 'ALTERNATIVE_TO':
            rel_label = 'alternative_to'
        elif rel_type == 'EXTENDS':
            rel_label = 'extends'
        elif rel_type == 'USES':
            rel_label = 'used_by'
            
        if is_outgoing:
            edges.append({'from': tech.uid, 'to': node_id, 'label': rel_label})
        else:
            edges.append({'from': node_id, 'to': tech.uid, 'label': rel_label})

    return {'nodes': nodes, 'edges': edges}


def _build_project_subgraph(project, technologies) -> dict:
    nodes = [{'id': project.uid, 'label': project.title, 'type': 'project', 'subtype': project.project_type, 'main': True, 'slug': project.slug}]
    edges = []
    for tech in technologies:
        nodes.append({'id': tech.uid, 'label': tech.name, 'type': 'technology', 'subtype': tech.tech_type, 'main': False, 'slug': tech.slug})
        edges.append({'from': project.uid, 'to': tech.uid, 'label': 'uses'})
    return {'nodes': nodes, 'edges': edges}