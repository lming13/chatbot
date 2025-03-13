from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
import chromadb

app = FastAPI()

# Initialisation de la base vectorielle
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="docs")

# Modèle de requête pour l'ingestion
class IngestRequest(BaseModel):
    id: str
    content: str

# Modèle de requête pour le chat
class ChatRequest(BaseModel):
    question: str

@app.post("/ingest/")
def ingest_document(request: IngestRequest):
    """ Ajoute un document à la base vectorielle """
    try:
        collection.add(ids=[request.id], documents=[request.content])
        return {"message": "Document ajouté avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'ingestion : {str(e)}")

@app.post("/chat/")
def chat(request: ChatRequest):
    """ Effectue une requête sur la base et génère une réponse avec Ollama """
    try:
        # Debugging: Vérifie ce que la base de données retourne
        results = collection.query(query_texts=[request.question], n_results=3)
        print(f"DEBUG - Résultats de la recherche : {results}")

        # Vérifier si "documents" est présent et éviter NoneType
        documents = results.get("documents", [])
        context = " ".join(documents) if documents else "Aucun contexte trouvé."

        # Vérifier que le modèle Ollama est bien défini et gérer les erreurs
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": f"{context} {request.question}"}])

        return {"response": response["message"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat : {str(e)}")
