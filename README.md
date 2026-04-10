# West Africa Voice Support Agent

A production-minded multilingual voice support agent for low-resource customer support scenarios in West Africa.

This project demonstrates a voice-first support workflow that accepts audio or text, retrieves grounded answers from a support knowledge base, generates concise support responses, and escalates risky or unsupported cases to human support.

## Why this project exists

Customer support systems in many African markets operate under constraints that are often underrepresented in mainstream AI demos:

- multilingual and code-switched inputs
- low-resource language settings
- noisy audio environments
- low-bandwidth or unstable connectivity
- informal phrasing and spelling variation
- trust-sensitive financial and account-related issues

This repo is a focused demonstration of how to build a safer support assistant for that environment.

## Current evaluation snapshot

- Top-1 retrieval accuracy: 83.3%
- Evidence recall@3: 100.0%
- Escalation accuracy: 75.0%
- Average gold coverage: 84.7%
- Average confidence: 0.771
- Unsupported answers: 0

## Demo assets

### Screenshots
- `samples/screenshots/docs-transcribe.png`
- `samples/screenshots/docs-voice-ask-wrong-recipient.png`
- `samples/screenshots/docs-voice-ask-locked-account.png`
- `samples/screenshots/eval-report.png`

### Demo recording
- `samples/demo/voice-support-demo.gif`
- or `samples/demo/voice-support-demo.mp4`

## What it does

The system supports a narrow but realistic customer-support flow:

1. Accepts voice or text input
2. Transcribes audio locally
3. Normalizes the user message
4. Retrieves relevant support documents from a knowledge base
5. Generates an answer grounded in retrieved evidence
6. Estimates confidence and checks for risky cases
7. Either:
   - returns a grounded response with supporting evidence, or
   - recommends escalation to a human support agent

## Example supported intents

- send money failed
- cash-out issue
- account locked
- wrong recipient
- KYC / identity verification help

## Core features

- **Voice + text support**
- **Local offline transcription with `faster-whisper`**
- **Hybrid retrieval**
  - domain-aware lexical retrieval
  - TF-IDF vector retrieval
  - hybrid reranking
- **Grounded answer generation**
- **Evidence-backed responses**
- **Confidence-aware fallback**
- **Escalation for risky or unsupported cases**
- **Offline evaluation suite**
- **Modular Python backend**

## Voice transcription

This project supports local offline speech transcription using `faster-whisper`.

### Endpoints
- `POST /transcribe` — upload audio and receive a transcript
- `POST /voice-ask` — upload audio and run the full support pipeline

### Backend
- ASR backend: `faster-whisper`
- Model size: `small`
- Device: `cpu`
- Compute type: `int8`

### Notes
The first transcription request may take longer because the model is loaded on first use.

## System architecture

```text
User
  ├─> Text input
  └─> Voice input
         └─> Local ASR (faster-whisper)

Normalized query
   └─> Hybrid retrieval
         ├─> lexical retrieval
         ├─> TF-IDF vector retrieval
         └─> reranking
               └─> grounded answer generation
                     └─> guardrails
                           ├─> confidence check
                           ├─> risky-intent detection
                           └─> escalation decision
                                 └─> final response