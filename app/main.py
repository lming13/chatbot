
from fastapi import FastAPI, HTTPException
import ollama
import chromadb
import time

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

        # ✅ Exécuter Ollama avec un timeout plus long
        print("🟢 DEBUG - Envoi de la requête à Ollama...")
        start_time = time.time()

        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": f"{context} {question}"}],
            options={"timeout": 120}  # ⏳ Timeout augmenté à 120s
        )

        elapsed_time = time.time() - start_time
                                                                                                                7,15           7%
