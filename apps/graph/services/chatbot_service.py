import os
import json
import urllib.request
import urllib.error
import re
from neomodel import db

def get_chatbot_response(user_message, context_tech_slug=None, history=None):
    user_message_lower = user_message.lower().strip()
    
    res_techs, _ = db.cypher_query("MATCH (t:Technology) RETURN t.name, t.slug")
    techs = [(row[0], row[1]) for row in res_techs] if res_techs else []
    
    matched_slugs = []
    
    if context_tech_slug:
        matched_slugs.append(context_tech_slug)
        
    for name, slug in techs:
        if slug in matched_slugs:
            continue
            
        pattern = r'\b' + re.escape(name.lower()) + r'\b'
        slug_pattern = r'\b' + re.escape(slug.lower()) + r'\b'
        
        if re.search(pattern, user_message_lower) or re.search(slug_pattern, user_message_lower):
            matched_slugs.append(slug)
            
    matched_slugs = matched_slugs[:8]
    
    graph_context = ""
    tech_details = []
    
    if matched_slugs:
        tech_details = get_technology_graph_context(matched_slugs)
        graph_context = format_graph_context_for_prompt(tech_details)
        
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    system_prompt = f"""
    Eres un Arquitecto de Software Experto y el Chatbot oficial de la plataforma TechGraph.
    Tu objetivo es responder de forma profesional, extremadamente directa, clara y concisa en ESPAÑOL.
    Para responder, apóyate exclusivamente en la información estructurada extraída de la base de datos Neo4j:

    --- DATOS REALES DE NEO4J ---
    {graph_context if graph_context else "No se ha mencionado ninguna tecnología específica o no está en el catálogo todavía."}
    -----------------------------

    REGLAS ESTRICTAS DE RESPUESTA (CRÍTICAS):
    1. **Sin rodeos ni saludos:** Prohibido usar saludos, bienvenidas, introducciones amigables, firmas o comentarios conversacionales del tipo "¡Hola! Bienvenido...", "Es un placer...", etc. Ve DIRECTO a la respuesta técnica.
    2. **Concisión absoluta:** Evita explicaciones extensas, consejos genéricos de relleno o divagaciones. Si te piden alternativas, muestra las alternativas directamente.
    3. **Sin preguntas de cierre:** No añadas preguntas al final de la respuesta ni ofrezcas más ayuda de forma conversacional (no digas "¿Te gustaría que...", "¿En qué más te puedo ayudar?", etc.).
    4. **Formato ultra-limpio:** Usa markdown de forma muy pulida (viñetas o una tabla sencilla si corresponde) para estructurar el resultado.
    5. **Veracidad:** Básate solo en los datos proporcionados. Si no hay información, indícalo de forma directa y corta.
    """
    
    if gemini_key:
        try:
            return call_gemini_api(gemini_key, system_prompt, user_message, history)
        except Exception as e:
            err_msg = str(e)
            if err_msg.startswith("Has agotado"):
                return f"**Error de cuota:** {err_msg}"
            return f"**Error de conexión con Google Gemini:** {err_msg}"
    else:
        return "**Servicio no configurado:** El Chatbot requiere una clave de API activa de Gemini."

def get_technology_graph_context(slugs):
    contexts = []
    for slug in slugs:
        query = """
        MATCH (t:Technology {slug: $slug})
        OPTIONAL MATCH (t)-[:ALTERNATIVE_TO]-(alt:Technology)
        OPTIONAL MATCH (t)-[:DEPENDS_ON]->(dep:Technology)
        OPTIONAL MATCH (t)-[:EXTENDS]->(ext:Technology)
        OPTIONAL MATCH (t)-[:COMPATIBLE_WITH]-(comp:Technology)
        OPTIONAL MATCH (t)-[:TAGGED_AS]->(tag:Tag)
        OPTIONAL MATCH (proj:Project)-[:USES]->(t)
        RETURN t.name AS name,
               t.description AS description,
               t.tech_type AS tech_type,
               t.license AS license,
               t.release_year AS release_year,
               t.is_open_source AS is_open_source,
               collect(distinct alt.name) AS alternativas,
               collect(distinct dep.name) AS dependencias,
               collect(distinct ext.name) AS extensiones,
               collect(distinct comp.name) AS compatibles,
               collect(distinct tag.name) AS etiquetas,
               collect(distinct proj.title) AS proyectos
        """
        res, _ = db.cypher_query(query, {"slug": slug})
        if res:
            row = res[0]
            contexts.append({
                'slug': slug,
                'name': row[0],
                'description': row[1],
                'tech_type': row[2],
                'license': row[3],
                'release_year': row[4],
                'is_open_source': row[5],
                'alternativas': row[6],
                'dependencias': row[7],
                'extensiones': row[8],
                'compatibles': row[9],
                'etiquetas': row[10],
                'proyectos': row[11]
            })
    return contexts

def format_graph_context_for_prompt(tech_details):
    context = ""
    for detail in tech_details:
        context += f"Ficha de {detail['name']}:\n"
        context += f"  - Tipo: {detail['tech_type']}\n"
        context += f"  - Descripción: {detail['description']}\n"
        context += f"  - Año Lanzamiento: {detail['release_year']}\n"
        context += f"  - Licencia: {detail['license']}\n"
        context += f"  - Código Abierto: {'Sí' if detail['is_open_source'] else 'No'}\n"
        if detail['etiquetas']:
            context += f"  - Etiquetas (Tags): {', '.join(detail['etiquetas'])}\n"
        if detail['alternativas']:
            context += f"  - Alternativas directas: {', '.join(detail['alternativas'])}\n"
        if detail['dependencias']:
            context += f"  - Depende de: {', '.join(detail['dependencias'])}\n"
        if detail['extensiones']:
            context += f"  - Es extendido por / extiende a: {', '.join(detail['extensiones'])}\n"
        if detail['compatibles']:
            context += f"  - Compatible con: {', '.join(detail['compatibles'])}\n"
        if detail['proyectos']:
            context += f"  - Utilizado en proyectos: {', '.join(detail['proyectos'])}\n"
        context += "\n"
    return context

def call_gemini_api(api_key, system_prompt, user_message, history=None):
    model = os.getenv('GEMINI_MODEL', 'gemini-flash-latest')
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    # Construir el historial estructurado de contenidos para Gemini
    contents = []
    if history:
        for msg in history:
            role = "model" if msg.get('role') in ['assistant', 'model'] else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg.get('content', '')}]
            })
    
    contents.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    body = {
        "systemInstruction": {
            "parts": [
                {"text": system_prompt}
            ]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.2
        }
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        if e.code == 429:
            try:
                error_body = e.read().decode('utf-8')
                error_json = json.loads(error_body)
                error_msg = error_json.get('error', {}).get('message', '').lower()
                
                if 'minute' in error_msg and 'request' in error_msg:
                    raise Exception("Has agotado el límite de peticiones por minuto de Gemini.")
                elif 'day' in error_msg or 'daily' in error_msg:
                    raise Exception("Has agotado el límite de peticiones por día de Gemini.")
                elif 'token' in error_msg:
                    raise Exception("Has agotado el límite de tokens por minuto de Gemini.")
                else:
                    raise Exception("Has agotado los recursos de la API de Gemini.")
            except Exception as parse_err:
                if str(parse_err).startswith("Has agotado"):
                    raise parse_err
                raise Exception("Has agotado los recursos de la API de Gemini.")
        else:
            try:
                error_body = e.read().decode('utf-8')
                raise Exception(f"HTTP {e.code} {e.reason}: {error_body}")
            except Exception:
                raise Exception(f"HTTP {e.code} {e.reason}")
