from django import forms
from .models import TECH_TYPES, PROJECT_TYPES, Technology


class TechnologyForm(forms.Form):
    name = forms.CharField(max_length=100, label='Nombre')
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Descripción'
    )
    url = forms.URLField(required=False, label='URL oficial')
    tech_type = forms.ChoiceField(
        choices=[(t, t.capitalize()) for t in TECH_TYPES], label='Tipo'
    )
    release_year = forms.IntegerField(required=False, label='Año de lanzamiento')
    license = forms.CharField(max_length=100, initial='MIT', required=False, label='Licencia')
    is_open_source = forms.BooleanField(initial=True, required=False, label='¿Es Código Abierto?')
    github_url = forms.URLField(required=False, label='URL del repositorio GitHub')
    documentation_url = forms.URLField(required=False, label='URL de la documentación oficial')


class ProjectForm(forms.Form):
    title = forms.CharField(max_length=200, label='Título')
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Descripción'
    )
    url = forms.URLField(required=False, label='URL del proyecto')
    project_type = forms.ChoiceField(
        choices=[(t, t.capitalize()) for t in PROJECT_TYPES], label='Tipo'
    )
    author_username = forms.CharField(max_length=100, label='Autor', required=True)
    technologies = forms.MultipleChoiceField(
        choices=[], widget=forms.CheckboxSelectMultiple,
        required=False, label='Tecnologías utilizadas'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        techs = Technology.nodes.order_by('name').all()
        self.fields['technologies'].choices = [
            (t.slug, f'{t.name} ({t.tech_type})') for t in techs
        ]


RELATION_TYPES = [
    ('compatible_with', 'Compatible with — works well together'),
    ('depends_on', 'Depends on — built on top of'),
    ('alternative_to', 'Alternative to — can substitute'),
    ('extends', 'Extends — superset / layer on top'),
]


class TechRelationForm(forms.Form):
    tech_a = forms.ChoiceField(choices=[], label='Technology A')
    relation_type = forms.ChoiceField(choices=RELATION_TYPES, label='Relationship')
    tech_b = forms.ChoiceField(choices=[], label='Technology B')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        techs = Technology.nodes.order_by('name').all()
        choices = [(t.slug, f'{t.name} ({t.tech_type})') for t in techs]
        self.fields['tech_a'].choices = choices
        self.fields['tech_b'].choices = choices