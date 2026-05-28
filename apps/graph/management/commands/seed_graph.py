import os
import json
import re
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware

from apps.graph.models import Technology, Project, TechnologyVersion, Tag

class Command(BaseCommand):
    help = 'Pobla la base de datos Neo4j'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=250
        )

    def handle(self, *args, **options):
        fixtures_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'fixtures')
        
        with open(os.path.join(fixtures_dir, 'technologies.json'), 'r', encoding='utf-8') as f:
            curated_technologies = json.load(f)
            
        with open(os.path.join(fixtures_dir, 'versions.json'), 'r', encoding='utf-8') as f:
            real_versions_map = json.load(f)
            
        with open(os.path.join(fixtures_dir, 'relations.json'), 'r', encoding='utf-8') as f:
            curated_relations = json.load(f)
            
        with open(os.path.join(fixtures_dir, 'projects.json'), 'r', encoding='utf-8') as f:
            offline_projects = json.load(f)

        if options['clear']:
            self.stdout.write('\n[!] Opción --clear detectada. Borrando nodos existentes...')
            from neomodel import db
            res, _ = db.cypher_query("MATCH (p:Project) RETURN count(p)")
            project_count = res[0][0] if res else 0
            db.cypher_query("MATCH (p:Project) DETACH DELETE p")
            self.stdout.write(f'  - Borrados {project_count} proyectos.')
            res, _ = db.cypher_query("MATCH (t:Technology) RETURN count(t)")
            tech_count = res[0][0] if res else 0
            db.cypher_query("MATCH (t:Technology) DETACH DELETE t")
            self.stdout.write(f'  - Borradas {tech_count} tecnologías.')
            res, _ = db.cypher_query("MATCH (tg:Tag) RETURN count(tg)")
            tag_count = res[0][0] if res else 0
            db.cypher_query("MATCH (tg:Tag) DETACH DELETE tg")
            self.stdout.write(f'  - Borrados {tag_count} tags.')
            res, _ = db.cypher_query("MATCH (v:TechnologyVersion) RETURN count(v)")
            version_count = res[0][0] if res else 0
            db.cypher_query("MATCH (v:TechnologyVersion) DETACH DELETE v")
            self.stdout.write(f'  - Borradas {version_count} versiones.')
            self.stdout.write(self.style.SUCCESS('[OK] Base de datos limpia.'))

        self.stdout.write('\n[1/5] Creando tecnologías del catálogo...')
        tech_map = {}
        tech_created_count = 0
        tech_skipped_count = 0

        for t_data in curated_technologies:
            slug = t_data['slug']
            existing = Technology.nodes.get_or_none(slug=slug)
            
            if existing:
                tech_map[slug] = existing
                tech_skipped_count += 1
            else:
                t = Technology(
                    name=t_data['name'],
                    slug=slug,
                    tech_type=t_data['tech_type'],
                    description=t_data['description'],
                    url=t_data.get('url', ''),
                    github_url=t_data.get('github_url', ''),
                    documentation_url=t_data.get('documentation_url', ''),
                    license=t_data.get('license', 'Unknown'),
                    release_year=t_data.get('release_year'),
                    is_open_source=t_data.get('is_open_source', True)
                ).save()
                tech_map[slug] = t
                tech_created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'  [OK] Tecnologías procesadas: {tech_created_count} creadas, {tech_skipped_count} ya existentes.'))

        self.stdout.write('\n[2/5] Generando etiquetas (Tags) y versiones estructuradas...')
        tags_map = {}
        versions_created = 0

        basic_tags = ['web', 'backend', 'frontend', 'ai', 'database', 'cloud', 'devops', 'mobile', 'testing', 'compiler', 'security', 'systems', 'analytics']
        for tag_name in basic_tags:
            tag = Tag.nodes.get_or_none(name=tag_name)
            if not tag:
                tag = Tag(name=tag_name).save()
            tags_map[tag_name] = tag

        for slug, t_node in tech_map.items():
            t_type = t_node.tech_type
            assigned_tags = []
            if t_type == 'language':
                assigned_tags.append('systems' if slug in ['c', 'cpp', 'rust', 'go', 'assembly'] else 'web')
            elif t_type == 'framework':
                assigned_tags.append('web')
                assigned_tags.append('frontend' if slug in ['react', 'vue', 'svelte', 'angular', 'nextjs', 'nuxt', 'sveltekit'] else 'backend')
            elif t_type == 'database':
                assigned_tags.append('database')
            elif t_type == 'platform':
                assigned_tags.append('cloud')
            elif t_type == 'tool':
                assigned_tags.append('devops')
            elif t_type == 'library' and slug in ['pytorch', 'tensorflow', 'transformers', 'scikit-learn']:
                assigned_tags.append('ai')

            for t_name in assigned_tags:
                if t_name in tags_map:
                    t_node.tagged_as.connect(tags_map[t_name])

            versions_to_create = real_versions_map.get(slug, [])
            if not versions_to_create:
                versions_to_create = [
                    ["1.0.0", t_node.release_year or 2020],
                    ["1.1.0", (t_node.release_year or 2020) + 1],
                    ["2.0.0", (t_node.release_year or 2020) + 2],
                    ["2.1.0", (t_node.release_year or 2020) + 3],
                    ["3.0.0", (t_node.release_year or 2020) + 4],
                ]

            for v_str, year in versions_to_create:
                existing_v = t_node.has_version.get_or_none(version=v_str)
                if not existing_v:
                    release_date = make_aware(datetime(max(year, 1970), 6, 15))
                    tv = TechnologyVersion(name=v_str, version=v_str, release_date=release_date).save()
                    t_node.has_version.connect(tv)
                    versions_created += 1

        self.stdout.write(self.style.SUCCESS(f'  [OK] Asignación completada. Creadas {versions_created} versiones.'))

        self.stdout.write('\n[3/5] Creando relaciones cruzadas de arquitectura entre tecnologías...')
        rel_created_count = 0
        rel_error_count = 0

        for r_data in curated_relations:
            slug_a, rel_type, slug_b, notes = r_data[0], r_data[1], r_data[2], r_data[3]
            ta = tech_map.get(slug_a)
            tb = tech_map.get(slug_b)
            if not ta or not tb:
                continue
            
            try:
                if rel_type == 'extends':
                    if not ta.extends.is_connected(tb):
                        ta.extends.connect(tb)
                        rel_created_count += 1
                elif rel_type == 'depends_on':
                    if not ta.depends_on.is_connected(tb):
                        ta.depends_on.connect(tb)
                        rel_created_count += 1
                elif rel_type == 'alternative_to':
                    if not ta.alternative_to.is_connected(tb):
                        ta.alternative_to.connect(tb)
                        rel_created_count += 1
                elif rel_type == 'compatible_with':
                    if not ta.compatible_with.is_connected(tb):
                        ta.compatible_with.connect(tb, {'notes': notes})
                        rel_created_count += 1
            except Exception:
                rel_error_count += 1

        self.stdout.write(self.style.SUCCESS(f'  [OK] Relaciones creadas: {rel_created_count}. Errores/omitidas: {rel_error_count}.'))

        self.stdout.write('\n[4/5] Descargando proyectos reales de código abierto desde la API de GitHub...')
        limit = min(options['limit'], 500)
        github_projects = []
        api_success = False

        pages_needed = (limit + 99) // 100
        try:
            for page in range(1, pages_needed + 1):
                page_limit = min(100, limit - len(github_projects))
                if page_limit <= 0:
                    break
                url = f"https://api.github.com/search/repositories?q=stars:>10000&sort=stars&order=desc&per_page={page_limit}&page={page}"
                req = Request(url)
                req.add_header('User-Agent', 'TechGraph-Populate-Command')
                self.stdout.write(f'  -> Petición HTTP: {url}')
                with urlopen(req, timeout=12) as response:
                    res_data = json.loads(response.read().decode('utf-8'))
                    items = res_data.get('items', [])
                    if items:
                        github_projects.extend(items)
            
            if github_projects:
                api_success = True
                self.stdout.write(self.style.SUCCESS(f'  [OK] Descargados con éxito {len(github_projects)} proyectos de GitHub.'))
        except URLError as e:
            self.stdout.write(self.style.WARNING(f'  [!] No se pudo conectar a GitHub (Error: {e.reason}).'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'  [!] Error de API de GitHub: {e}.'))

        if not api_success:
            self.stdout.write(self.style.WARNING('  [!] Cargando dataset local enriquecido en Modo Resiliencia (Offline)...'))
            github_projects = offline_projects[:limit]

        self.stdout.write('\n[5/5] Insertando proyectos y mapeando dependencias a tecnologías...')
        projects_created_count = 0
        projects_skipped_count = 0
        relations_uses_count = 0

        for r_data in github_projects:
            raw_slug = r_data.get('full_name') or r_data.get('slug')
            proj_slug = slugify(raw_slug.replace('/', '-'))
            
            existing = Project.nodes.get_or_none(slug=proj_slug)
            if existing:
                projects_skipped_count += 1
                continue

            title = r_data.get('name') or r_data.get('title')
            description = r_data.get('description') or ''
            proj_url = r_data.get('html_url') or r_data.get('url') or ''
            author = r_data.get('owner', {}).get('login') if isinstance(r_data.get('owner'), dict) else r_data.get('author', 'anonymous')
            created_at_str = r_data.get('created_at')
            created_dt = self.parse_date(created_at_str)

            inferred_type = self.infer_project_type(r_data)

            project = Project(
                title=title,
                slug=proj_slug,
                description=description[:500],
                url=proj_url,
                project_type=inferred_type,
                author_username=author,
                created_at=created_dt
            ).save()
            projects_created_count += 1

            primary_lang = r_data.get('language')
            if primary_lang:
                lang_slug = slugify(primary_lang)
                if lang_slug == 'c-':
                    lang_slug = 'cpp'
                elif lang_slug == 'c-sharp':
                    lang_slug = 'csharp'
                
                tech_node = tech_map.get(lang_slug)
                if tech_node:
                    project.uses.connect(tech_node, {'purpose': 'Lenguaje de programación principal'})
                    relations_uses_count += 1

            topics = r_data.get('topics', [])
            for topic in topics:
                t_slug = slugify(topic)
                tech_node = tech_map.get(t_slug)
                if tech_node and tech_node.slug != slugify(primary_lang or ''):
                    if not project.uses.is_connected(tech_node):
                        purpose = f"Tecnología integrada como {tech_node.tech_type}"
                        project.uses.connect(tech_node, {'purpose': purpose})
                        relations_uses_count += 1

        self.stdout.write(self.style.SUCCESS(f'  [OK] Proyectos procesados: {projects_created_count} creados, {projects_skipped_count} ya existentes.'))
        self.stdout.write(self.style.SUCCESS(f'  [OK] Relaciones de uso (USES) mapeadas con éxito: {relations_uses_count}.'))

        self.stdout.write(self.style.SUCCESS('\n============================================================='))
        self.stdout.write(self.style.SUCCESS('                  POBLACIÓN DE GRAFO COMPLETADA!'))
        self.stdout.write(self.style.SUCCESS('============================================================='))
        self.stdout.write(f'  - Tecnologías: {len(tech_map)} registradas en catálogo.')
        self.stdout.write(f'  - Versiones creadas: {versions_created}.')
        self.stdout.write(f'  - Relaciones cruzadas: {rel_created_count} de arquitectura mapeadas.')
        self.stdout.write(f'  - Proyectos importados: {projects_created_count} nuevos repositorios reales.')
        self.stdout.write(f'  - Relaciones de Proyectos (USES): {relations_uses_count} asignadas dinámicamente.')
        self.stdout.write(self.style.SUCCESS('=============================================================\n'))

    def parse_date(self, date_str):
        if not date_str:
            return timezone.now()
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            return make_aware(dt)
        except Exception:
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                return dt
            except Exception:
                return timezone.now()

    def infer_project_type(self, repo_data):
        topics = [t.lower() for t in repo_data.get('topics', [])]
        desc = (repo_data.get('description') or '').lower()
        
        if any(t in topics for t in ['cli', 'command-line', 'terminal']) or 'command line' in desc:
            return 'cli'
        elif any(t in topics for t in ['game', 'engine', 'game-development']) or 'game' in desc:
            return 'game'
        elif any(t in topics for t in ['library', 'package', 'sdk', 'api-client']) or 'library' in desc or 'framework' in desc:
            return 'library'
        elif any(t in topics for t in ['api', 'rest-api', 'graphql', 'grpc']) or 'api' in desc:
            return 'api'
        elif any(t in topics for t in ['mobile', 'android', 'ios', 'react-native', 'flutter']) or 'app' in desc:
            return 'mobile'
        elif any(t in topics for t in ['desktop', 'electron', 'tauri', 'gui']) or 'desktop app' in desc:
            return 'desktop'
        elif any(t in topics for t in ['web', 'website', 'web-app', 'frontend', 'backend', 'fullstack']) or 'web app' in desc or 'dashboard' in desc:
            return 'web app'
        else:
            return 'other'
