import requests
from fastapi import FastAPI, HTTPException
import ollama
import chromadb

app = FastAPI()

# Initialisation de la base vectorielle
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="docs")

@app.post("/chat/")
def chat(question: str):
    try:
        print(f"🟢 DEBUG - Question reçue: {question}")

        # Vérifier la base ChromaDB
        results = collection.query(query_texts=[question], n_results=1)
        print(f"🟢 DEBUG - Résultats de la recherche : {results}")

        documents = results.get("documents", [])
        flat_documents = [doc for sublist in documents for doc in sublist] if documents else []
        context = " ".join(flat_documents) if flat_documents else "Aucun contexte trouvé."

        print(f"🟢 DEBUG - Contexte envoyé à Ollama : {context}")

        # Vérifier si Ollama tourne bien
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            print(f"🟢 DEBUG - Test connexion Ollama : {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"🛑 Impossible de contacter Ollama : {str(e)}")

        # Envoi à Ollama
        print("🟢 DEBUG - Envoi de la requête à Ollama...")
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": f"{context} {question}"}]
        )

        print(f"🟢 DEBUG - Réponse brute Ollama: {response}")

        # ✅ Correction : extraire la bonne donnée
        if hasattr(response, 'message'):
            return {"response": response.message}
        elif isinstance(response, dict) and "message" in response:
            return {"response": response["message"]}
        else:
            raise HTTPException(status_code=500, detail=f"🛑 Réponse mal formattée : {response}")

    except Exception as e:
        print(f"🛑 ERREUR - {str(e)}")
        raise HTTPException(status_code=500, detail=f"🛑 Erreur lors du chat : {str(e)}")
