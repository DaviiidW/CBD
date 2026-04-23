"""
python manage.py seed_graph
python manage.py seed_graph --clear   (borra todo primero)
"""
from django.core.management.base import BaseCommand
from apps.graph.models import Technology, Project


TECHNOLOGIES = [
    # (name, slug, tech_type, description, url)
    ('Python',      'python',      'language',  'General-purpose, interpreted, high-level language.', 'https://python.org'),
    ('JavaScript',  'javascript',  'language',  'The language of the web.', 'https://developer.mozilla.org/en-US/docs/Web/JavaScript'),
    ('TypeScript',  'typescript',  'language',  'Typed superset of JavaScript.', 'https://typescriptlang.org'),
    ('Rust',        'rust',        'language',  'Systems language focused on safety and performance.', 'https://rust-lang.org'),
    ('Go',          'go',          'language',  'Fast, statically typed, compiled language by Google.', 'https://go.dev'),
    ('SQL',         'sql',         'language',  'Structured Query Language for relational databases.', ''),
    ('FastAPI',     'fastapi',     'framework', 'Modern, fast Python web framework for APIs.', 'https://fastapi.tiangolo.com'),
    ('Django',      'django',      'framework', 'High-level Python web framework.', 'https://djangoproject.com'),
    ('Flask',       'flask',       'framework', 'Lightweight WSGI Python web framework.', 'https://flask.palletsprojects.com'),
    ('Express',     'express',     'framework', 'Minimal Node.js web framework.', 'https://expressjs.com'),
    ('NestJS',      'nestjs',      'framework', 'Progressive Node.js framework with TypeScript.', 'https://nestjs.com'),
    ('Gin',         'gin',         'framework', 'Fast HTTP web framework for Go.', 'https://gin-gonic.com'),
    ('React',       'react',       'library',   'UI library for building component-based interfaces.', 'https://react.dev'),
    ('Vue',         'vue',         'framework', 'Progressive JavaScript framework for UIs.', 'https://vuejs.org'),
    ('Svelte',      'svelte',      'framework', 'Compiler-based UI framework with no virtual DOM.', 'https://svelte.dev'),
    ('Next.js',     'nextjs',      'framework', 'React framework for production with SSR/SSG.', 'https://nextjs.org'),
    ('Nuxt',        'nuxt',        'framework', 'Vue framework with SSR support.', 'https://nuxt.com'),
    ('Vite',        'vite',        'tool',      'Lightning-fast frontend build tool.', 'https://vitejs.dev'),
    ('Webpack',     'webpack',     'tool',      'Module bundler for JavaScript applications.', 'https://webpack.js.org'),
    ('esbuild',     'esbuild',     'tool',      'Extremely fast JavaScript bundler.', 'https://esbuild.github.io'),
    ('PostgreSQL',  'postgresql',  'database',  'Powerful open-source relational database.', 'https://postgresql.org'),
    ('MongoDB',     'mongodb',     'database',  'Document-oriented NoSQL database.', 'https://mongodb.com'),
    ('Redis',       'redis',       'database',  'In-memory data structure store, used as cache/broker.', 'https://redis.io'),
    ('Neo4j',       'neo4j',       'database',  'Leading graph database platform.', 'https://neo4j.com'),
    ('SQLite',      'sqlite',      'database',  'Serverless, self-contained SQL database engine.', 'https://sqlite.org'),
    ('Docker',      'docker',      'platform',  'Containerization platform.', 'https://docker.com'),
    ('Kubernetes',  'kubernetes',  'platform',  'Container orchestration system.', 'https://kubernetes.io'),
    ('AWS',         'aws',         'platform',  'Amazon Web Services cloud platform.', 'https://aws.amazon.com'),
    ('SQLAlchemy',  'sqlalchemy',  'library',   'Python SQL toolkit and ORM.', 'https://sqlalchemy.org'),
    ('Pydantic',    'pydantic',    'library',   'Data validation using Python type hints.', 'https://docs.pydantic.dev'),
    ('Celery',      'celery',      'library',   'Distributed task queue for Python.', 'https://docs.celeryq.dev'),
    ('Prisma',      'prisma',      'library',   'Next-generation ORM for Node.js and TypeScript.', 'https://prisma.io'),
    ('GraphQL',     'graphql',     'library',   'Query language and runtime for APIs.', 'https://graphql.org'),
    ('Tailwind',    'tailwind',    'library',   'Utility-first CSS framework.', 'https://tailwindcss.com'),
]

RELATIONS = [
    ('typescript',  'extends',          'javascript'),
    ('nextjs',      'depends_on',       'react'),
    ('nuxt',        'depends_on',       'vue'),
    ('nestjs',      'depends_on',       'typescript'),
    ('fastapi',     'depends_on',       'pydantic'),
    ('sqlalchemy',  'compatible_with',  'postgresql'),
    ('sqlalchemy',  'compatible_with',  'sqlite'),
    ('sqlalchemy',  'compatible_with',  'mongodb'),
    ('celery',      'compatible_with',  'redis'),
    ('celery',      'compatible_with',  'postgresql'),
    ('prisma',      'compatible_with',  'postgresql'),
    ('prisma',      'compatible_with',  'mongodb'),
    ('vite',        'alternative_to',   'webpack'),
    ('esbuild',     'alternative_to',   'webpack'),
    ('esbuild',     'alternative_to',   'vite'),
    ('vite',        'compatible_with',  'react'),
    ('vite',        'compatible_with',  'vue'),
    ('vite',        'compatible_with',  'svelte'),
    ('react',       'alternative_to',   'vue'),
    ('react',       'alternative_to',   'svelte'),
    ('vue',         'alternative_to',   'svelte'),
    ('django',      'alternative_to',   'flask'),
    ('fastapi',     'alternative_to',   'flask'),
    ('fastapi',     'alternative_to',   'django'),
    ('docker',      'compatible_with',  'kubernetes'),
    ('graphql',     'compatible_with',  'react'),
    ('graphql',     'compatible_with',  'fastapi'),
    ('graphql',     'compatible_with',  'nestjs'),
    ('tailwind',    'compatible_with',  'react'),
    ('tailwind',    'compatible_with',  'vue'),
    ('tailwind',    'compatible_with',  'nextjs'),
    ('tailwind',    'compatible_with',  'svelte'),
    ('gin',         'depends_on',       'go'),
    ('express',     'depends_on',       'javascript'),
    ('nestjs',      'alternative_to',   'express'),
    ('postgresql',  'alternative_to',   'sqlite'),
    ('postgresql',  'alternative_to',   'mongodb'),
    ('redis',       'compatible_with',  'django'),
    ('redis',       'compatible_with',  'fastapi'),
    ('redis',       'compatible_with',  'nestjs'),
    ('docker',      'compatible_with',  'fastapi'),
    ('docker',      'compatible_with',  'django'),
    ('docker',      'compatible_with',  'nestjs'),
    ('docker',      'compatible_with',  'postgresql'),
    ('docker',      'compatible_with',  'redis'),
    ('fastapi',     'compatible_with',  'sqlalchemy'),
    ('django',      'compatible_with',  'postgresql'),
    ('django',      'compatible_with',  'redis'),
    ('django',      'compatible_with',  'celery'),
]

PROJECTS = [
    {
        'title': 'FastAPI + React Dashboard',
        'slug': 'fastapi-react-dashboard',
        'description': 'Admin dashboard con FastAPI como backend y React SPA. Usa PostgreSQL y Redis para caché.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['fastapi', 'react', 'postgresql', 'redis', 'vite', 'pydantic', 'tailwind'],
    },
    {
        'title': 'Django E-Commerce',
        'slug': 'django-ecommerce',
        'description': 'Plataforma e-commerce con Django, Celery para tareas asíncronas y PostgreSQL.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['django', 'postgresql', 'celery', 'redis', 'python'],
    },
    {
        'title': 'Next.js Blog Platform',
        'slug': 'nextjs-blog',
        'description': 'Blog SSG/SSR con Next.js, Tailwind CSS y una capa de API GraphQL.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['nextjs', 'react', 'typescript', 'tailwind', 'graphql'],
    },
    {
        'title': 'NestJS Microservices',
        'slug': 'nestjs-microservices',
        'description': 'Arquitectura de microservicios event-driven con NestJS, Redis y PostgreSQL.',
        'project_type': 'api',
        'author': 'admin',
        'technologies': ['nestjs', 'typescript', 'redis', 'postgresql', 'docker'],
    },
    {
        'title': 'Svelte + FastAPI Notes App',
        'slug': 'svelte-fastapi-notes',
        'description': 'App de notas minimalista con frontend Svelte + Vite y backend FastAPI.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['svelte', 'vite', 'fastapi', 'python', 'sqlite', 'pydantic'],
    },
    {
        'title': 'Go REST API',
        'slug': 'go-rest-api',
        'description': 'API REST de alto rendimiento con Go y Gin, PostgreSQL y Docker.',
        'project_type': 'api',
        'author': 'admin',
        'technologies': ['go', 'gin', 'postgresql', 'docker'],
    },
    {
        'title': 'Graph Knowledge Base',
        'slug': 'graph-knowledge-base',
        'description': 'Herramienta de gestión del conocimiento con Neo4j, FastAPI y React.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['neo4j', 'fastapi', 'react', 'python', 'pydantic', 'vite'],
    },
    {
        'title': 'Vue + Nuxt Portfolio',
        'slug': 'vue-nuxt-portfolio',
        'description': 'Portfolio SSR con Nuxt 3, Tailwind y desplegado en AWS.',
        'project_type': 'web app',
        'author': 'admin',
        'technologies': ['nuxt', 'vue', 'typescript', 'tailwind', 'aws'],
    },
]


class Command(BaseCommand):
    help = 'Pobla Neo4j con tecnologías, relaciones y proyectos de ejemplo.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Borra todos los nodos antes de hacer seed.')

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Borrando nodos existentes...')
            for p in Project.nodes.all():
                p.delete()
            for t in Technology.nodes.all():
                t.delete()
            self.stdout.write(self.style.WARNING('Todos los nodos borrados.'))

        # Tecnologías
        self.stdout.write('Creando tecnologías...')
        tech_map = {}
        for name, slug, tech_type, desc, url in TECHNOLOGIES:
            existing = Technology.nodes.get_or_none(slug=slug)
            if existing:
                tech_map[slug] = existing
                self.stdout.write(f'  skip {name} (ya existe)')
            else:
                t = Technology(name=name, slug=slug, tech_type=tech_type, description=desc, url=url).save()
                tech_map[slug] = t
                self.stdout.write(f'  + {name}')

        # Relaciones
        self.stdout.write('Creando relaciones...')
        for slug_a, rel, slug_b in RELATIONS:
            ta = tech_map.get(slug_a)
            tb = tech_map.get(slug_b)
            if not ta or not tb:
                self.stdout.write(self.style.WARNING(f'  skip {slug_a} -{rel}-> {slug_b} (nodo no encontrado)'))
                continue
            try:
                if rel == 'compatible_with' and not ta.compatible_with.is_connected(tb):
                    ta.compatible_with.connect(tb)
                elif rel == 'depends_on' and not ta.depends_on.is_connected(tb):
                    ta.depends_on.connect(tb)
                elif rel == 'alternative_to' and not ta.alternative_to.is_connected(tb):
                    ta.alternative_to.connect(tb)
                elif rel == 'extends' and not ta.extends.is_connected(tb):
                    ta.extends.connect(tb)
                self.stdout.write(f'  {slug_a} --[{rel}]--> {slug_b}')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  error: {e}'))

        # Proyectos
        self.stdout.write('Creando proyectos...')
        for data in PROJECTS:
            existing = Project.nodes.get_or_none(slug=data['slug'])
            if existing:
                self.stdout.write(f'  skip {data["title"]} (ya existe)')
                continue
            project = Project(
                title=data['title'], slug=data['slug'],
                description=data['description'], project_type=data['project_type'],
                author_username=data['author'],
            ).save()
            for slug in data['technologies']:
                tech = tech_map.get(slug)
                if tech:
                    project.uses.connect(tech)
            self.stdout.write(f'  + {data["title"]}')

        self.stdout.write(self.style.SUCCESS('\n¡Seed completado!'))
        self.stdout.write(f'  {len(TECHNOLOGIES)} tecnologías, {len(RELATIONS)} relaciones, {len(PROJECTS)} proyectos.')