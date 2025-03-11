from fastapi import FastAPI
import ollama
import chromadb

app = FastAPI()

# Initialisation de la base vectorielle
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="docs")

@app.post("/ingest/")
def ingest_document(id: str, content: str):
    collection.add(ids=[id], documents=[content])
    return {"message": "Document ajouté"}

@app.post("/chat/")
def chat(question: str):
    results = collection.query(query_texts=[question], n_results=3)
    context = " ".join(results["documents"]) if results["documents"] else ""
    
    response = ollama.chat("mistral", f"{context} {question}")
    return {"response": response}
