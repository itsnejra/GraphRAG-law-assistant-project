"""
Modul za pretragu i dohvat relevantnih dokumenata koristeći GraphRAG.
Optimizovan za Zakon o radu FBiH.
"""

import logging
import re
from typing import List, Dict, Any
from src.graph_rag import GraphRAG

logger = logging.getLogger(__name__)

# Ključne riječi za različite oblasti radnog prava
EMPLOYMENT_KEYWORDS = {
    "salary": ["plata", "plaća", "naknada", "minimalna", "isplata", "obračun"],
    "working_time": [
        "radno vreme",
        "radno vrijeme",
        "sati",
        "prekovremeno",
        "noćni rad",
    ],
    "contract": ["ugovor", "sadržaj", "elementi", "obavezno", "forma", "potpis"],
    "vacation": ["godišnji odmor", "odmor", "odsustvo"],
    "termination": ["otkaz", "prestanak", "raskid", "otkazni rok"],
    "probation": ["probni rad", "probni period", "iskusni rad"],
    "pregnancy": ["trudnoća", "trudnica", "porodiljno", "majčinstvo"],
    "health_safety": ["bezbednost", "sigurnost", "zdravlje", "zaštita na radu"],
}


def retrieve_context(
    graph_rag: GraphRAG, query: str, n_results: int = 8, analysis_type: str = "general"
) -> List[Dict[str, Any]]:
    """
    Glavna funkcija za dohvaćanje konteksta
    """
    logger.info(f"Dohvaćanje konteksta za: {query}")

    if analysis_type == "compliance":
        return retrieve_compliance_context(graph_rag, query, n_results)
    elif analysis_type == "contract_analysis":
        return retrieve_contract_context(graph_rag, query, n_results)
    else:
        return retrieve_general_context(graph_rag, query, n_results)


def retrieve_compliance_context(
    graph_rag: GraphRAG, query: str, n_results: int = 8
) -> List[Dict[str, Any]]:
    """
    Specijalizovano dohvaćanje za compliance analizu
    """
    # Identificiraj relevantne oblasti
    relevant_areas = identify_relevant_areas(query)

    all_results = []

    # Pretraži svaku oblast
    for area, keywords in relevant_areas.items():
        for keyword in keywords[:2]:  # Uzmi prva 2 ključna pojma
            enhanced_query = f"{query} {keyword}"
            results = graph_rag.retrieve(enhanced_query, n_results=3, use_graph=True)

            for result in results:
                result["employment_area"] = area
                result["compliance_score"] = calculate_compliance_score(result["text"])
                all_results.append(result)

    # Ako nema rezultata, koristi osnovnu pretragu
    if not all_results:
        all_results = graph_rag.retrieve(query, n_results=n_results, use_graph=True)

    # Ukloni duplikate i rangiraj
    unique_results = remove_duplicates(all_results)
    return rank_compliance_results(unique_results, query)[:n_results]


def retrieve_contract_context(
    graph_rag: GraphRAG, query: str, n_results: int = 8
) -> List[Dict[str, Any]]:
    """
    Specijalizovano dohvaćanje za analizu ugovora
    """
    # Ključne oblasti za ugovore
    contract_queries = [
        "obavezni sadržaj ugovora o radu",
        "elementi ugovora o radu",
        "forma ugovora o radu",
        "uslovi rada definicija",
    ]

    all_results = []

    # Pretraži svaku oblast
    for contract_query in contract_queries:
        results = graph_rag.retrieve(contract_query, n_results=2, use_graph=True)
        for result in results:
            result["contract_relevance"] = calculate_contract_relevance(result["text"])
            all_results.append(result)

    # Dodaj rezultate za originalni upit
    query_results = graph_rag.retrieve(query, n_results=n_results // 2, use_graph=True)
    for result in query_results:
        result["contract_relevance"] = calculate_contract_relevance(result["text"])
        all_results.append(result)

    # Filtriraj i rangiraj
    unique_results = remove_duplicates(all_results)
    return sorted(
        unique_results, key=lambda x: x.get("contract_relevance", 0), reverse=True
    )[:n_results]


def retrieve_general_context(
    graph_rag: GraphRAG, query: str, n_results: int = 8
) -> List[Dict[str, Any]]:
    """
    Općenito dohvaćanje konteksta
    """
    # Analiziraj i proširi upit
    enhanced_query = enhance_query(query)

    # Prilagodi broj rezultata
    adjusted_n = adjust_result_count(query, n_results)

    # Dohvati rezultate
    results = graph_rag.retrieve(enhanced_query, n_results=adjusted_n, use_graph=True)

    # Filtriraj i vrati
    return filter_results(results, query)


def identify_relevant_areas(query: str) -> Dict[str, List[str]]:
    """
    Identificira relevantne oblasti radnog prava
    """
    query_lower = query.lower()
    relevant_areas = {}

    for area, keywords in EMPLOYMENT_KEYWORDS.items():
        matching_keywords = [kw for kw in keywords if kw in query_lower]
        if matching_keywords:
            relevant_areas[area] = matching_keywords

    # Ako nema poklapanja, vrati sve glavne oblasti
    if not relevant_areas:
        return {"general": ["radni odnos", "zakon o radu", "radnik", "poslodavac"]}

    return relevant_areas


def calculate_compliance_score(text: str) -> float:
    """
    Računa compliance score za tekst
    """
    text_lower = text.lower()
    score = 0.0

    # Bonus za članke zakona
    if re.search(r"član\s+\d+", text_lower):
        score += 0.3

    # Bonus za obveze
    obligation_words = ["mora", "treba", "obavezno", "potrebno", "zahteva"]
    for word in obligation_words:
        if word in text_lower:
            score += 0.1

    # Bonus za specifične podatke
    if re.search(r"\d+", text_lower):
        score += 0.1

    return min(1.0, score)


def calculate_contract_relevance(text: str) -> float:
    """
    Računa relevantnost za ugovore o radu
    """
    text_lower = text.lower()
    relevance = 0.0

    contract_keywords = ["ugovor", "sadržaj", "elementi", "obavezno", "forma", "potpis"]
    for keyword in contract_keywords:
        if keyword in text_lower:
            relevance += 0.15

    structural_elements = [
        "naziv",
        "adresa",
        "datum",
        "pozicija",
        "plata",
        "radno vreme",
    ]
    for element in structural_elements:
        if element in text_lower:
            relevance += 0.05

    return min(1.0, relevance)


def rank_compliance_results(
    results: List[Dict[str, Any]], query: str
) -> List[Dict[str, Any]]:
    """
    Rangira rezultate za compliance analizu
    """

    def compliance_key(result):
        compliance_score = result.get("compliance_score", 0.0)
        relevance = result.get("relevance", 0.0)
        distance = result.get("distance", 1.0)

        # Manji distance = veća relevantnost
        distance_score = 1.0 - min(distance, 1.0)

        return compliance_score * 0.4 + relevance * 0.3 + distance_score * 0.3

    return sorted(results, key=compliance_key, reverse=True)


def remove_duplicates(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Uklanja duplikate na osnovu sličnosti teksta
    """
    unique_results = []
    seen_texts = set()

    for result in results:
        # Pojednostavljeni tekst za usporedbu
        simplified_text = result["text"][:100].lower().replace(" ", "")

        if simplified_text not in seen_texts:
            unique_results.append(result)
            seen_texts.add(simplified_text)

    return unique_results


def enhance_query(query: str) -> str:
    """
    Poboljšava upit dodavanjem relevantnih pojmova
    """
    query_lower = query.lower()

    # Mapa proširenja
    enhancements = {
        "otpustiti": "otkaz prestanak radnog odnosa",
        "plata": "plaća naknada zarada",
        "trudnoća": "trudnica porodiljno majčinstvo",
        "godišnji": "odmor odsustvo vacation",
        "prekovremeno": "prekovremen rad dodatni sati",
        "bolovanje": "bolest privremena spriječenost",
        "ugovor": "sporazum contract angažman",
    }

    enhanced_terms = []
    for key, enhancement in enhancements.items():
        if key in query_lower:
            enhanced_terms.append(enhancement)

    # Prepoznavanje članaka
    article_matches = re.findall(r"(?:član|članak|čl\.)\s*(\d+)", query_lower)
    for match in article_matches:
        enhanced_terms.extend([f"član {match}", f"čl. {match}"])

    if enhanced_terms:
        return f"{query} {' '.join(enhanced_terms[:3])}"  # Ograniči na 3 dodatna pojma

    return query


def adjust_result_count(query: str, default_n: int) -> int:
    """
    Prilagođava broj rezultata prema složenosti upita
    """
    query_lower = query.lower()

    # Specifični članci - manje rezultata
    if re.search(r"član\s+\d+", query_lower):
        return max(3, default_n - 2)

    # Compliance upiti - više rezultata
    if any(word in query_lower for word in ["usklađenost", "compliance", "analiza"]):
        return default_n + 3

    # Općeniti upiti - više rezultata
    if any(word in query_lower for word in ["kako", "šta je", "objasni"]):
        return default_n + 2

    return default_n


def filter_results(results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """
    Filtrira i sortira rezultate prema relevantnosti
    """
    if not results:
        return []

    # Sortiranje prema relevantnosti ili distance
    if "relevance" in results[0]:
        sorted_results = sorted(
            results, key=lambda x: x.get("relevance", 0), reverse=True
        )
    else:
        sorted_results = sorted(results, key=lambda x: x.get("distance", 1.0))

    # Uklanjanje duplikata
    return remove_duplicates(sorted_results)
