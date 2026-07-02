import json
import os
import sys

# Add the parent directory to sys.path to allow imports from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import CATALOG_PATH, CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME, logger
import chromadb
from chromadb.utils import embedding_functions

def build_embeddings():
    if not os.path.exists(CATALOG_PATH):
        logger.error(f"Catalog file not found at {CATALOG_PATH}")
        return

    logger.info("Loading catalog...")
    with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
        catalog = json.load(f, strict=False)

    logger.info(f"Loaded {len(catalog)} assessments.")

    # Prepare data for ChromaDB
    documents = []
    metadatas = []
    ids = []

    for item in catalog:
        # Create a rich text representation for the embedding
        entity_id = item.get("entity_id")
        name = item.get("name", "")
        description = item.get("description", "")
        job_levels = item.get("job_levels_raw", "")
        keys = ", ".join(item.get("keys", []))
        test_type = item.get("test_type", "Unknown") # test_type wasn't explicit in sample, but required in output

        # Construct a document that captures the semantic meaning of the assessment
        doc = f"Name: {name}\nDescription: {description}\nJob Levels: {job_levels}\nCategories: {keys}"
        documents.append(doc)
        
        # Determine a test_type heuristic if not in catalog. 
        # The prompt says "test_type" should be returned. 
        # In the sample, OPQ32r is 'P', Java 8 is 'K'. 
        # Let's derive it from keys if missing.
        keys_list = item.get("keys", [])
        if any("Personality" in k for k in keys_list):
            derived_type = "P"
        elif any("Knowledge" in k for k in keys_list):
            derived_type = "K"
        elif any("Ability" in k for k in keys_list):
            derived_type = "A"
        else:
            derived_type = "U"
            
        metadata = {
            "name": name,
            "url": item.get("link", ""),
            "test_type": item.get("test_type", derived_type)
        }
        metadatas.append(metadata)
        ids.append(str(entity_id))

    logger.info("Initializing ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
    
    # Create or get collection
    # We delete it if it exists to rebuild from scratch
    try:
        client.delete_collection(name="shl_assessments")
    except Exception:
        pass # Collection does not exist
        
    collection = client.create_collection(
        name="shl_assessments",
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"}
    )

    logger.info("Adding documents to vector store. This may take a few minutes...")
    # Add in batches to avoid overwhelming memory/limits
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        collection.add(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        logger.info(f"Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")

    logger.info(f"Successfully embedded and saved {len(documents)} assessments to {CHROMA_PERSIST_DIR}")

if __name__ == "__main__":
    build_embeddings()
