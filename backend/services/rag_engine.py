
import re
import numpy as np
import faiss

from sentence_transformers import SentenceTransformer


# --------------------------------
# MODEL CONFIGURATION
# --------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = None


def get_embedding_model():
    global model

    if model is None:
        print("Loading RAG embedding model...")
        model = SentenceTransformer(MODEL_NAME)
        print("RAG embedding model loaded successfully.")

    return model


# --------------------------------
# TEXT CLEANING
# --------------------------------

def clean_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", str(text))

    return text.strip()


# --------------------------------
# TEXT CHUNKING
# --------------------------------

def chunk_text(text, chunk_size=100, overlap=20):

    text = clean_text(text)

    if not text:
        return []

    if chunk_size <= 0 or overlap < 0:
        raise ValueError("Invalid chunk configuration.")

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    words = text.split()

    chunks = []

    step = chunk_size - overlap

    for start in range(0, len(words), step):

        chunk = " ".join(
            words[start:start + chunk_size]
        )

        if chunk:
            chunks.append(chunk)

        if start + chunk_size >= len(words):
            break

    return chunks


# --------------------------------
# EMBEDDING GENERATION
# --------------------------------

def create_embeddings(chunks):

    if not chunks:
        return np.empty(
            (0, 384),
            dtype="float32"
        )

    embedding_model = get_embedding_model()

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    return np.asarray(
        embeddings,
        dtype="float32"
    )


# --------------------------------
# FAISS INDEX
# --------------------------------

def build_faiss_index(chunks):

    if not chunks:
        return None, []

    embeddings = create_embeddings(chunks)

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return index, chunks


# --------------------------------
# RETRIEVAL
# --------------------------------

def retrieve_relevant_chunks(
    query,
    index,
    chunks,
    top_k=3
):

    if not query or index is None or not chunks:
        return []

    embedding_model = get_embedding_model()

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    k = min(top_k, len(chunks))

    scores, indices = index.search(
        query_embedding,
        k
    )

    results = []

    for score, idx in zip(scores[0], indices[0]):

        if idx < 0:
            continue

        results.append({
            "text": chunks[int(idx)],
            "similarity": round(
                float(score) * 100,
                2
            )
        })

    return results


# --------------------------------
# RESUME RELEVANCE ANALYSIS
# --------------------------------

def analyze_resume_relevance(
    resume_text,
    job_description,
    top_k=3
):

    resume_chunks = chunk_text(resume_text)

    if not resume_chunks:

        return {
            "chunks_count": 0,
            "retrieved_evidence": [],
            "context": ""
        }

    index, stored_chunks = build_faiss_index(
        resume_chunks
    )

    job_chunks = chunk_text(
        job_description,
        chunk_size=80,
        overlap=10
    )

    if not job_chunks:
        job_chunks = [clean_text(job_description)]

    retrieved_evidence = []

    for requirement in job_chunks:

        matches = retrieve_relevant_chunks(
            requirement,
            index,
            stored_chunks,
            top_k=top_k
        )

        for match in matches:

            retrieved_evidence.append({
                "query": requirement,
                "resume_evidence": match["text"],
                "similarity": match["similarity"]
            })

    # Remove duplicate evidence

    unique_evidence = []
    seen = set()

    for item in retrieved_evidence:

        key = item["resume_evidence"]

        if key not in seen:

            seen.add(key)

            unique_evidence.append(item)

    # Limit context size to prevent unnecessarily
    # large prompts

    selected_evidence = unique_evidence[:12]

    context = "\n".join(
        item["resume_evidence"]
        for item in selected_evidence
    )

    print(
        f"RAG completed: {len(resume_chunks)} resume chunks, "
        f"{len(selected_evidence)} evidence chunks retrieved."
    )

    return {
        "chunks_count": len(resume_chunks),
        "retrieved_evidence": selected_evidence,
        "context": context
    }