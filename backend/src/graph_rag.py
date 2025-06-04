"""
GraphRAG implementacija za poboljšani retrieval sa grafom znanja.
Kombinuje vektorsku pretragu sa semantičkim vezama između članaka.
"""

import os
import logging
import numpy as np
import networkx as nx
import re
import hashlib
import colorsys
from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

logger = logging.getLogger(__name__)

try:
    from pyvis.network import Network

    PYVIS_AVAILABLE = True
except ImportError:
    PYVIS_AVAILABLE = False
    logger.warning("Pyvis nije dostupan - vizualizacija neće raditi")


class GraphRAG:
    """
    GraphRAG sistem koji kombinuje vektorsku pretragu sa grafom znanja
    """

    def __init__(
        self,
        vectorstore: chromadb.Collection,
        embedding_model_name: str,
        llm_model_name: str,
    ):
        """
        Inicijalizuje GraphRAG instancu
        """
        self.vectorstore = vectorstore
        self.embedding_model_name = embedding_model_name
        self.llm_model_name = llm_model_name

        # Inicijalizacija modela
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Gemini konfiguracija
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY nije postavljen")

        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel(llm_model_name)

        # Kreiranje grafa znanja
        self.knowledge_graph = nx.DiGraph()
        self._build_knowledge_graph()

        logger.info(
            f"GraphRAG inicijalizovan sa {len(self.knowledge_graph.nodes)} čvorova"
        )

    def _ensure_scalar(self, value):
        """
        Osigurava da je vrijednost skalarna
        """
        if isinstance(value, np.ndarray):
            return float(value.item() if value.size == 1 else np.mean(value))
        return float(value) if hasattr(value, "__float__") else value

    def _build_knowledge_graph(self) -> None:
        """
        Kreira graf znanja na osnovu podataka iz vektorske baze
        """
        collection_data = self.vectorstore.get(
            include=["documents", "metadatas", "embeddings"]
        )

        documents = collection_data.get("documents", [])
        metadatas = collection_data.get("metadatas", [])
        embeddings = collection_data.get("embeddings", [])
        ids = collection_data.get("ids", [])

        # Dodavanje čvorova
        for i, doc_id in enumerate(ids):
            if i < len(documents) and i < len(metadatas):
                # ISPRAVKA: Provjeri embeddings pravilno
                embedding_value = None
                if (
                    embeddings is not None
                    and isinstance(embeddings, list)
                    and len(embeddings) > i
                ):
                    embedding_value = embeddings[i]

                self.knowledge_graph.add_node(
                    doc_id,
                    text=documents[i],
                    metadata=metadatas[i],
                    embedding=embedding_value,
                )

        # Kreiranje veza između članaka
        self._create_article_connections()

        # Kreiranje semantičkih veza - ISPRAVKA
        if (
            embeddings is not None
            and isinstance(embeddings, list)
            and len(embeddings) > 0
        ):
            self._create_semantic_connections(ids, embeddings)

    def _create_article_connections(self):
        """
        Povezuje članke u istom poglavlju i susjedne stavove
        """
        chapters = {}

        # Grupiranje po poglavljima
        for doc_id in self.knowledge_graph.nodes:
            metadata = self.knowledge_graph.nodes[doc_id]["metadata"]
            chapter = metadata.get("chapter")
            article = metadata.get("article")

            if chapter and article:
                if chapter not in chapters:
                    chapters[chapter] = []
                chapters[chapter].append(doc_id)

        # Povezivanje članaka u poglavlju
        for chapter, article_ids in chapters.items():
            for i, doc_id1 in enumerate(article_ids):
                for j, doc_id2 in enumerate(article_ids):
                    if i != j:
                        article1 = self.knowledge_graph.nodes[doc_id1]["metadata"].get(
                            "article", ""
                        )
                        article2 = self.knowledge_graph.nodes[doc_id2]["metadata"].get(
                            "article", ""
                        )

                        num1 = self._extract_article_number(article1)
                        num2 = self._extract_article_number(article2)

                        # ISPRAVKA: Dodana provjera da su brojevi validni
                        if (
                            num1 is not None
                            and num2 is not None
                            and abs(num1 - num2) == 1
                        ):
                            if num1 < num2:
                                self.knowledge_graph.add_edge(
                                    doc_id1, doc_id2, relation="next_article"
                                )

    def _create_semantic_connections(self, ids, embeddings):
        """
        Kreira semantičke veze na osnovu sličnosti
        """
        threshold = 0.85

        # ISPRAVKA: Provjeri da su embeddings validni
        if not embeddings or not isinstance(embeddings, list):
            return

        for i, doc_id1 in enumerate(ids):
            if i < len(embeddings) and embeddings[i] is not None:
                emb1 = embeddings[i]
                for j, doc_id2 in enumerate(ids):
                    if i != j and j < len(embeddings) and embeddings[j] is not None:
                        emb2 = embeddings[j]

                        try:
                            similarity = self._compute_cosine_similarity(emb1, emb2)
                            similarity_value = self._ensure_scalar(similarity)

                            if similarity_value > threshold:
                                self.knowledge_graph.add_edge(
                                    doc_id1,
                                    doc_id2,
                                    relation="semantic_similar",
                                    weight=similarity_value,
                                )
                        except Exception as e:
                            # Preskači ako je greška u računanju sličnosti
                            continue

    def _extract_article_number(self, article_text: str) -> Optional[int]:
        """
        Izvlači broj članka iz teksta
        """
        match = re.search(r"[Čč]lan\s+(\d+)", article_text)
        return int(match.group(1)) if match else None

    def _compute_cosine_similarity(self, emb1, emb2):
        """
        Računa kosinusnu sličnost između dva vektora
        """
        a = np.array(emb1)
        b = np.array(emb2)

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))

    def retrieve(
        self, query: str, n_results: int = 5, use_graph: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Dohvaća relevantne segmente za upit
        """
        # Osnovna pretraga
        results = self.vectorstore.query(query_texts=[query], n_results=n_results)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        base_results = []
        for i in range(len(documents)):
            base_results.append(
                {
                    "text": documents[i],
                    "metadata": metadatas[i],
                    "distance": self._ensure_scalar(distances[i])
                    if distances
                    else None,
                    "id": ids[i],
                }
            )

        if not use_graph:
            return base_results

        # Poboljšanje sa grafom znanja
        return self._enhance_results_with_graph(base_results, query)

    def _enhance_results_with_graph(
        self, base_results: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Poboljšava rezultate koristeći graf znanja
        """
        if not base_results:
            return []

        base_ids = [result["id"] for result in base_results]
        expanded_ids = set(base_ids)

        # Dodavanje povezanih čvorova
        for base_id in base_ids:
            if base_id in self.knowledge_graph:
                neighbors = list(self.knowledge_graph.neighbors(base_id))

                for neighbor in neighbors:
                    if self.knowledge_graph.has_edge(base_id, neighbor):
                        edge_data = self.knowledge_graph.get_edge_data(
                            base_id, neighbor
                        )
                        relation = edge_data.get("relation", "")
                        weight = self._ensure_scalar(edge_data.get("weight", 0.0))

                        if relation == "semantic_similar" and weight > 0.9:
                            expanded_ids.add(neighbor)
                        elif relation in ["next_article", "next_paragraph"]:
                            expanded_ids.add(neighbor)

        # Dodavanje bliskih članaka iz istog poglavlja
        for base_id in base_ids:
            if base_id in self.knowledge_graph:
                node_metadata = self.knowledge_graph.nodes[base_id]["metadata"]
                chapter = node_metadata.get("chapter", "")
                article = node_metadata.get("article", "")
                article_num = self._extract_article_number(article)

                for node_id in self.knowledge_graph.nodes:
                    if node_id not in expanded_ids:
                        node_meta = self.knowledge_graph.nodes[node_id]["metadata"]

                        if node_meta.get("chapter") == chapter:
                            other_article_num = self._extract_article_number(
                                node_meta.get("article", "")
                            )

                            # ISPRAVKA: Dodana provjera da su oba broja validni
                            if (
                                article_num is not None
                                and other_article_num is not None
                                and abs(article_num - other_article_num) <= 2
                            ):
                                expanded_ids.add(node_id)

        # Kreiranje dodatnih rezultata
        additional_results = []
        for node_id in expanded_ids:
            if node_id not in base_ids and node_id in self.knowledge_graph:
                node_data = self.knowledge_graph.nodes[node_id]
                additional_results.append(
                    {
                        "text": node_data.get("text", ""),
                        "metadata": node_data.get("metadata", {}),
                        "distance": 1.0,
                        "id": node_id,
                        "source": "graph_expansion",
                    }
                )

        # Kombiniranje i rangiranje
        all_results = base_results + additional_results
        return self._rank_results(all_results, query)

    def _rank_results(
        self, results: List[Dict[str, Any]], query: str
    ) -> List[Dict[str, Any]]:
        """
        Rangira rezultate prema relevantnosti
        """
        if not results:
            return []

        query_embedding = self.embedding_model.encode(query).tolist()

        for result in results:
            text = result["text"]

            # Semantička sličnost
            text_embedding = self.embedding_model.encode(text).tolist()
            semantic_similarity = self._ensure_scalar(
                self._compute_cosine_similarity(query_embedding, text_embedding)
            )

            # Poklapanje ključnih riječi
            keyword_match = self._calculate_keyword_match(text, query)

            # Specifičnost sadržaja
            specificity = self._calculate_specificity(result)

            # Faktor izvora
            source_factor = 1.0 if result.get("source") != "graph_expansion" else 0.7

            # Konačna relevantnost
            relevance = (
                semantic_similarity * 0.5
                + keyword_match * 0.3
                + specificity * 0.1
                + source_factor * 0.1
            )

            result["relevance"] = relevance

        return sorted(results, key=lambda x: x.get("relevance", 0), reverse=True)

    def _calculate_keyword_match(self, text: str, query: str) -> float:
        """
        Računa poklapanje ključnih riječi
        """
        text_lower = text.lower()
        query_words = query.lower().split()

        matches = sum(1 for word in query_words if word in text_lower)
        return matches / len(query_words) if query_words else 0.0

    def _calculate_specificity(self, result: Dict[str, Any]) -> float:
        """
        Procjenjuje specifičnost sadržaja
        """
        metadata = result.get("metadata", {})

        if metadata.get("paragraphs"):
            return 1.0

        article = metadata.get("article", "")
        if article and self._extract_article_number(article) is not None:
            return 0.8

        return 0.5

    def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        """
        Generira odgovor koristeći Gemini model
        """
        formatted_context = self._format_context(context)
        prompt = self._create_prompt(query, formatted_context)

        try:
            generation_config = {
                "temperature": 0.2,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }

            response = self.gemini_model.generate_content(
                prompt, generation_config=generation_config
            )

            return self._clean_response(response.text)

        except Exception as e:
            logger.error(f"Greška generiranja odgovora: {str(e)}")
            return "Došlo je do greške prilikom generiranja odgovora."

    def _format_context(self, context: List[Dict[str, Any]]) -> str:
        """
        Formatira kontekst za model
        """
        formatted_parts = []

        for i, item in enumerate(context):
            text = item["text"]
            metadata = item.get("metadata", {})

            chapter = metadata.get("chapter", "")
            article = metadata.get("article", "")

            if chapter and article:
                header = f"[{chapter} - {article}]"
            elif article:
                header = f"[{article}]"
            else:
                header = f"[Segment {i + 1}]"

            formatted_parts.append(f"{header}\n{text}\n")

        return "\n".join(formatted_parts)

    def _create_prompt(self, query: str, context: str) -> str:
        """
        Kreira prompt za Gemini model
        """
        prompt = f"""Ti si pravni asistent za Zakon o radu Federacije BiH.

Relevantni dijelovi zakona:
{context}

Pitanje korisnika: {query}

Odgovori jasno i koncizno koristeći samo informacije iz datog konteksta. 
Navedi konkretne brojeve članaka i stavova gdje je primjenjivo.
Ako ne možeš odgovoriti na osnovu konteksta, jasno to naznači."""

        return prompt

    def _clean_response(self, response: str) -> str:
        """
        Čisti generirani odgovor
        """
        cleaned = response.strip()

        prefixes_to_remove = ["Assistant:", "AI:", "<assistant>"]
        for prefix in prefixes_to_remove:
            if cleaned.startswith(prefix):
                cleaned = cleaned[len(prefix) :].strip()

        return cleaned

    def visualize_graph(self, output_path="knowledge_graph.html", limit_nodes=50):
        """
        Kreira interaktivnu vizualizaciju grafa znanja
        """
        if not PYVIS_AVAILABLE:
            logger.warning("Pyvis nije instaliran - vizualizacija nije moguća")
            return None

        # Ograniči broj čvorova za performanse
        vis_graph = self.knowledge_graph.copy()
        if limit_nodes and limit_nodes < len(vis_graph.nodes):
            important_nodes = sorted(
                vis_graph.degree, key=lambda x: x[1], reverse=True
            )[:limit_nodes]
            nodes_to_keep = [node for node, _ in important_nodes]
            nodes_to_remove = [
                node for node in vis_graph.nodes if node not in nodes_to_keep
            ]
            vis_graph.remove_nodes_from(nodes_to_remove)

        # Kreiranje Pyvis mreže
        net = Network(height="600px", width="100%", notebook=False, directed=True)

        # Dodavanje čvorova
        for node in vis_graph.nodes:
            node_data = vis_graph.nodes[node]
            metadata = node_data.get("metadata", {})
            article = metadata.get("article", "")
            chapter = metadata.get("chapter", "Nepoznato")

            # Kratki tekst za prikaz
            text = node_data.get("text", "")[:100] + "..."

            # Broj članka za label
            article_num = self._extract_article_number(article)
            article_label = str(article_num) if article_num is not None else "?"

            # Boja prema poglavlju
            color = self._get_color_for_chapter(chapter)

            net.add_node(
                node,
                label=f"Čl.{article_label}",
                title=f"{article}<br>{text}",
                color=color,
                size=15 + (vis_graph.degree(node) * 3),
            )

        # Dodavanje veza
        edge_colors = {
            "next_article": "#0077cc",
            "semantic_similar": "#cc0000",
            "default": "#999999",
        }

        for u, v, data in vis_graph.edges(data=True):
            relation = data.get("relation", "default")
            color = edge_colors.get(relation, edge_colors["default"])

            net.add_edge(u, v, color=color, title=relation)

        # Osnovne opcije
        net.set_options("""
        var options = {
          "physics": {"enabled": true, "stabilization": {"iterations": 100}},
          "interaction": {"navigationButtons": true}
        }
        """)

        # Spremanje
        os.makedirs(
            os.path.dirname(output_path) if os.path.dirname(output_path) else ".",
            exist_ok=True,
        )
        net.save_graph(output_path)

        logger.info(f"Graf vizualizacija spremljena: {output_path}")
        return output_path

    def _get_color_for_chapter(self, chapter):
        """
        Generira konzistentnu boju za poglavlje
        """
        hash_object = hashlib.md5(chapter.encode())
        hash_hex = hash_object.hexdigest()

        h = int(hash_hex[:2], 16) / 255.0
        s = 0.7
        l = 0.6

        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
