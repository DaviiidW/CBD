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
- Neo4j Desktop corriendo en local con una instancia activa en el puerto `7687`

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

Abre el `.env` y edita los valores marcados:

- **`SECRET_KEY`** — genera una en [https://djecrety.ir](https://djecrety.ir)
- **`NEO4J_BOLT_URL`** — sustituye `tu-contraseña` por la contraseña de tu instancia Neo4j local

#### 4. Migraciones
```bash
python manage.py migrate
```

#### 5. Poblar la base de datos con datos de ejemplo
```bash
python manage.py seed_graph
```

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


