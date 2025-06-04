"""
Modul za generiranje odgovora na osnovu dohvaćenog konteksta.
Optimizovan za Zakon o radu FBiH.
"""

import logging
import re
from typing import List, Dict, Any
from src.graph_rag import GraphRAG

logger = logging.getLogger(__name__)


def generate_response(
    graph_rag: GraphRAG,
    query: str,
    context: List[Dict[str, Any]],
    response_type: str = "general",
) -> str:
    """
    Glavna funkcija za generiranje odgovora
    """
    if not context:
        return generate_no_context_response(query)

    # Pripremi kontekst prema tipu odgovora
    if response_type == "compliance":
        context_text = format_context_for_compliance(context)
        return generate_compliance_response(graph_rag, query, context_text)
    elif response_type == "legal_requirement":
        context_text = format_context_with_articles(context)
        return generate_legal_requirement_response(graph_rag, query, context_text)
    else:
        context_text = format_context_general(context)
        return generate_general_response(graph_rag, query, context_text)


def generate_compliance_response(
    graph_rag: GraphRAG, query: str, context_text: str
) -> str:
    """
    Generiše specijalizovani odgovor za compliance analizu
    """
    compliance_prompt = f"""Ti si ekspert za Zakon o radu Federacije BiH i specijalizovan si za analizu usklađenosti.

RELEVANTNE ODREDBE ZAKONA:
{context_text}

ZAHTJEV ZA ANALIZU:
{query}

Napravi detaljnu analizu usklađenosti:

1. **OPŠTA OCENA** - Da li je u skladu sa zakonom
2. **SPECIFIČNI PROBLEMI** - Konkretni prekršaji
3. **PRAVNA OSNOVA** - Tačni članovi zakona
4. **PREPORUKE** - Koraci za postizanje usklađenosti

Budi precizan i koristi konkretne članove zakona.

ODGOVOR:"""

    try:
        response = graph_rag.gemini_model.generate_content(
            compliance_prompt,
            generation_config={
                "temperature": 0.1,
                "top_p": 0.9,
                "max_output_tokens": 1200,
            },
        )
        return clean_response(response.text)
    except Exception as e:
        logger.error(f"Greška u compliance generiranju: {str(e)}")
        return f"Greška u analizi usklađenosti: {str(e)}"


def generate_legal_requirement_response(
    graph_rag: GraphRAG, query: str, context_text: str
) -> str:
    """
    Generiše odgovor fokusiran na pravne zahtjeve
    """
    legal_prompt = f"""Ti si pravni asistent za Zakon o radu Federacije BiH.

RELEVANTNE ODREDBE:
{context_text}

PITANJE:
{query}

Odgovori fokusirajući se na:

1. **GLAVNA PRAVILA** - Šta zakon nalaže/dozvoljava/zabranjuje
2. **USLOVI** - Kada se pravila primenjuju
3. **POSTUPAK** - Kako se sprovodi u praksi
4. **ČLANOVI ZAKONA** - Tačne reference

Koristi jasan jezik i navedi konkretne brojeve članaka.

ODGOVOR:"""

    try:
        response = graph_rag.gemini_model.generate_content(
            legal_prompt,
            generation_config={
                "temperature": 0.2,
                "top_p": 0.95,
                "max_output_tokens": 1000,
            },
        )
        return clean_response(response.text)
    except Exception as e:
        logger.error(f"Greška u legal requirement generiranju: {str(e)}")
        return f"Greška u generiranju pravnog odgovora: {str(e)}"


def generate_general_response(
    graph_rag: GraphRAG, query: str, context_text: str
) -> str:
    """
    Generiše opšti odgovor koristeći poboljšan prompt
    """
    general_prompt = f"""Ti si stručnjak za Zakon o radu Federacije BiH i pomaženš ljudima da razumeju svoja prava i obaveze.

RELEVANTNI DELOVI ZAKONA:
{context_text}

PITANJE KORISNIKA:
{query}

INSTRUKCIJE:
- Koristi **tekst** za bold tekst
- Za članove zakona koristi format: (Član X stav Y)
- Struktuiraj odgovor sa jasnim **podnaslovima:**
- Ne koristi *** nego samo **

Odgovori jasno i razumljivo:

1. Odgovori direktno i navedi koji član zakona se koristi (Član X stav Y)
2. Struktuiraj sa **podnaslovima:**
3. Koristi jednostavan jezik

ODGOVOR:"""

    try:
        response = graph_rag.gemini_model.generate_content(
            general_prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "max_output_tokens": 800,
            },
        )
        return clean_response(response.text)
    except Exception as e:
        logger.error(f"Greška u general generiranju: {str(e)}")
        return f"Greška u generiranju odgovora: {str(e)}"


def format_context_for_compliance(context: List[Dict[str, Any]]) -> str:
    """
    Formatira kontekst za compliance analizu
    """
    formatted_parts = []

    for i, item in enumerate(context):
        text = item["text"]
        metadata = item.get("metadata", {})

        article = metadata.get("article", "")
        chapter = metadata.get("chapter", "")

        if article:
            header = f"**{article}**"
        else:
            header = f"**Segment {i + 1}**"

        if chapter:
            header += f" - {chapter}"

        formatted_parts.append(f"{header}\n{text}\n")

    return "\n---\n".join(formatted_parts)


def format_context_with_articles(context: List[Dict[str, Any]]) -> str:
    """
    Formatira kontekst sa naglaskom na članke zakona
    """
    formatted_parts = []

    # Grupišemo po člancima
    articles_groups = {}
    other_content = []

    for item in context:
        metadata = item.get("metadata", {})
        article = metadata.get("article", "")

        if article and "član" in article.lower():
            if article not in articles_groups:
                articles_groups[article] = []
            articles_groups[article].append(item)
        else:
            other_content.append(item)

    # Prikaži članke sortirano
    sorted_articles = sorted(articles_groups.keys(), key=extract_article_number)

    for article in sorted_articles:
        items = articles_groups[article]
        formatted_parts.append(f"### {article}")

        for item in items:
            text = item["text"]
            metadata = item.get("metadata", {})
            paragraphs = metadata.get("paragraphs", "")

            if paragraphs:
                para_text = f" (Stavovi: {paragraphs})"
            else:
                para_text = ""

            formatted_parts.append(f"{text}{para_text}")

        formatted_parts.append("")

    # Dodaj ostali sadržaj
    if other_content:
        formatted_parts.append("### DODATNI SADRŽAJ")
        for item in other_content:
            text = item["text"]
            formatted_parts.append(f"{text}\n")

    return "\n".join(formatted_parts)


def format_context_general(context: List[Dict[str, Any]]) -> str:
    """
    Opšte formatiranje konteksta
    """
    formatted_parts = []

    for i, item in enumerate(context):
        text = item["text"]
        metadata = item.get("metadata", {})

        article = metadata.get("article", "")
        chapter = metadata.get("chapter", "")

        if article:
            header = f"📋 **{article}**"
        elif chapter:
            header = f"📋 {chapter}"
        else:
            header = f"📋 **Segment {i + 1}**"

        formatted_parts.append(f"{header}\n{text}\n")

    return "\n".join(formatted_parts)


def extract_article_number(article_string: str) -> int:
    """
    Izvlači broj članka za sortiranje
    """
    match = re.search(r"član\s+(\d+)", article_string.lower())
    return int(match.group(1)) if match else 999


def clean_response(response: str) -> str:
    """
    Čisti generirani odgovor od artefakata
    """
    cleaned = response.strip()

    # Ukloni problematične prefixe
    prefixes_to_remove = [
        "Assistant:",
        "AI:",
        "ODGOVOR:",
        "**ODGOVOR:**",
        "Prema Zakonu o radu Federacije BiH,",
    ]

    for prefix in prefixes_to_remove:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :].strip()

    # Popravi formatiranje
    cleaned = fix_formatting(cleaned)

    # Ukloni dvostruke prazne redove
    cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)

    return cleaned.strip()


def fix_formatting(text: str) -> str:
    """
    Popravlja problematično formatiranje
    """
    # Ukloni *** prije naslova
    text = re.sub(r"\*\*\*([^*]+?):", r"**\1:**", text)

    # Popravi formatiranje članaka u zagradama
    text = re.sub(r"\(\*\*([^)]+?)\*\*\)", r"(\1)", text)
    text = re.sub(r"\(\*\*([^)]+?)\*\*\s*\*\*([^)]+?)\*\*\)", r"(\1 \2)", text)

    # Osiguraj da naslovi budu na novom redu
    text = re.sub(r"(\*\*[^*]+?:\*\*)", r"\n\1\n", text)

    # Ukloni višestruke prazne linije
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)

    return text


def generate_no_context_response(query: str) -> str:
    """
    Generiše odgovor kada nema konteksta
    """
    query_lower = query.lower()

    if any(word in query_lower for word in ["član", "članak", "čl."]):
        return "Ne mogu pronaći informacije o navedenom članku u Zakonu o radu FBiH. Molimo proverite broj članka."

    elif "usklađenost" in query_lower or "compliance" in query_lower:
        return "Za analizu usklađenosti potreban je pristup relevantnim odredbama zakona. Molimo kontaktirajte pravnog stručnjaka."

    else:
        return "Ne mogu pronaći relevantne informacije u Zakonu o radu FBiH za vaše pitanje. Pokušajte reformulirati pitanje."
