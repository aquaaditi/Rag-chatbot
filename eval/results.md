# Automatic evaluation

_2026-11-01 17:05 · model `gemini-flash-lite-latest` · 15 scripts (P1, P2, P3; 90 seconds; 0 newly generated, the rest from eval/runs/) · BERTScore model `distilbert-base-uncased`_

## 1. Retrieval ablation (policymakers, plain English): does hybrid search help?

| search mode | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dense | 3 | 65% | 88% | 97% | 0 | 0 | 0.407 | 0.167 | 0.392 | 37.0 | 1.7 | 12% |
| bm25 | 3 | 64% | 91% | 91% | 0 | 0 | 0.402 | 0.160 | 0.376 | 39.2 | 1 | 12% |
| hybrid | 3 | 73% | 88% | 91% | 0 | 0 | 0.414 | 0.166 | 0.375 | 42.3 | 1 | 14% |

## 2. Audience adaptation (hybrid search): does the output change with the audience?

| audience | n | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| grad_students | 3 | 87% | 100% | 100% | 0 | 0 | 0.357 | 0.139 | 0.309 | 31.6 | 0.7 | 7% |
| policymakers | 3 | 73% | 88% | 91% | 0 | 0 | 0.414 | 0.166 | 0.375 | 42.3 | 1 | 14% |
| press | 3 | 39% | 86% | 93% | 0 | 0 | 0.440 | 0.175 | 0.423 | 40.6 | 1.3 | 18% |

## 3. Every script

| script | words | supported | grounded | cited | number errors | invented IDs | ROUGE-1 | ROUGE-L | BERTScore | readability | warnings | length error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `P1_policymakers_plain_english_dense_90s` | 201 | 60% | 90% | 90% | 0 | 0 | 0.394 | 0.156 | 0.413 | 29 | 2 | 11% |
| `P1_policymakers_plain_english_bm25_90s` | 194 | 75% | 92% | 92% | 0 | 0 | 0.377 | 0.152 | 0.372 | 36.9 | 1 | 14% |
| `P1_policymakers_plain_english_hybrid_90s` | 196 | 73% | 91% | 91% | 0 | 0 | 0.423 | 0.172 | 0.397 | 39 | 1 | 13% |
| `P1_grad_students_technical_hybrid_90s` | 233 | 90% | 100% | 100% | 0 | 0 | 0.298 | 0.121 | 0.214 | 28.7 | 0 | 4% |
| `P1_press_press_release_hybrid_90s` | 196 | 64% | 100% | 100% | 0 | 0 | 0.430 | 0.193 | 0.441 | 32.5 | 1 | 13% |
| `P2_policymakers_plain_english_dense_90s` | 214 | 80% | 100% | 100% | 0 | 0 | 0.441 | 0.178 | 0.412 | 42 | 1 | 5% |
| `P2_policymakers_plain_english_bm25_90s` | 181 | 64% | 82% | 82% | 0 | 0 | 0.417 | 0.150 | 0.402 | 40.6 | 1 | 20% |
| `P2_policymakers_plain_english_hybrid_90s` | 195 | 83% | 92% | 92% | 0 | 0 | 0.406 | 0.149 | 0.380 | 44.1 | 1 | 13% |
| `P2_grad_students_technical_hybrid_90s` | 202 | 80% | 100% | 100% | 0 | 0 | 0.393 | 0.144 | 0.377 | 34.7 | 1 | 10% |
| `P2_press_press_release_hybrid_90s` | 177 | 44% | 89% | 89% | 0 | 0 | 0.436 | 0.153 | 0.435 | 40.6 | 2 | 21% |
| `P3_policymakers_plain_english_dense_90s` | 182 | 55% | 73% | 100% | 0 | 0 | 0.385 | 0.166 | 0.352 | 39.9 | 2 | 19% |
| `P3_policymakers_plain_english_bm25_90s` | 218 | 55% | 100% | 100% | 0 | 0 | 0.412 | 0.179 | 0.356 | 40 | 1 | 3% |
| `P3_policymakers_plain_english_hybrid_90s` | 192 | 64% | 82% | 91% | 0 | 0 | 0.412 | 0.177 | 0.349 | 43.7 | 1 | 15% |
| `P3_grad_students_technical_hybrid_90s` | 240 | 91% | 100% | 100% | 0 | 0 | 0.381 | 0.151 | 0.337 | 31.4 | 1 | 7% |
| `P3_press_press_release_hybrid_90s` | 183 | 10% | 70% | 90% | 0 | 0 | 0.453 | 0.181 | 0.394 | 48.6 | 1 | 19% |

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
