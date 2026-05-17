import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

def run_keep_awake_query():
    uri = os.environ.get("NEO4J_URI")
    user = os.environ.get("NEO4J_USERNAME")
    password = os.environ.get("NEO4J_PASSWORD")

    if not uri or not password:
        print("Error: Missing NEO4J_URI or NEO4J_PASSWORD in environment variables.")
        return

    print(f"Connecting to {uri}...")
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 AS active")
            record = result.single()
            if record and record["active"] == 1:
                print("Successfully connected to Neo4j Aura and executed keep-awake query.")
            else:
                print("Connected but failed to execute the keep-awake query correctly.")
        driver.close()
    except Exception as e:
        print(f"An error occurred while connecting to Neo4j: {e}")

if __name__ == "__main__":
    run_keep_awake_query()
