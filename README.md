# MedTimeline — your family's health story, organized

> DSH Hacks V2 — Theme: AI × Healthcare

**Caregivers juggle reports from different dates and providers. MedTimeline turns them
into one chronological health story — with trends, flagged values, and questions for the
next appointment — and answers every question with citations to the exact line.**

## The problem

When you care for an aging parent or manage a chronic condition, medical documents arrive
scattered: a lab report from March, a follow-up in September, a discharge summary from a
hospital visit. No one shows you the *story* — that HbA1c is trending up, that ferritin is
falling, that the March comment recommended a re-check that the September report quietly
contradicts.

Caregivers become accidental data managers — with no tools built for them.

## What MedTimeline does

| Feature | Detail |
|---|---|
| **Multi-document ingestion** | Upload reports from any dates (PDF / TXT / MD); every passage keeps its exact origin |
| **Chronological timeline** | Reports and measurements assembled into one dated story across all documents |
| **Trend detection** | Repeated measurements compared across dates (rising / falling / stable) with both values and dates shown |
| **Flagged values** | LOW/HIGH results surfaced with their reference ranges, straight from the document |
| **Appointment prep** | Auto-generated questions for the next visit, built from the trends and flags ("HbA1c rose from 5.6 (2026-03) to 5.9 (2026-09) — what could explain this?") |
| **🔊 Spoken questions** | One button reads the appointment questions aloud |
| **Grounded Q&A** | Ask anything about the documents: answers cite the exact line, and off-document questions are declined |
| **Safety by design** | Never diagnoses, never prescribes; every answer points back to the clinician |

## Safety design

- **Organizer, not doctor.** MedTimeline assembles and explains what the documents say —
  it does not interpret symptoms or recommend treatment.
- **No outside knowledge.** Answers come only from retrieved excerpts; off-document
  questions return an explicit refusal.
- **Clinician handoff.** Appointment questions are phrased as questions *for your doctor*.
- **Synthetic demo data.** The two sample reports (`data/sample_course/report_2026-03.md`,
  `report_2026-09.md`) are entirely fictional — no real patient data ships with this project.

## How it works

```
 upload ×N ──► ingest (pdf/txt/md) ──► source-linked passages
                                          │
                      /api/timeline ──► dated events ──► trends + flags + questions
                                          │
 question ──► TF-IDF retrieval ──► grounded answer + citations ──► 🔊 TTS
```

- Timeline extraction: date regex + table-row parsing over source-linked units
  (`core/timeline.py`); trends from repeated measurements across dates.
- Retrieval: scikit-learn TF-IDF (local, any language).
- Grounding: retrieval-scoped prompts, mandatory citations, explicit `NOT_COVERED` refusal.
- Audio: edge-tts neural voices, content-hash cached.
- LLM: any OpenAI-compatible endpoint.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp config.example.env .env      # set LLM_BASE_URL / LLM_API_KEY / LLM_MODEL
uvicorn server:app --port 7864  # open http://127.0.0.1:7864
```

Upload both sample reports, click **Build timeline**, and watch the story assemble.

## Impact

- **Caregivers**: the person managing a parent's care finally sees the whole story.
- **Continuity**: trends across providers and dates — the thing no single report shows.
- **Preparedness**: arrive at appointments with specific, document-grounded questions.
- **Safety**: grounded answers + honest refusals + clinician handoff.

## Honest limitations

- Not a medical device; not for emergencies.
- Timeline extraction expects dated, tabular reports (typical lab formats).
- The demo uses synthetic reports; real use must consider privacy (documents stay local here).
