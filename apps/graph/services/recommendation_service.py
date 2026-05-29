import logging
from neomodel import db

logger = logging.getLogger(__name__)


class GDSNotAvailableError(RuntimeError):
    pass


def is_gds_available():
    try:
        res, _ = db.cypher_query("SHOW PROCEDURES YIELD name WHERE name = 'gds.graph.exists' RETURN count(name) > 0")
        return res and res[0][0]
    except Exception:
        return False


def clear_similarities():
    logger.info("Eliminando relaciones SIMILAR_TO previas...")
    query = "MATCH (:User)-[r:SIMILAR_TO]->(:User) DELETE r"
    db.cypher_query(query)


def create_projection(projection_name="user-tech-likes"):
    logger.info(f"Comprobando existencia de proyección '{projection_name}'...")
    exists_query = "CALL gds.graph.exists($name) YIELD exists"
    res, _ = db.cypher_query(exists_query, {"name": projection_name})
    
    if res and res[0][0]:
        logger.info(f"Destruyendo proyección existente '{projection_name}'...")
        db.cypher_query("CALL gds.graph.drop($name)", {"name": projection_name})

    logger.info(f"Creando proyección '{projection_name}'...")
    project_query = """
    CALL gds.graph.project(
        $name,
        {
            User: { label: 'User' },
            Technology: { label: 'Technology' }
        },
        {
            LIKES: {
                type: 'LIKES',
                orientation: 'NATURAL'
            }
        }
    )
    """
    db.cypher_query(project_query, {"name": projection_name})


def run_node_similarity(projection_name="user-tech-likes"):
    logger.info(f"Ejecutando NodeSimilarity sobre '{projection_name}'...")
    similarity_query = """
    CALL gds.nodeSimilarity.write(
        $name,
        {
            writeRelationshipType: 'SIMILAR_TO',
            writeProperty: 'score',
            similarityCutoff: 0.1,
            degreeCutoff: 1
        }
    )
    """
    results, _ = db.cypher_query(similarity_query, {"name": projection_name})
    return results


def drop_projection(projection_name="user-tech-likes"):
    logger.info(f"Destruyendo proyección '{projection_name}' para liberar memoria...")
    exists_query = "CALL gds.graph.exists($name) YIELD exists"
    res, _ = db.cypher_query(exists_query, {"name": projection_name})
    if res and res[0][0]:
        db.cypher_query("CALL gds.graph.drop($name)", {"name": projection_name})


def recompute_all(projection_name="user-tech-likes"):
    if not is_gds_available():
        raise GDSNotAvailableError(
            "El plugin de Neo4j 'Graph Data Science' (GDS) no está instalado o no se encuentra habilitado en tu base de datos Neo4j. "
            "Por favor, instálalo en tu servidor o actívalo en Neo4j Desktop (o añade NEO4J_PLUGINS=['graph-data-science'] en Docker) "
            "para poder usar las recomendaciones basadas en similitudes colaborativas."
        )

    logger.info("Iniciando recálculo completo de similitudes en Neo4j GDS...")
    clear_similarities()
    create_projection(projection_name)
    stats = run_node_similarity(projection_name)
    drop_projection(projection_name)
    logger.info("Recálculo GDS completado con éxito.")
    return stats


def get_recommendations(username, limit=10):
    query = """
    MATCH (u:User {username: $username})-[s:SIMILAR_TO]-(other:User)
    MATCH (other)-[:LIKES]->(tech:Technology)
    WHERE NOT (u)-[:LIKES]->(tech)
    RETURN tech.name AS name,
           tech.slug AS slug,
           tech.tech_type AS tech_type,
           tech.description AS description,
           sum(s.score) AS recommendation_score,
           collect(distinct other.username) AS similar_users
    ORDER BY recommendation_score DESC
    LIMIT $limit
    """
    results, _ = db.cypher_query(query, {"username": username, "limit": limit})
    
    return [
        {
            "name": row[0],
            "slug": row[1],
            "tech_type": row[2],
            "description": row[3],
            "score": round(row[4], 3),
            "similar_users": row[5]
        }
        for row in results
    ]


def get_fallback_recommendations(username, limit=10):
    query = """
    MATCH (u:User {username: $username})-[:LIKES]->(liked:Technology)-[:TAGGED_AS]->(tag:Tag)<-[:TAGGED_AS]-(rec:Technology)
    WHERE NOT (u)-[:LIKES]->(rec) AND rec <> liked
    RETURN rec.name AS name,
           rec.slug AS slug,
           rec.tech_type AS tech_type,
           rec.description AS description,
           count(tag) AS recommendation_score,
           collect(distinct liked.name) AS reason
    ORDER BY recommendation_score DESC
    LIMIT $limit
    """
    results, _ = db.cypher_query(query, {"username": username, "limit": limit})
    
    return [
        {
            "name": row[0],
            "slug": row[1],
            "tech_type": row[2],
            "description": row[3],
            "score": int(row[4]),
            "reason": row[5]
        }
        for row in results
    ]


def get_similar_users(username, limit=5):
    query = """
    MATCH (u:User {username: $username})-[s:SIMILAR_TO]-(other:User)
    RETURN other.username AS username, s.score AS score
    ORDER BY score DESC
    LIMIT $limit
    """
    results, _ = db.cypher_query(query, {"username": username, "limit": limit})
    
    return [
        {
            "username": row[0],
            "score": round(row[1] * 100, 1)
        }
        for row in results
    ]

