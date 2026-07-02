from retriever.vectorstore import get_vectorstore
from app.config import logger

def retrieve_assessments(query: str, top_k: int = 15) -> list:
    """
    Retrieves the top-k most relevant assessments for a given query.
    Returns a list of dictionaries with document, metadata, and distance.
    """
    collection = get_vectorstore()
    if not collection:
        logger.error("Vector store not initialized. Returning empty results.")
        return []
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results and 'documents' in results and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            dists = results['distances'][0]
            
            for doc, meta, dist in zip(docs, metas, dists):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return formatted_results
    except Exception as e:
        logger.error(f"Error querying vector store: {e}")
        return []

def format_retrieval_context(results: list) -> str:
    """
    Formats the retrieval results into a string that can be injected into the prompt.
    """
    if not results:
        return "No relevant assessments found in the catalog."
        
    context_parts = []
    for i, result in enumerate(results):
        meta = result['metadata']
        content = result['content']
        part = f"--- Assessment {i+1} ---\n{content}\nURL: {meta.get('url', '')}\nTest Type: {meta.get('test_type', '')}"
        context_parts.append(part)
        
    return "\n\n".join(context_parts)
