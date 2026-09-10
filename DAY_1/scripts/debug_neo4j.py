import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

uri = os.environ["NEO4J_URI"]
username = os.environ["NEO4J_USERNAME"]
password = os.environ["NEO4J_PASSWORD"]
env_database = os.environ.get("NEO4J_DATABASE")

print("URI:", uri)
print("Username:", username)
print("NEO4J_DATABASE env var:", env_database)

driver = GraphDatabase.driver(uri, auth=(username, password))

print("\n-- Databases visible to this user --")
with driver.session(database="system") as session:
    for record in session.run("SHOW DATABASES"):
        print(dict(record))

for db_name in [env_database, "neo4j"]:
    if not db_name:
        continue
    print(f"\n-- Counts in database '{db_name}' --")
    try:
        with driver.session(database=db_name) as session:
            node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
            rel_count = session.run("MATCH ()-->() RETURN count(*) AS c").single()["c"]
            print(f"nodes={node_count} relationships={rel_count}")
    except Exception as exc:
        print("ERROR:", exc)

driver.close()
