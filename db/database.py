from neo4j import GraphDatabase
from settings.config import NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD


driver = GraphDatabase.driver(
    NEO4J_URL,
    auth=(NEO4J_USER, NEO4J_PASSWORD)
)
