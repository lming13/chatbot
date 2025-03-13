from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import chromadb

app = FastAPI()

# Initialisation de la base vectorielle
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="docs")

# Modèle de requête
class ChatRequest(BaseModel):
    question: str

@app.post("/chat/")
def chat(request: ChatRequest):
    """ Recherche dans la base ChromaDB et génère une réponse avec Ollama """
    try:
        # Effectuer une recherche dans ChromaDB
        results = collection.query(query_texts=[request.question], n_results=1)
        print(f"DEBUG - Résultats de la recherche : {results}")  # Debugging

        # Vérifier si "documents" est bien dans les résultats
        documents = results.get("documents", [])
        if not documents or not any(documents):
            context = "Aucun contexte trouvé."
        else:
            # Aplatir les listes de listes pour obtenir une seule liste
            flat_documents = [doc for sublist in documents for doc in sublist]
            context = " ".join(flat_documents) if flat_documents else "Aucun contexte trouvé."

  
