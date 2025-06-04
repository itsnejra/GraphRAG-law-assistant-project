"""
Skripta za vizualizaciju grafa znanja.
"""

import os
import logging
from dotenv import load_dotenv
from src.embeddings import load_vectorstore
from src.graph_rag import GraphRAG

# Konfiguracija loggera
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def visualize_graph():
    """
    Generira i prikazuje vizualizaciju grafa znanja.
    """
    load_dotenv()
    
    # Učitavanje vektorske baze
    embedding_model = os.getenv('EMBEDDING_MODEL')
    vectorstore_path = os.getenv('VECTORSTORE_PATH')
    llm_model = os.getenv('LLM_MODEL')
    
    # Provjera da li vektorska baza postoji
    if not os.path.exists(vectorstore_path):
        logger.error(f"Vektorska baza ne postoji na putanji: {vectorstore_path}")
        return
    
    # Učitavanje vektorske baze
    logger.info("Učitavanje vektorske baze...")
    collection = load_vectorstore(vectorstore_path, embedding_model)
    
    # Inicijalizacija GraphRAG
    logger.info("Inicijalizacija GraphRAG...")
    graph_rag = GraphRAG(collection, embedding_model, llm_model)
    
    # Kreiranje mape za slike ako ne postoji
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "knowledge_graph.html")
    
    # Pozivanje vizualizacije
    logger.info("Generiranje vizualizacije grafa znanja...")
    limit_nodes = None  # postavi na neki broj (npr. 100) za ograničenje prikaza
    try:
        graph_rag.visualize_interactive(output_path=output_path, limit_nodes=limit_nodes)
        logger.info(f"Vizualizacija uspješno generirana i spremljena na: {output_path}")
        
        # Otvaranje vizualizacije u web browseru
        import webbrowser
        webbrowser.open('file://' + os.path.abspath(output_path))
    except Exception as e:
        logger.error(f"Greška prilikom generiranja vizualizacije: {str(e)}")

if __name__ == "__main__":
    visualize_graph()