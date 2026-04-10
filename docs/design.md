# Design Notes

## Goal

Build a production-minded voice support assistant for low-resource customer support scenarios in West Africa.

## Main system decisions

### 1. Local ASR
Used `faster-whisper` for offline transcription to avoid API cost and keep the demo reproducible.

### 2. Hybrid retrieval
Combined:
- lexical retrieval
- TF-IDF vector retrieval
- hybrid reranking

This was chosen as a practical middle ground between a brittle keyword system and a heavier dense retrieval stack.

### 3. Grounded answer generation
Answers are composed from retrieved evidence instead of relying only on canned source-based templates.

### 4. Guardrails
The assistant escalates:
- risky account-sensitive issues
- wrong-recipient cases
- locked-account cases
- document-review requests
- unclear queries
- low-confidence responses

## Main tradeoffs

- kept the support domain narrow to make grounding stronger
- chose easier-to-debug components over a heavier LLM orchestration stack
- prioritized evaluation and safe fallback over broader coverage

## Next improvements

- dense embeddings
- multilingual routing
- broader eval set
- stronger calibration
- real human handoff integration