# Manual de Usuario — TechGraph

## ¿Qué es TechGraph?

TechGraph es una aplicación web que permite explorar cómo las tecnologías del mundo del desarrollo de software se relacionan entre sí. Puedes registrar proyectos reales, vincularlos a los lenguajes y herramientas que usan, y descubrir conexiones entre tecnologías de forma visual e interactiva.

La aplicación está construida sobre una **base de datos de grafos** (Neo4j), lo que la hace especialmente eficiente para responder preguntas del tipo:

- ¿Qué proyectos puedo hacer si sé Python y React?
- ¿Cómo se conecta Rust con WebAssembly?
- ¿Qué alternativas tiene Webpack?
- ¿Qué tecnologías suelen aparecer juntas?

**Acceso**: [https://cbd-q00l.onrender.com](https://cbd-q00l.onrender.com) o bien en local siguiendo las instrucciones del [README.md](README.md).

---

## Índice

1. [Primeros pasos](#1-primeros-pasos)
2. [Navegación](#2-navegación)
3. [Explorar tecnologías](#3-explorar-tecnologías)
4. [Explorar proyectos](#4-explorar-proyectos)
5. [El grafo visual](#5-el-grafo-visual)
6. [Buscar camino entre tecnologías](#6-buscar-camino-entre-tecnologías)
7. [Filtrar proyectos por stack](#7-filtrar-proyectos-por-stack)
8. [Contribuir — añadir tecnologías y proyectos](#8-contribuir--añadir-tecnologías-y-proyectos)
9. [Por qué una base de datos de grafos](#9-por-qué-una-base-de-datos-de-grafos)

---

## 1. Primeros pasos

Al entrar a la aplicación verás la página de inicio con tres secciones principales:

- **Proyectos recientes** — los últimos proyectos añadidos por la comunidad
- **Tecnologías más conectadas** — las que más relaciones tienen en el grafo
- **Tecnologías que van juntas** — pares que aparecen juntos en más proyectos

No necesitas cuenta para explorar. Solo necesitas registrarte si quieres **añadir** proyectos o tecnologías.

### Acceso rápido con usuario de demo

Hay un usuario de demostración preconfigurado disponible tanto en la versión desplegada como en local:

| Campo | Render (producción) | Local |
|---|---|---|
| **URL de login** | [https://cbd-q00l.onrender.com/login/](https://cbd-q00l.onrender.com/login/) | [http://localhost:8000/login/](http://localhost:8000/login/) |
| **Usuario** | `demo` | `demo` |
| **Contraseña** | `demo1234` | `demo1234` |

> El usuario demo tiene permisos para añadir tecnologías, proyectos y relaciones, igual que cualquier usuario registrado.

---

## 2. Navegación

La barra de navegación superior da acceso a todas las secciones:

| Sección | Descripción |
|---|---|
| **Home** | Página principal con resumen y accesos rápidos |
| **Graph** | Grafo global interactivo con todos los nodos |
| **Technologies** | Listado completo de tecnologías |
| **Projects** | Listado completo de proyectos |
| **Find Path** | Busca el camino entre dos tecnologías |
| **Filter** | Filtra proyectos por su stack tecnológico |

Si tienes sesión iniciada, aparecerán también los botones **+ Technology** y **+ Project** en la esquina superior derecha.

---

## 3. Explorar tecnologías

Desde **Technologies** puedes ver todas las tecnologías registradas, organizadas por tipo:

- `language` — lenguajes de programación (Python, JavaScript, Go...)
- `framework` — frameworks web o de aplicación (Django, React, FastAPI...)
- `library` — librerías (SQLAlchemy, Pydantic, Tailwind...)
- `tool` — herramientas de desarrollo (Vite, Webpack, Docker...)
- `database` — bases de datos (PostgreSQL, MongoDB, Neo4j...)
- `platform` — plataformas de despliegue o infraestructura (AWS, Kubernetes...)

Al hacer click en una tecnología verás su **página de detalle**, que incluye:

- Un **grafo local** con todas sus conexiones directas
- Las **tecnologías relacionadas** y el tipo de relación que las une
- Las **alternativas** disponibles
- Los **proyectos** que la utilizan
- Un acceso directo a **buscar camino** desde esa tecnología

### Tipos de relación entre tecnologías

| Relación | Significado | Ejemplo |
|---|---|---|
| `compatible_with` | Funcionan bien juntas | Vite + React |
| `depends_on` | Una está construida sobre la otra | Next.js → React |
| `alternative_to` | Pueden sustituirse | Vite ↔ Webpack |
| `extends` | Una es superconjunto de la otra | TypeScript → JavaScript |

---

## 4. Explorar proyectos

Desde **Projects** puedes ver todos los proyectos registrados. Cada proyecto muestra:

- El **tipo** de aplicación (web app, api, cli, game...)
- Una **descripción** del proyecto
- El **autor** que lo añadió

Al entrar al detalle de un proyecto verás:

- El **grafo de su stack** — un diagrama visual con todas las tecnologías que usa
- Las **etiquetas de tecnologías** enlazadas a sus páginas de detalle
- **Proyectos relacionados** — otros proyectos que comparten tecnologías similares
- Un acceso directo a buscar **stacks similares**

---

## 5. El grafo visual

La sección **Graph** muestra un grafo interactivo con todos los nodos y conexiones de la base de datos.

### Cómo interactuar

| Acción | Resultado |
|---|---|
| **Scroll** | Zoom in / zoom out |
| **Click y arrastrar** | Mover el grafo |
| **Click en un nodo** | Ir a la página de detalle de esa tecnología o proyecto |
| **Hover sobre un nodo** | Ver el nombre y tipo |

### Leyenda de colores

| Color | Tipo |
|---|---|
| 🔵 Azul | Language |
| 🟣 Morado | Framework |
| 🟢 Verde | Library |
| 🟡 Amarillo | Tool |
| 🔴 Rojo | Database |
| 🩵 Cian | Platform |
| ⚫ Gris (rombo) | Project |

Los nodos con forma de **rombo** son proyectos. El resto son tecnologías.

---

## 6. Buscar camino entre tecnologías

La sección **Find Path** permite descubrir cómo dos tecnologías están conectadas, aunque no tengan una relación directa.

### Cómo usarlo

1. Selecciona la tecnología de origen en el desplegable **Desde**
2. Selecciona la tecnología de destino en **Hasta**
3. Pulsa **Buscar camino**

La aplicación calculará el **camino más corto** entre ambas tecnologías atravesando cualquier tipo de relación (compatible, depends_on, extends, alternative_to), con un máximo de 6 saltos.

### Ejemplo

Buscando el camino entre **TypeScript** y **PostgreSQL**:

```
TypeScript ── NestJS ── PostgreSQL
```

TypeScript no se relaciona directamente con PostgreSQL, pero a través de NestJS sí.

> Esta consulta utiliza el algoritmo `shortestPath()` de Cypher, que en una base de datos relacional requeriría consultas recursivas complejas.

---

## 7. Filtrar proyectos por stack

La sección **Filter** permite encontrar proyectos que usan **todas** las tecnologías que selecciones a la vez.

### Cómo usarlo

1. Marca una o varias tecnologías en el panel de la izquierda
2. Pulsa **Buscar**
3. Aparecerán solo los proyectos que usen **todas** las seleccionadas simultáneamente

### Ejemplo

Si seleccionas `fastapi` + `react` + `postgresql`, solo aparecerán proyectos que usen los tres a la vez — no los que usen solo uno o dos de ellos.

> Esta consulta demuestra la potencia del grafo: en SQL requeriría un JOIN por cada tecnología seleccionada.

---

## 8. Contribuir — añadir tecnologías y proyectos

Para añadir contenido necesitas una cuenta. El registro es libre y gratuito.

### Crear una cuenta

1. Haz click en **Register** en la barra de navegación
2. Introduce un nombre de usuario y contraseña
3. Ya puedes contribuir

### Añadir una tecnología

1. Haz click en **+ Technology** (barra superior) o en el botón de la página de tecnologías
2. Rellena el formulario:
   - **Name** — nombre de la tecnología
   - **Description** — descripción breve
   - **Official URL** — enlace a la web oficial (opcional)
   - **Type** — tipo: language, framework, library, tool, database, platform u other
3. Guarda

### Añadir un proyecto

1. Haz click en **+ Project**
2. Rellena el formulario:
   - **Title** — nombre del proyecto
   - **Type** — tipo de aplicación
   - **Description** — descripción breve
   - **Project URL** — enlace al repositorio o web (opcional)
   - **Technologies used** — marca todas las tecnologías que usa el proyecto
3. Guarda

### Añadir una relación entre tecnologías

1. Haz click en **⟷ Añadir relación** desde la página de tecnologías o desde el home
2. Selecciona la **Tecnología A**, el **tipo de relación** y la **Tecnología B**
3. Crea la relación

Esto enriquece el grafo y permite que las consultas de camino y compatibilidad sean más precisas.

---

## 9. Por qué una base de datos de grafos

TechGraph está construido sobre **Neo4j**, una base de datos de grafos, en lugar de una base de datos relacional clásica como PostgreSQL o MySQL.

### ¿Qué es una base de datos de grafos?

En lugar de guardar datos en tablas con filas y columnas, una base de datos de grafos los guarda como **nodos** (entidades) y **relaciones** (conexiones entre entidades). Esto la hace especialmente eficiente cuando los datos tienen muchas interconexiones.

### Comparación con SQL

| Consulta | En SQL | En Neo4j (Cypher) |
|---|---|---|
| Proyectos con Python Y React | `JOIN technologies t1 ON... JOIN technologies t2 ON... WHERE t1.slug='python' AND t2.slug='react'` | `WHERE ALL(s IN ['python','react'] WHERE s IN used_slugs)` |
| Camino entre dos tecnologías | CTEs recursivos o múltiples self-joins | `shortestPath((a)-[*..6]-(b))` |
| Tecnologías que co-ocurren | Subconsulta con GROUP BY y HAVING | `MATCH (p)-[:USES]->(t1), (p)-[:USES]->(t2) RETURN count(p)` |

Cuantas más relaciones tienen los datos, mayor es la ventaja del grafo frente al modelo relacional — tanto en simplicidad del código como en rendimiento.