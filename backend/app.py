from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import logging
import traceback
import json
import time
import re
import PIL.Image
import fitz  # pymupdf za PDF čitanje
from werkzeug.utils import secure_filename
from src.chunking import create_chunks
from src.embeddings import create_embeddings, load_vectorstore
from src.graph_rag import GraphRAG
from src.retrieval import retrieve_context
from src.generation import generate_response

from collections import defaultdict
from datetime import datetime, timedelta
import uuid

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

app = Flask(__name__)
CORS(
    app,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Session-ID"],
)

graph_rag = None

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "pdf"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conversation_memory = defaultdict(list)
session_cleanup_time = {}
MAX_CONVERSATION_HISTORY = 8
SESSION_TIMEOUT_MINUTES = 30
MAX_MEMORY_LENGTH = 2000

SUPPORTED_LANGUAGES = {
    "bs": {"name": "Bosanski", "code": "bs"},
    "sr": {"name": "Српски", "code": "sr"},
    "hr": {"name": "Hrvatski", "code": "hr"},
    "en": {"name": "English", "code": "en"},
    "de": {"name": "Deutsch", "code": "de"},
}


def cleanup_old_sessions():
    current_time = datetime.now()
    timeout_delta = timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    sessions_to_remove = []
    for session_id, last_activity in session_cleanup_time.items():
        if current_time - last_activity > timeout_delta:
            sessions_to_remove.append(session_id)
    for session_id in sessions_to_remove:
        if session_id in conversation_memory:
            del conversation_memory[session_id]
        if session_id in session_cleanup_time:
            del session_cleanup_time[session_id]


def get_or_create_session_id(request):
    session_id = request.headers.get("X-Session-ID")
    if not session_id and request.is_json:
        data = request.get_json(silent=True)
        if data:
            session_id = data.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


def add_to_conversation_memory(session_id, user_message, ai_response):
    cleanup_old_sessions()
    session_cleanup_time[session_id] = datetime.now()
    conversation_memory[session_id].append(
        {
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat(),
        }
    )
    conversation_memory[session_id].append(
        {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat(),
        }
    )
    if len(conversation_memory[session_id]) > MAX_CONVERSATION_HISTORY:
        conversation_memory[session_id] = conversation_memory[session_id][
            -MAX_CONVERSATION_HISTORY:
        ]


def get_conversation_context(session_id):
    if session_id not in conversation_memory:
        return ""
    messages = conversation_memory[session_id]
    if not messages:
        return ""
    context_parts = []
    for msg in messages[-6:]:
        role = "Korisnik" if msg["role"] == "user" else "Asistent"
        content = (
            msg["content"][:300] + "..."
            if len(msg["content"]) > 300
            else msg["content"]
        )
        context_parts.append(f"{role}: {content}")
    context = "\n".join(context_parts)
    if len(context) > MAX_MEMORY_LENGTH:
        context = context[-MAX_MEMORY_LENGTH:]
        context = context[context.find("\n") + 1 :] if "\n" in context else context
    return context


def detect_input_language(text):
    try:
        from langdetect import detect

        lang = detect(text)
        if lang == "sh":
            return "bs"
        if lang in ["hr", "sr"]:
            return lang
        if lang in SUPPORTED_LANGUAGES:
            return lang
        return "bs"
    except Exception:
        return "bs"


def get_language_from_request():
    lang = request.args.get("lang", "").lower()
    if lang in SUPPORTED_LANGUAGES:
        return lang
    accept_lang = request.headers.get("Accept-Language", "")
    for lang_code in SUPPORTED_LANGUAGES:
        if lang_code in accept_lang.lower():
            return lang_code
    if request.is_json:
        data = request.get_json(silent=True)
        if data and "language" in data:
            requested_lang = data["language"].lower()
            if requested_lang in SUPPORTED_LANGUAGES:
                return requested_lang
    return "bs"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/api/health", methods=["GET", "OPTIONS"])
def health_check():
    if request.method == "OPTIONS":
        return "", 200
    return jsonify(
        {
            "status": "healthy",
            "service": "GraphRAG Backend",
            "timestamp": time.time(),
            "graph_rag_loaded": graph_rag is not None,
            "version": "v1.3",
            "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
            "features": ["conversation_memory", "multilingual_support"],
            "active_sessions": len(conversation_memory),
        }
    )


@app.route("/api/languages", methods=["GET"])
def get_supported_languages():
    return jsonify(
        {
            "supported_languages": {
                code: {"name": lang["name"], "code": code}
                for code, lang in SUPPORTED_LANGUAGES.items()
            }
        }
    )


@app.route("/api/clear_session", methods=["POST"])
def clear_session():
    try:
        session_id = get_or_create_session_id(request)
        if session_id in conversation_memory:
            del conversation_memory[session_id]
        if session_id in session_cleanup_time:
            del session_cleanup_time[session_id]
        return jsonify(
            {
                "success": True,
                "message": "Chat historija je obrisana",
                "session_id": session_id,
            }
        )
    except Exception:
        return jsonify(
            {"success": False, "error": "Greška prilikom čišćenja sesije."}
        ), 500


@app.route("/")
def index():
    return jsonify(
        {
            "message": "GraphRAG Backend API - MULTILINGUAL + CONVERSATION MEMORY",
            "status": "running",
            "features": [
                "Brza analiza dokumenata",
                "Proširena compliance provjera",
                "Optimizovane AI analize",
                "Fokusirani pravni komentari i savjeti",
                "Podrška za više jezika (BS, SR, HR, EN, DE)",
                "Conversation memory (pamti razgovor)",
            ],
            "supported_languages": list(SUPPORTED_LANGUAGES.keys()),
            "active_sessions": len(conversation_memory),
            "endpoints": [
                "/api/chat",
                "/process_pdf",
                "/api/analyze_document",
                "/api/languages",
                "/api/clear_session",
            ],
        }
    )


@app.route("/process_pdf", methods=["GET"])
def process_pdf_route():
    try:
        from src.data_processing import process_pdf

        pdf_path = os.getenv("PDF_PATH")
        processed_dir = os.getenv("PROCESSED_DIR")
        if not pdf_path or not os.path.exists(pdf_path):
            return jsonify(
                {
                    "success": False,
                    "error": "PDF fajl nije pronađen ili nije konfigurisan",
                }
            ), 404
        os.makedirs(processed_dir, exist_ok=True)
        text = process_pdf(pdf_path)
        chunks_dir = os.getenv("CHUNKS_DIR")
        os.makedirs(chunks_dir, exist_ok=True)
        chunk_size = int(os.getenv("CHUNK_SIZE", 500))
        chunk_overlap = int(os.getenv("CHUNK_OVERLAP", 100))
        chunks = create_chunks(text, chunk_size, chunk_overlap)
        vectorstore_path = os.getenv("VECTORSTORE_PATH")
        os.makedirs(vectorstore_path, exist_ok=True)
        embedding_model = os.getenv("EMBEDDING_MODEL")
        create_embeddings(chunks, embedding_model, vectorstore_path)
        global graph_rag
        graph_rag = None
        return jsonify(
            {
                "success": True,
                "message": "PDF je uspješno obrađen i GraphRAG baza je kreirana",
            }
        ), 200
    except Exception:
        return jsonify(
            {"success": False, "error": "Greška prilikom obrade PDF-a."}
        ), 500


@app.route("/api/chat", methods=["POST"])
def chat_api():
    global graph_rag
    try:
        session_id = get_or_create_session_id(request)
        data = request.json
        query = data.get("query", "")

        # Jezik iz zahtjeva ili detekcija iz teksta
        language = data.get("language", "").lower()
        if not language or language not in SUPPORTED_LANGUAGES:
            language = detect_input_language(query)

        if graph_rag is None:
            vectorstore_path = os.getenv("VECTORSTORE_PATH")
            embedding_model = os.getenv("EMBEDDING_MODEL")
            llm_model = os.getenv("LLM_MODEL")
            if not vectorstore_path or not os.path.exists(vectorstore_path):
                error_msg = (
                    "Vektorska baza nije pronađena. Pokrenite /process_pdf prvo."
                )
                return jsonify(
                    {"success": False, "error": error_msg, "session_id": session_id}
                ), 400
            vectorstore = load_vectorstore(vectorstore_path, embedding_model)
            graph_rag = GraphRAG(vectorstore, embedding_model, llm_model)

        if not query:
            return jsonify(
                {
                    "success": False,
                    "error": "Pitanje je obavezno",
                    "session_id": session_id,
                }
            ), 400

        normalized_query = query.lower().strip()
        context_chunks = retrieve_context(graph_rag, normalized_query)

        # Dodaj eksplicitnu instrukciju LLM-u na kom jeziku da odgovori
        language_prompts = {
            "en": "Please answer in English.",
            "de": "Bitte antworte auf Deutsch.",
            "hr": "Odgovori na hrvatskom jeziku.",
            "sr": "Одговори на српском језику.",
            "bs": "Odgovori na bosanskom jeziku.",
        }
        lang_instruction = language_prompts.get(
            language, "Odgovori na bosanskom jeziku."
        )
        full_query = f"{lang_instruction}\n\n{query}"

        response = generate_response(graph_rag, full_query, context_chunks)

        add_to_conversation_memory(session_id, query, response)

        return jsonify(
            {
                "success": True,
                "answer": response,
                "language": language,
                "language_name": SUPPORTED_LANGUAGES.get(
                    language, {"name": "Nepoznat"}
                )["name"],
                "session_id": session_id,
                "conversation_length": len(conversation_memory[session_id]),
                "sources": [
                    chunk.get("metadata", {}).get("article", "Nepoznat članak")
                    for chunk in context_chunks
                ],
            }
        )
    except Exception as e:
        logger.error(f"Greška prilikom generiranja odgovora: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/analyze_document", methods=["POST"])
def analyze_document():
    global graph_rag
    try:
        ui_language = get_language_from_request()

        if graph_rag is None:
            vectorstore_path = os.getenv("VECTORSTORE_PATH")
            embedding_model = os.getenv("EMBEDDING_MODEL")
            llm_model = os.getenv("LLM_MODEL")
            if not vectorstore_path or not os.path.exists(vectorstore_path):
                error_msg = (
                    "Vektorska baza nije pronađena. Pokrenite /process_pdf prvo."
                )
                return jsonify(
                    {
                        "success": False,
                        "error": error_msg,
                    }
                ), 400
            vectorstore = load_vectorstore(vectorstore_path, embedding_model)
            graph_rag = GraphRAG(vectorstore, embedding_model, llm_model)

        if "document" not in request.files:
            return jsonify(
                {"success": False, "error": "Nijedan dokument nije uploadovan"}
            ), 400

        file = request.files["document"]
        if file.filename == "":
            return jsonify(
                {"success": False, "error": "Nijedan fajl nije odabran"}
            ), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(f"analyze_{int(time.time())}_{file.filename}")
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            extracted_text = extract_text_from_document(file_path)
            structured_doc = structure_employment_document(graph_rag, extracted_text)
            structured_doc["filename"] = file.filename
            legal_requirements = get_legal_requirements_for_contract(graph_rag)
            legal_compliance_analysis = analyze_legal_compliance_main_fields(
                graph_rag, structured_doc, legal_requirements, extracted_text
            )
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify(
                {
                    "success": True,
                    "message": "Analiza dokumenta je uspješno završena",
                    "ui_language": ui_language,
                    "ui_language_name": SUPPORTED_LANGUAGES[ui_language]["name"],
                    "document": structured_doc,
                    "compliance_analysis": {
                        "legal_compliance_analysis": legal_compliance_analysis
                    },
                    "analysis_metadata": {
                        "text_length": len(extracted_text),
                        "parsing_method": structured_doc.get(
                            "parsing_method", "simple_fast"
                        ),
                        "analysis_version": "main_fields_v2",
                        "analysis_language": "bs",
                        "ui_language": ui_language,
                    },
                }
            )
        else:
            return jsonify(
                {
                    "success": False,
                    "error": "Nepodržan format fajla. Podržani: PDF, PNG, JPG, JPEG, GIF, WEBP",
                }
            ), 400
    except Exception:
        return jsonify(
            {"success": False, "error": "Greška prilikom analize dokumenta."}
        ), 500


def extract_text_from_document(file_path):
    try:
        if file_path.lower().endswith(".pdf"):
            doc = fitz.open(file_path)
            all_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    all_text += page_text + "\n"
                else:
                    pix = page.get_pixmap(matrix=fitz.Matrix(1.8, 1.8))
                    img_data = pix.tobytes("png")
                    temp_img_path = f"temp_page_{page_num}.png"
                    with open(temp_img_path, "wb") as f:
                        f.write(img_data)
                    image = PIL.Image.open(temp_img_path)
                    ocr_prompt = """Izvuci sav tekst iz ove slike dokumenta.
                    Fokusiraj se na brojeve, nazive, datume, uslove rada.
                    Vrati čist tekst bez komentara."""
                    try:
                        import google.generativeai as genai

                        model = genai.GenerativeModel(os.getenv("LLM_MODEL"))
                        response = model.generate_content(
                            [ocr_prompt, image],
                            generation_config={
                                "temperature": 0.1,
                                "max_output_tokens": 600,
                            },
                        )
                        all_text += response.text + "\n"
                    except Exception:
                        pass
                    try:
                        os.remove(temp_img_path)
                    except:
                        pass
            doc.close()
            return all_text
        elif file_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            image = PIL.Image.open(file_path)
            ocr_prompt = """Izvuci sav tekst iz ove slike dokumenta.
            Fokusiraj se na brojeve, nazive, datume, uslove rada.
            Vrati čist tekst bez komentara."""
            try:
                import google.generativeai as genai

                model = genai.GenerativeModel(os.getenv("LLM_MODEL"))
                response = model.generate_content(
                    [ocr_prompt, image],
                    generation_config={"temperature": 0.1, "max_output_tokens": 600},
                )
                return response.text
            except Exception:
                return ""
        else:
            return ""
    except Exception:
        return ""


def structure_employment_document(graph_rag, text):
    if not text or len(text.strip()) < 30:
        return {
            "document_type": "Nedovoljan tekst",
            "raw_text": text,
            "parsing_error": "OCR nije pročitao dovoljno teksta za analizu",
            "parsing_method": "error_fallback",
        }
    structure_prompt = f"""Analiziraj ovaj tekst dokumenta i izvuci ključne informacije o radu.

TEKST DOKUMENTA:
{text[:8000]}

Vrati SAMO JSON objekat sa sledećim poljima (ako informacija ne postoji, stavi null):
{{
    "document_type": "tip dokumenta (ugovor o radu/obračun plate/ponuda za posao/itd.)",
    "company_name": "naziv kompanije/poslodavca",
    "employee_name": "ime zaposlenog",
    "position": "pozicija/radno mesto", 
    "salary": "plata kao broj (bez valute i slova)",
    "currency": "valuta (KM/EUR/RSD/itd.)",
    "working_hours": "radno vreme po nedelji kao broj",
    "probation_period": "probni rad u mesecima kao broj",
    "vacation_days": "godišnji odmor u danima kao broj",
    "notice_period": "otkazni rok u danima kao broj",
    "contract_type": "tip ugovora (određeno vreme/neodređeno vreme/privremeni)",
    "start_date": "datum početka rada",
    "workplace": "mesto rada/adresa"
}}
VAŽNO: 
- Traži podatke kroz CIJELI tekst! Ako su na kraju, svejedno ih izvuci.
- Za brojeve izvuci samo cifre (npr. za "1.500 KM" stavi 1500)
- Ako nisi siguran o nekoj informaciji, stavi null
- Samo JSON, bez objašnjenja."""
    try:
        response = graph_rag.gemini_model.generate_content(
            structure_prompt,
            generation_config={
                "temperature": 0.1,
                "max_output_tokens": 1200,
            },
        )
        json_text = response.text.strip()
        if json_text.startswith("```json"):
            json_text = json_text[7:-3]
        elif json_text.startswith("```"):
            json_text = json_text[3:-3]
        m = re.search(r"\{[\s\S]+\}", json_text)
        if m:
            json_text = m.group(0)
        parsed_data = json.loads(json_text)
        parsed_data["parsing_method"] = "simple_fast_ai"
        return parsed_data
    except Exception:
        return {
            "error": "Greška pri parsiranju podataka.",
            "raw_text": text[:200] + "...",
            "parsing_method": "general_error_fallback",
        }


def get_legal_requirements_for_contract(graph_rag):
    topics = [
        "ugovor o radu sadržaj elementi",
        "obavezni sadržaj ugovora",
        "minimalna plata",
        "radno vrijeme ograničenja",
        "godišnji odmor zakon",
        "probni rad zakon",
        "otkazni rok zakon",
    ]
    all_requirements = []
    for topic in topics:
        try:
            context = graph_rag.retrieve(topic.lower(), n_results=1, use_graph=True)
            all_requirements.extend([item["text"] for item in context])
        except Exception:
            pass
    return "\n\n".join(all_requirements)


def analyze_legal_compliance_main_fields(
    graph_rag, structured_doc, legal_requirements, raw_text
):
    doc_text = json.dumps(structured_doc, indent=2, ensure_ascii=False)
    prompt = f"""
Ti si pravni ekspert za radne ugovore u Federaciji BiH. 
Analiziraj sljedeće ključne stavke iz dokumenta i za svaku napiši:
- status ("USKLAĐENO", "NIJE_USKLAĐENO", "NEJASNO")
- komentar (detaljno i jasno objasni zašto je nešto u skladu ili nije, sa primjerom iz zakona ili prakse)
- savjet (prijateljski i praktičan prijedlog kako poboljšati ili zašto je to važno)

Analiziraj polja:
- plata
- radno vrijeme
- godišnji odmor
- otkazni rok
- probni rad

DOKUMENT:
{doc_text}

SIROVI TEKST:
{raw_text[:8000]}

ZAKONSKE OBAVEZE:
{legal_requirements[:2000]}

Vrati ISKLJUČIVO JSON objekat sa ovim poljima (ništa drugo!):

{{
  "salary": {{
    "status": "...",
    "comment": "...",
    "advice": "..."
  }},
  "working_hours": {{
    "status": "...",
    "comment": "...",
    "advice": "..."
  }},
  "vacation_days": {{
    "status": "...",
    "comment": "...",
    "advice": "..."
  }},
  "notice_period": {{
    "status": "...",
    "comment": "...",
    "advice": "..."
  }},
  "probation_period": {{
    "status": "...",
    "comment": "...",
    "advice": "..."
  }}
}}
Samo JSON, bez objašnjenja, bez markdowna, bez dodatnog teksta.
"""
    try:
        response = graph_rag.gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 1800},
        )
        m = re.search(r"\{[\s\S]+\}", response.text)
        json_text = m.group(0) if m else response.text
        return json.loads(json_text)
    except Exception:
        fields = [
            "salary",
            "working_hours",
            "vacation_days",
            "notice_period",
            "probation_period",
        ]
        return {
            field: {
                "status": "NEJASNO",
                "comment": "Nije moguće generisati analizu.",
                "advice": "Provjerite i popunite ovo polje u dokumentu.",
            }
            for field in fields
        }


if __name__ == "__main__":
    required_env = ["EMBEDDING_MODEL", "LLM_MODEL", "GOOGLE_API_KEY"]
    missing_env = [var for var in required_env if not os.getenv(var)]
    if not missing_env:
        vectorstore_path = os.getenv("VECTORSTORE_PATH")
        if vectorstore_path and not os.path.exists(vectorstore_path):
            pass
        os.makedirs("static", exist_ok=True)
        app.run(debug=True, host="0.0.0.0", port=5000)
