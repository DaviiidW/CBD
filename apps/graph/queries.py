from neomodel import db


def get_compatible_technologies(tech_slug: str) -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (t:Technology {slug: $slug})
        OPTIONAL MATCH (t)-[:COMPATIBLE_WITH]-(c:Technology)
        OPTIONAL MATCH (t)-[:DEPENDS_ON]->(d:Technology)
        OPTIONAL MATCH (t)<-[:EXTENDS]-(e:Technology)
        WITH t,
             collect(DISTINCT {node: c, rel: 'compatible_with'}) +
             collect(DISTINCT {node: d, rel: 'depends_on'}) +
             collect(DISTINCT {node: e, rel: 'extended_by'}) AS related
        UNWIND related AS r
        WITH r WHERE r.node IS NOT NULL
        RETURN r.node.name AS name, r.node.slug AS slug,
               r.node.tech_type AS tech_type, r.rel AS relationship
        ORDER BY name
        """,
        {'slug': tech_slug},
    )
    return [
        {'name': r[0], 'slug': r[1], 'tech_type': r[2], 'relationship': r[3]}
        for r in results
    ]


def get_projects_by_technologies(tech_slugs: list[str]) -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (p:Project)-[:USES]->(t:Technology)
        WHERE t.slug IN $slugs
        WITH p, collect(t.slug) AS used_slugs
        WHERE ALL(s IN $slugs WHERE s IN used_slugs)
        RETURN p.title AS title, p.slug AS slug,
               p.description AS description, p.project_type AS project_type,
               p.author_username AS author
        ORDER BY title
        """,
        {'slugs': tech_slugs},
    )
    return [
        {'title': r[0], 'slug': r[1], 'description': r[2], 'project_type': r[3], 'author': r[4]}
        for r in results
    ]


def get_alternative_technologies(tech_slug: str) -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (t:Technology {slug: $slug})-[:ALTERNATIVE_TO]-(alt:Technology)
        RETURN alt.name AS name, alt.slug AS slug, alt.tech_type AS tech_type,
               alt.description AS description
        ORDER BY name
        """,
        {'slug': tech_slug},
    )
    return [
        {'name': r[0], 'slug': r[1], 'tech_type': r[2], 'description': r[3]}
        for r in results
    ]


def find_path_between_technologies(slug_a: str, slug_b: str) -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (a:Technology {slug: $slug_a}), (b:Technology {slug: $slug_b})
        MATCH path = shortestPath((a)-[*..6]-(b))
        UNWIND nodes(path) AS n
        RETURN 
            CASE WHEN n:Technology THEN n.name ELSE n.title END AS name, 
            n.slug AS slug, 
            CASE WHEN n:Technology THEN n.tech_type ELSE n.project_type END AS subtype,
            CASE WHEN n:Technology THEN 'technology' ELSE 'project' END AS type
        """,
        {'slug_a': slug_a, 'slug_b': slug_b},
    )
    return [{'name': r[0], 'slug': r[1], 'tech_type': r[2], 'type': r[3]} for r in results]


def get_technology_cooccurrence() -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (p:Project)-[:USES]->(t1:Technology),
              (p)-[:USES]->(t2:Technology)
        WHERE id(t1) < id(t2)
        RETURN t1.name AS tech_a, t1.slug AS slug_a,
               t2.name AS tech_b, t2.slug AS slug_b,
               count(p) AS projects_together
        ORDER BY projects_together DESC
        LIMIT 15
        """
    )
    return [
        {'tech_a': r[0], 'slug_a': r[1], 'tech_b': r[2], 'slug_b': r[3], 'count': r[4]}
        for r in results
    ]


def get_full_graph_data() -> dict:
    nodes_result, _ = db.cypher_query(
        """
        MATCH (n)
        WHERE n:Technology OR n:Project
        RETURN
            CASE WHEN n:Technology THEN 'technology' ELSE 'project' END AS label,
            n.uid AS uid,
            CASE WHEN n:Technology THEN n.name ELSE n.title END AS name,
            CASE WHEN n:Technology THEN n.tech_type ELSE n.project_type END AS subtype,
            n.slug AS slug
        """
    )
    edges_result, _ = db.cypher_query(
        """
        MATCH (a)-[r]->(b)
        WHERE (a:Technology OR a:Project) AND (b:Technology OR b:Project)
        RETURN a.uid AS source, b.uid AS target, type(r) AS rel_type
        """
    )
    nodes = [
        {'id': r[1], 'label': r[2], 'type': r[0], 'subtype': r[3], 'slug': r[4]}
        for r in nodes_result
    ]
    edges = [
        {'from': r[0], 'to': r[1], 'label': r[2]}
        for r in edges_result
    ]
    return {'nodes': nodes, 'edges': edges}


def get_most_connected_technologies(limit: int = 10) -> list[dict]:
    results, _ = db.cypher_query(
        """
        MATCH (t:Technology)
        OPTIONAL MATCH (t)-[r]-()
        RETURN t.name AS name, t.slug AS slug, t.tech_type AS tech_type,
               count(r) AS connections
        ORDER BY connections DESC
        LIMIT $limit
        """,
        {'limit': limit},
    )
    return [
        {'name': r[0], 'slug': r[1], 'tech_type': r[2], 'connections': r[3]}
        for r in results
    ]


def get_graph_stats() -> dict:
    results, _ = db.cypher_query(
        """
        MATCH (t:Technology) WITH count(t) AS techs
        MATCH (p:Project) WITH techs, count(p) AS projects
        MATCH ()-[r]->() WITH techs, projects, count(r) AS connections
        RETURN techs, projects, connections
        """
    )
    if results:
        return {
            'total_techs': results[0][0],
            'total_projects': results[0][1],
            'total_connections': results[0][2]
        }
    return {'total_techs': 0, 'total_projects': 0, 'total_connections': 0}