# Automatic evaluation

_2026-11-13 14:26 · model `gemini-flash-lite-latest` · 15 scripts (P1, P2, P3; 90 seconds; 15 newly generated, the rest from eval/runs/) · BERTScore model `distilbert-base-uncased`_

## 1. Retrieval ablation (policymakers, plain English): does hybrid search help?

| search mode | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dense | 3 | 54% | 72% | 78% | 0 | 0 | 0.422 | 0.178 | 0.395 | 37.3 | 1.7 | 8% |
| bm25 | 3 | 63% | 86% | 91% | 0 | 0 | 0.399 | 0.159 | 0.385 | 40.8 | 1.7 | 13% |
| hybrid | 3 | 90% | 96% | 100% | 0 | 0 | 0.421 | 0.172 | 0.386 | 39.9 | 0.7 | 10% |

## 2. Audience adaptation (hybrid search): does the output change with the audience?

| audience | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| grad_students | 3 | 75% | 97% | 100% | 0.3 | 0 | 0.383 | 0.146 | 0.303 | 35.8 | 0 | 5% |
| policymakers | 3 | 90% | 96% | 100% | 0 | 0 | 0.421 | 0.172 | 0.386 | 39.9 | 0.7 | 10% |
| press | 3 | 47% | 85% | 100% | 0 | 0 | 0.432 | 0.176 | 0.406 | 38.4 | 1.3 | 16% |

## 3. Every script

| script | words | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P1_policymakers_plain_english_dense_90s` | 198 | 70% | 90% | 100% | 0 | 0 | 0.407 | 0.162 | 0.405 | 38.5 | 1 | 12% |
| `P1_policymakers_plain_english_bm25_90s` | 189 | 69% | 92% | 92% | 0 | 0 | 0.364 | 0.155 | 0.371 | 38.1 | 1 | 16% |
| `P1_policymakers_plain_english_hybrid_90s` | 223 | 100% | 100% | 100% | 0 | 0 | 0.396 | 0.161 | 0.408 | 28.8 | 1 | 1% |
| `P1_grad_students_technical_hybrid_90s` | 240 | 75% | 100% | 100% | 0 | 0 | 0.337 | 0.114 | 0.201 | 34.8 | 0 | 7% |
| `P1_press_press_release_hybrid_90s` | 206 | 67% | 83% | 100% | 0 | 0 | 0.432 | 0.168 | 0.387 | 36.2 | 1 | 8% |
| `P2_policymakers_plain_english_dense_90s` | 236 | 75% | 100% | 100% | 0 | 0 | 0.441 | 0.202 | 0.445 | 38.5 | 2 | 5% |
| `P2_policymakers_plain_english_bm25_90s` | 223 | 53% | 73% | 80% | 0 | 0 | 0.418 | 0.168 | 0.415 | 45.7 | 1 | 1% |
| `P2_policymakers_plain_english_hybrid_90s` | 206 | 92% | 100% | 100% | 0 | 0 | 0.451 | 0.165 | 0.408 | 44.9 | 1 | 8% |
| `P2_grad_students_technical_hybrid_90s` | 214 | 64% | 91% | 100% | 1 | 0 | 0.413 | 0.173 | 0.372 | 45.7 | 0 | 5% |
| `P2_press_press_release_hybrid_90s` | 180 | 42% | 83% | 100% | 0 | 0 | 0.405 | 0.162 | 0.426 | 41.7 | 2 | 20% |
| `P3_policymakers_plain_english_dense_90s` | 243 | 17% | 25% | 33% | 0 | 0 | 0.418 | 0.170 | 0.335 | 34.8 | 2 | 8% |
| `P3_policymakers_plain_english_bm25_90s` | 275 | 67% | 92% | 100% | 0 | 0 | 0.415 | 0.154 | 0.369 | 38.7 | 3 | 22% |
| `P3_policymakers_plain_english_hybrid_90s` | 177 | 78% | 89% | 100% | 0 | 0 | 0.416 | 0.189 | 0.342 | 45.9 | 0 | 21% |
| `P3_grad_students_technical_hybrid_90s` | 236 | 86% | 100% | 100% | 0 | 0 | 0.397 | 0.152 | 0.338 | 27 | 0 | 5% |
| `P3_press_press_release_hybrid_90s` | 183 | 33% | 89% | 100% | 0 | 0 | 0.459 | 0.197 | 0.406 | 37.3 | 1 | 19% |

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
