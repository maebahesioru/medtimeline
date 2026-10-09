# Devpost submission text — MedTimeline (DSH Hacks V2)

## Inspiration

When you care for an aging parent or manage a chronic condition, medical documents arrive
scattered: a lab report from March, a follow-up in September, a discharge summary from a
hospital visit. No one shows you the *story* — that HbA1c is trending up, that ferritin is
falling, that a value flagged HIGH in September was borderline in March.

Caregivers become accidental data managers, with no tools built for them. We built the tool
we wished existed: one that assembles scattered reports into a single chronological health
story, finds the trends, and prepares the questions you should ask next.

## What it does

**MedTimeline** turns multiple dated medical documents into one organized health story:

- **Chronological timeline** — every report and measurement placed on a dated timeline
  across all uploaded documents, with exact source links.
- **Trend detection** — repeated measurements compared across dates, e.g.
  "Ferritin: 22 ng/mL (2026-03-10) → 9 ng/mL (2026-09-15) — falling" — both values and
  both dates shown, nothing inferred beyond the documents.
- **Flagged values** — LOW/HIGH results surfaced with their reference ranges, straight
  from the documents.
- **Appointment prep** — auto-generated questions for the next visit, built from the
  trends and flags: "The HbA1c has risen from 5.6% (2026-03) to 5.9% (2026-09) — what
  could explain this, and should we investigate?"
- **🔊 Spoken questions** — one button reads the appointment questions aloud.
- **Grounded Q&A** — ask anything about the documents: answers cite the exact line and
  compare values across reports; questions the documents don't cover are declined.
- **Safety by design** — never diagnoses, never prescribes, does not interpret symptoms;
  every answer points back to the clinician.

## How we built it

- **Python + FastAPI** backend; single-page web UI (no build step).
- **Timeline extraction** (`core/timeline.py`): dated report parsing + measurement-row
  extraction over source-linked units; trends computed from repeated measurements.
- **Retrieval**: scikit-learn TF-IDF (local, any language) + optional LLM re-ranking.
- **Grounding contract**: retrieval-scoped prompts + mandatory citations + explicit
  refusal token.
- **Audio**: edge-tts neural voices with content-hash caching.
- **LLM**: any OpenAI-compatible endpoint.

## Challenges we ran into

- Extracting measurements reliably from real-world lab report formats (tables with
  reference ranges and flags) while keeping every value linked to its source line.
- Keeping the tool honest: trend detection shows only what the documents contain, and
  questions are phrased *for the clinician* rather than answered by the AI.
- Making an LLM refuse off-document questions required a strict prompt contract plus
  UI-level flags.

## What we learned

For caregivers, the most valuable AI output isn't an answer — it's an **organization**:
seeing the whole story at once, and arriving at the next appointment with the right
questions. Grounding and refusal are what make such a tool safe to trust.

## What's next

- OCR for scanned reports; support for discharge summaries and medication lists.
- Shared family timelines with consent-based access.
- Trend alerts between visits.

## Built with

python, fastapi, scikit-learn, edge-tts, llm, rag, caregiving, health-literacy
