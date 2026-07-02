import os
import chromadb
from chromadb.utils import embedding_functions
from app.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL_NAME, logger

_client = None
_collection = None
_ef = None

def get_vectorstore():
    global _client, _collection, _ef
    if _client is None:
        if not os.path.exists(CHROMA_PERSIST_DIR):
            logger.warning(f"ChromaDB directory {CHROMA_PERSIST_DIR} not found. Please run scripts/build_embeddings.py first.")
            return None
            
        logger.info(f"Connecting to ChromaDB at {CHROMA_PERSIST_DIR}")
        _client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        _ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)
        
        try:
            _collection = _client.get_collection(name="shl_assessments", embedding_function=_ef)
        except ValueError:
            logger.error("Collection 'shl_assessments' does not exist. Please run scripts/build_embeddings.py.")
            return None
            
    return _collection
