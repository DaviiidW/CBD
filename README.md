# TechGraph

Explorador de tecnologías basado en grafos. Muestra cómo lenguajes, frameworks, librerías y proyectos se relacionan entre sí, demostrando el valor de una base de datos de grafos (Neo4j) frente a una relacional en según qué contextos.

>Para más información sobre el uso de la aplicación consulta el [Manual de Usuario](./MANUAL_USUARIO.md).


## Despliegue

El proyecto está desplegado en **Render** con base de datos en **Neo4j Aura Free**. Puedes acceder directamente en [https://cbd-q00l.onrender.com](https://cbd-q00l.onrender.com).


> El servicio puede tardar ~30 segundos en responder si ha estado inactivo (plan gratuito de Render).


## Stack

| Capa | Tecnología |
|---|---|
| Backend | Django 6.0 |
| Base de datos | Neo4j + neomodel |
| Frontend | Django Templates + vis.js |
| Despliegue | Render + Neo4j Aura |

---

## Arranque en local

### Requisitos

- Python 3.11+
- **Neo4j Desktop** corriendo en local con una instancia activa en el puerto `7687`.
- **Plugin Graph Data Science (GDS)** instalado en tu base de datos Neo4j (necesario para el funcionamiento del motor de recomendaciones basadas en similitudes).

#### ¿Cómo instalar el plugin GDS en Neo4j Desktop?
1. Abre **Neo4j Desktop** y haz clic en los 3 puntos en la derecha del botón de iniciar la instancia en la cual se desea instalar el plugin.
2. Haz clic en la pestaña **Plugins**.
3. Busca la sección **Graph Data Science Library** y haz click en **Install**.
4. Espera a que finalice la descarga e instalación.
5. Si la base de datos estaba encendida, **reiníciala** (haz click en *Stop* y luego en *Start*) para que cargue el plugin correctamente.

### Pasos

Antes de nada, recuerda tener activa la instancia de Neo4j y conocer la contraseña de la misma.

#### 1. Clonar el repositorio
```bash
git clone https://github.com/DaviiidW/CBD
cd CBD
```

#### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 3. Configurar variables de entorno
```bash
cp env.example .env
```

Abre el `.env` y edita los valores correspondientes:

- **`SECRET_KEY`** — Genera una clave secreta en [https://djecrety.ir](https://djecrety.ir) y pégala aquí.
- **`NEO4J_URI`** — URI de tu base de datos Neo4j (por defecto `bolt://localhost:7687`).
- **`NEO4J_USER`** — Nombre de usuario de la instancia local de Neo4j (por defecto `neo4j`).
- **`NEO4J_PASSWORD`** — La contraseña de tu instancia de Neo4j local.
- **`GEMINI_API_KEY`** — (Opcional) Clave de API de Gemini si deseas utilizar el Asistente chatbot interactivo de arquitectura.
- **`GEMINI_MODEL`** — (Opcional) Modelo de Gemini a utilizar (por defecto `gemini-flash-lite-latest`).

#### 4. Migraciones
```bash
python manage.py migrate
```

#### 5. Poblar la base de datos con datos de ejemplo
```bash
python manage.py seed_graph
```

Este comando poblará el grafo con tecnologías, relaciones y proyectos reales desde las fixtures del proyecto y la API de búsqueda de GitHub. Puedes pasarle los siguientes parámetros opcionales:
- `--clear` — Borra todos los nodos y relaciones del grafo (proyectos, tecnologías, tags y usuarios de prueba) antes de la inserción. Es muy recomendable usarlo para reiniciar a una base de datos limpia.
- `--limit <N>` — Limita la cantidad de proyectos reales descargados de GitHub para indexar (por defecto `250`, máximo `500`).

#### 6. Crear usuario de demostración
```bash
python manage.py create_demo_user
```

#### 7. (Opcional) Crear superusuario para el panel /admin/
```bash
python manage.py createsuperuser
```

#### 8. Arrancar el servidor
```bash
python manage.py runserver
```

Abre [http://localhost:8000](http://localhost:8000)

> Para acceder con el usuario de demo consulta el [Manual de Usuario](./MANUAL_USUARIO.md#acceso-rápido-con-usuario-de-demo).

---

## Estructura del proyecto

```
proyecto/
├── configuracion/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── urls_auth.py
│   └── graph/
│       ├── __init__.py
│       ├── apps.py
│       ├── models.py
│       ├── queries.py
│       ├── views.py
│       ├── forms.py
│       ├── urls.py
│       └── management/
│           ├── __init__.py
│           └── commands/
│               ├── __init__.py
│               ├── create_demo_user.py
│               └── seed_graph.py
├── templates/
│   ├── base.html
│   ├── core/
│   │   └── home.html
│   ├── graph/
│   │   ├── global_graph.html
│   │   ├── technology_list.html
│   │   ├── technology_detail.html
│   │   ├── project_list.html
│   │   ├── project_detail.html
│   │   ├── add_technology.html
│   │   ├── add_project.html
│   │   ├── add_tech_relation.html
│   │   ├── find_path.html
│   │   └── filter_projects.html
│   └── registration/
│       ├── login.html
│       └── register.html
├── static/
│   ├── css/
│   │   └── main.css
│   └── js/
│       └── graph.js
├── manage.py
├── build.sh
├── Procfile
├── requirements.txt
├── .env.example
├── README.md
└── MANUAL_USUARIO.md
```


