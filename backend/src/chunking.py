"""
Modul za segmentaciju teksta zakona sa semantičkim pristupom
"""

import re
import logging
from typing import List, Dict, Any
import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


def create_chunks(
    text: str, chunk_size: int = 500, chunk_overlap: int = 100, method: str = "semantic"
) -> List[Dict[str, Any]]:
    """
    Glavna funkcija za segmentaciju pravnog teksta
    """
    if method == "legal":
        return legal_chunking(text, chunk_size, chunk_overlap)
    elif method == "basic":
        return basic_chunking(text, chunk_size, chunk_overlap)
    else:
        return semantic_chunking(text, chunk_size, chunk_overlap)


def basic_chunking(
    text: str, chunk_size: int = 500, chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Osnovna segmentacija na fiksne blokove
    """
    chunks = []
    sentences = sent_tokenize(text)

    current_chunk = []
    current_size = 0

    for i, sentence in enumerate(sentences):
        sentence_size = len(sentence)

        if current_size + sentence_size > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": {
                        "source": "basic_chunking",
                        "start_idx": i - len(current_chunk),
                        "end_idx": i - 1,
                    },
                }
            )

            # Preklapanje - zadržaj zadnje rečenice
            overlap_size = min(chunk_overlap // 50, len(current_chunk))
            current_chunk = current_chunk[-overlap_size:] if overlap_size > 0 else []
            current_size = sum(len(s) for s in current_chunk)

        current_chunk.append(sentence)
        current_size += sentence_size

    # Dodaj preostali chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append(
            {
                "text": chunk_text,
                "metadata": {
                    "source": "basic_chunking",
                    "start_idx": len(sentences) - len(current_chunk),
                    "end_idx": len(sentences) - 1,
                },
            }
        )

    return chunks


def semantic_chunking(
    text: str, chunk_size: int = 500, chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Semantička segmentacija po člancima i stavovima
    """
    chunks = []

    # Prepoznavanje poglavlja
    chapter_pattern = r"\n\s*([IVX]+\.?\s+[A-ZŠĐČĆŽ].*?)\n"
    article_pattern = r"\n\s*([Čč]lan\s+\d+\.?)\s*\n"

    chapter_splits = re.split(chapter_pattern, text)
    current_chapter = "Uvod"

    for i, section in enumerate(chapter_splits):
        if i % 2 == 1:  # Naslov poglavlja
            current_chapter = section.strip()
        elif i > 0 and i % 2 == 0:  # Sadržaj poglavlja
            # Podijeli po člancima
            article_splits = re.split(article_pattern, section)
            current_article = None

            for j, art_section in enumerate(article_splits):
                if j % 2 == 1:  # Naslov članka
                    current_article = art_section.strip()
                elif j > 0 and j % 2 == 0 and current_article:  # Sadržaj članka
                    process_article(
                        chunks,
                        current_chapter,
                        current_article,
                        art_section,
                        chunk_size,
                    )

    return chunks


def process_article(
    chunks: List[Dict], chapter: str, article: str, content: str, chunk_size: int
):
    """
    Obrađuje pojedinačni članak i dijeli ga po stavovima ako je potrebno
    """
    if len(content) <= chunk_size:
        # Članak je dovoljno mali
        chunks.append(
            {
                "text": f"{article}\n{content.strip()}",
                "metadata": {
                    "source": "semantic_chunking",
                    "chapter": chapter,
                    "article": article,
                },
            }
        )
    else:
        # Podijeli po stavovima
        paragraph_pattern = r"\n\s*\((\d+)\)\s+"
        paragraph_splits = re.split(paragraph_pattern, content)

        current_text = f"{article}\n"
        current_paragraphs = []

        for k, para_section in enumerate(paragraph_splits):
            if k == 0:
                current_text += para_section.strip()
            elif k % 2 == 1:  # Broj stava
                current_paragraph = para_section.strip()
            elif k % 2 == 0:  # Sadržaj stava
                para_content = para_section.strip()
                para_text = f"\n({current_paragraph}) {para_content}"

                # Provjeri veličinu
                if (
                    len(current_text + para_text) > chunk_size
                    and len(current_text) > len(article) + 10
                ):
                    chunks.append(
                        {
                            "text": current_text,
                            "metadata": {
                                "source": "semantic_chunking",
                                "chapter": chapter,
                                "article": article,
                                "paragraphs": ",".join(current_paragraphs),
                            },
                        }
                    )

                    # Novi chunk sa preklapanjem
                    current_text = f"{article}\n({current_paragraph}) {para_content}"
                    current_paragraphs = [current_paragraph]
                else:
                    current_text += para_text
                    current_paragraphs.append(current_paragraph)

        # Dodaj preostali tekst
        if current_text != f"{article}\n":
            chunks.append(
                {
                    "text": current_text,
                    "metadata": {
                        "source": "semantic_chunking",
                        "chapter": chapter,
                        "article": article,
                        "paragraphs": ",".join(current_paragraphs)
                        if current_paragraphs
                        else "",
                    },
                }
            )


def legal_chunking(
    text: str, chunk_size: int = 500, chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Napredna pravna segmentacija koja poštuje strukturu zakona
    """
    chunks = []

    # Prepoznavanje glavnih dijelova
    chapter_matches = list(re.finditer(r"([IVX]+\.?\s+[A-ZŠĐČĆŽ].*?)\n", text))
    if not chapter_matches:
        logger.warning(
            "Nije pronađena pravna struktura, koristi se osnovna segmentacija"
        )
        return basic_chunking(text, chunk_size, chunk_overlap)

    last_end = 0
    for i, match in enumerate(chapter_matches):
        chapter_title = match.group(1).strip()
        start = match.start()

        if i > 0:
            end = start
            chapter_content = text[last_end:end]
            prev_chapter_title = chapter_matches[i - 1].group(1).strip()

            # Obradi članke u poglavlju
            chapter_chunks = process_chapter_articles(
                chapter_content, prev_chapter_title, chunk_size
            )
            chunks.extend(chapter_chunks)

        last_end = start

    # Dodaj zadnje poglavlje
    if last_end < len(text) and chapter_matches:
        chapter_content = text[last_end:].strip()
        last_chapter_title = chapter_matches[-1].group(1).strip()
        chapter_chunks = process_chapter_articles(
            chapter_content, last_chapter_title, chunk_size
        )
        chunks.extend(chapter_chunks)

    return chunks if chunks else basic_chunking(text, chunk_size, chunk_overlap)


def process_chapter_articles(
    content: str, chapter_title: str, chunk_size: int
) -> List[Dict]:
    """
    Obrađuje članke unutar poglavlja
    """
    chunks = []
    article_matches = list(re.finditer(r"([Čč]lan\s+\d+\.?)\s*\n", content))

    if not article_matches:
        # Nema članaka, koristi osnovnu segmentaciju
        chapter_chunks = basic_chunking(content, chunk_size, 100)
        for chunk in chapter_chunks:
            chunk["metadata"]["chapter"] = chapter_title
            chunk["metadata"]["source"] = "legal_chunking"
        return chapter_chunks

    prev_end = 0
    for i, art_match in enumerate(article_matches):
        article_title = art_match.group(1).strip()
        start = art_match.start()

        if i > 0:
            end = start
            article_content = content[prev_end:end]
            prev_article_title = article_matches[i - 1].group(1).strip()

            # Obradi članak
            process_single_article(
                chunks, chapter_title, prev_article_title, article_content, chunk_size
            )

        prev_end = start

    # Dodaj zadnji članak
    if prev_end < len(content) and article_matches:
        article_content = content[prev_end:].strip()
        last_article_title = article_matches[-1].group(1).strip()
        process_single_article(
            chunks, chapter_title, last_article_title, article_content, chunk_size
        )

    return chunks


def process_single_article(
    chunks: List[Dict], chapter: str, article: str, content: str, chunk_size: int
):
    """
    Obrađuje pojedinačni članak sa stavovima
    """
    if len(content) <= chunk_size:
        chunks.append(
            {
                "text": f"{article}\n{content.strip()}",
                "metadata": {
                    "source": "legal_chunking",
                    "chapter": chapter,
                    "article": article,
                },
            }
        )
    else:
        # Podijeli po stavovima
        paragraph_matches = list(re.finditer(r"\((\d+)\)\s+", content))

        if paragraph_matches:
            current_chunk_text = f"{article}\n"
            current_paragraphs = ""
            prev_end = 0

            for j, para_match in enumerate(paragraph_matches):
                para_num = para_match.group(1)
                para_start = para_match.start()

                if j > 0:
                    para_content = content[prev_end:para_start].strip()
                    prev_para_num = paragraph_matches[j - 1].group(1)
                    para_text = f"({prev_para_num}) {para_content}"

                    if len(current_chunk_text + para_text) > chunk_size:
                        chunks.append(
                            {
                                "text": current_chunk_text.strip(),
                                "metadata": {
                                    "source": "legal_chunking",
                                    "chapter": chapter,
                                    "article": article,
                                    "paragraphs": current_paragraphs,
                                },
                            }
                        )

                        current_chunk_text = f"{article}\n"
                        current_paragraphs = ""

                    current_chunk_text += para_text + "\n"
                    current_paragraphs += (
                        "," if current_paragraphs else ""
                    ) + prev_para_num

                prev_end = para_start

            # Dodaj zadnji stav
            if prev_end < len(content):
                para_content = content[prev_end:].strip()
                if paragraph_matches:
                    last_para_num = paragraph_matches[-1].group(1)
                    para_text = f"({last_para_num}) {para_content}"
                    current_chunk_text += para_text
                    current_paragraphs += (
                        "," if current_paragraphs else ""
                    ) + last_para_num

            if current_chunk_text != f"{article}\n":
                chunks.append(
                    {
                        "text": current_chunk_text.strip(),
                        "metadata": {
                            "source": "legal_chunking",
                            "chapter": chapter,
                            "article": article,
                            "paragraphs": current_paragraphs,
                        },
                    }
                )
        else:
            # Nema stavova, koristi osnovnu segmentaciju
            article_chunks = basic_chunking(content, chunk_size, 100)
            for chunk in article_chunks:
                chunk["metadata"]["chapter"] = chapter
                chunk["metadata"]["article"] = article
                chunk["metadata"]["source"] = "legal_chunking"
                chunk["text"] = f"{article}\n{chunk['text']}"
                chunks.append(chunk)
