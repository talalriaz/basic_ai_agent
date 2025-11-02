from src.retrieval.vector_db import VectorDBManager

query_text = "What is the policy for sick leave?"
vector_db_manager = VectorDBManager()
text = vector_db_manager.query_db(query_text,top_k=3)
print(text)