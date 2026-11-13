# Automatic evaluation

_2026-11-13 14:37 · model `gemini-flash-lite-latest` · 15 scripts (P1, P2, P3; 90 seconds; 15 newly generated, the rest from eval/runs/) · BERTScore model `distilbert-base-uncased`_

## 1. Retrieval ablation (policymakers, plain English): does hybrid search help?

| search mode | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dense | 3 | 83% | 97% | 100% | 0 | 0 | 0.438 | 0.200 | 0.419 | 35.0 | 1 | 4% |
| bm25 | 3 | 62% | 89% | 92% | 0 | 0 | 0.424 | 0.152 | 0.394 | 37.2 | 1 | 5% |
| hybrid | 3 | 78% | 91% | 94% | 0 | 0 | 0.431 | 0.157 | 0.397 | 35.8 | 0.7 | 3% |

## 2. Audience adaptation (hybrid search): does the output change with the audience?

| audience | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| grad_students | 3 | 86% | 94% | 97% | 0.3 | 0 | 0.365 | 0.146 | 0.299 | 32.3 | 0 | 13% |
| policymakers | 3 | 78% | 91% | 94% | 0 | 0 | 0.431 | 0.157 | 0.397 | 35.8 | 0.7 | 3% |
| press | 3 | 30% | 70% | 90% | 0 | 0 | 0.426 | 0.171 | 0.397 | 46.5 | 0.7 | 8% |

## 3. Every script

| script | words | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P1_policymakers_plain_english_dense_90s` | 234 | 91% | 91% | 100% | 0 | 0 | 0.362 | 0.143 | 0.379 | 27.3 | 1 | 4% |
| `P1_policymakers_plain_english_bm25_90s` | 216 | 54% | 85% | 92% | 0 | 0 | 0.424 | 0.154 | 0.395 | 43.5 | 0 | 4% |
| `P1_policymakers_plain_english_hybrid_90s` | 221 | 70% | 90% | 100% | 0 | 0 | 0.417 | 0.157 | 0.402 | 24 | 2 | 2% |
| `P1_grad_students_technical_hybrid_90s` | 239 | 85% | 92% | 92% | 0 | 0 | 0.289 | 0.128 | 0.173 | 33 | 0 | 6% |
| `P1_press_press_release_hybrid_90s` | 193 | 8% | 62% | 100% | 0 | 0 | 0.424 | 0.184 | 0.400 | 50.2 | 0 | 14% |
| `P2_policymakers_plain_english_dense_90s` | 237 | 77% | 100% | 100% | 0 | 0 | 0.460 | 0.197 | 0.444 | 42.3 | 0 | 5% |
| `P2_policymakers_plain_english_bm25_90s` | 232 | 58% | 83% | 83% | 0 | 0 | 0.419 | 0.122 | 0.410 | 35.2 | 1 | 3% |
| `P2_policymakers_plain_english_hybrid_90s` | 215 | 73% | 82% | 82% | 0 | 0 | 0.442 | 0.138 | 0.418 | 41 | 0 | 4% |
| `P2_grad_students_technical_hybrid_90s` | 231 | 82% | 91% | 100% | 1 | 0 | 0.416 | 0.149 | 0.379 | 38.7 | 0 | 3% |
| `P2_press_press_release_hybrid_90s` | 206 | 60% | 80% | 87% | 0 | 0 | 0.389 | 0.141 | 0.400 | 43.8 | 1 | 8% |
| `P3_policymakers_plain_english_dense_90s` | 216 | 80% | 100% | 100% | 0 | 0 | 0.490 | 0.260 | 0.435 | 35.3 | 2 | 4% |
| `P3_policymakers_plain_english_bm25_90s` | 241 | 75% | 100% | 100% | 0 | 0 | 0.429 | 0.180 | 0.378 | 33 | 2 | 7% |
| `P3_policymakers_plain_english_hybrid_90s` | 231 | 91% | 100% | 100% | 0 | 0 | 0.435 | 0.175 | 0.370 | 42.3 | 0 | 3% |
| `P3_grad_students_technical_hybrid_90s` | 292 | 92% | 100% | 100% | 0 | 0 | 0.390 | 0.162 | 0.346 | 25.2 | 0 | 30% |
| `P3_press_press_release_hybrid_90s` | 226 | 23% | 69% | 85% | 0 | 0 | 0.464 | 0.187 | 0.391 | 45.4 | 1 | 0% |

## What the columns mean

| Column | Meaning | Better |
|---|---|---|
| supported | share of claims whose cited chunk really says it (embedding match >= 0.80): our **factuality proxy** | higher |
| grounded | lenient version: supported OR weak (match >= 0.70). True plain-English paraphrases often score 0.70-0.80, so the truth is usually between the two | higher |
| cited | **citation coverage**: share of claims with a valid [chunk ID] | higher |
| number errors | claims with a number that is not in the cited chunk (per script) | 0 |
| invented IDs | cited chunk IDs that were never given to the model (per script) | 0 |
| ROUGE-1 / ROUGE-L | shared words / longest shared word sequence with the **human reference** | higher* |
| BERTScore | similarity in meaning to the human reference (rescaled: ~0 = unrelated) | higher* |
| readability | Flesch reading ease (60+ plain English, <30 academic) | depends on the audience |
| warnings | safety & accessibility warnings (long sentences, undefined acronyms, readability floor) | lower |
| length error | distance from the target length (90s = 225 words) | lower |

\* The references were written by hand for a general audience, so a technical script for
graduate students SHOULD score lower against them - that is adaptation, not a mistake.
