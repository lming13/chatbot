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
        results = collection.query(query_texts=[request.question], n_results=1)
        print(f"DEBUG - Résultats de la recherche : {results}")

        # Vérifier et aplatir les documents récupérés
        documents = results.get("documents", [])
        flat_documents = [doc for sublist in documents for doc in sublist]  # Aplatir les listes
        context = " ".join(flat_documents) if flat_documents else "Aucun contexte trouvé."

        # Vérifier que le modèle Ollama est bien défini et gérer les erreurs
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": f"{context} {request.question}"}]
        )

        return {"response": response["message"]}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chat : {str(e)}")
