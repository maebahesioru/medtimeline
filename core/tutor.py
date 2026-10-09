"""Grounded tutor — answers strictly from retrieved course excerpts, with citations.

Design:
  - The tutor sees ONLY the top retrieved excerpts.
  - It must cite each claim with [unit_id] markers.
  - If the excerpts don't cover the question it must refuse and say so
    (the API layer also returns the refusal flag for the UI).
  - Outside knowledge is never blended silently: a clearly separated
    "Not in your materials" note is allowed only when the person asked
    something the material misses, and it is flagged.
"""
from __future__ import annotations

from .ingest import Unit
from .retrieve import Retriever
from . import llm

TUTOR_SYSTEM = """You are MedExplain, a health-literacy companion. You help people UNDERSTAND their own medical documents (lab reports, discharge summaries, medication guides) in plain language.

Rules (strict):
1. Explain ONLY using the provided excerpts from the person's document. Never add outside medical facts, statistics, or advice.
2. Cite every explanation with the excerpt id in square brackets, e.g. [u1a2b3c4], and mention the value/section being explained.
3. Use plain language: define medical terms, explain what a value being high/low may mean ACCORDING TO THE DOCUMENT's own comments and reference ranges.
4. NEVER diagnose, NEVER prescribe, NEVER give treatment or dosage advice. You are a translator of documents, not a doctor.
5. If the excerpts do not contain the answer, reply exactly:
   "NOT_COVERED: I couldn't find this in the document."
   followed by one short sentence about what the document does say nearby.
6. Always end medical explanations with: "Discuss this with your clinician — this is not medical advice."
7. If the person describes symptoms or asks what they should do, do not interpret the symptoms; explain what the document says and direct them to their clinician.
"""



def answer(question: str, retriever: Retriever, k: int = 6, rerank: bool = True) -> dict:
    hits = retriever.search(question, k=k)
    if rerank:
        hits = retriever.rerank(question, hits, top=4)
    else:
        hits = hits[:4]

    if not hits:
        return {
            "answer": "NOT_COVERED: I couldn't find this in the document.",
            "citations": [],
            "refused": True,
        }

    context = "\n\n".join(
        f"[{u.id}] (source: {u.source_file}, {u.location})\n{u.text}" for u, _s in hits
    )
    user = (
        f"Student question: {question}\n\n"
        f"Available excerpts:\n{context}\n\n"
        "Answer with citations, or refuse with NOT_COVERED if not covered."
    )
    text = llm.chat(
        [{"role": "system", "content": TUTOR_SYSTEM}, {"role": "user", "content": user}],
        temperature=0.15,
        max_tokens=900,
    )

    refused = text.strip().startswith("NOT_COVERED")
    citations = []
    for u, score in hits:
        if u.id in text:
            citations.append(
                {
                    "unit_id": u.id,
                    "source_file": u.source_file,
                    "location": u.location,
                    "source_type": u.source_type,
                    "excerpt": u.text[:300],
                    "score": round(score, 3),
                }
            )
    return {"answer": text.strip(), "citations": citations, "refused": refused}
