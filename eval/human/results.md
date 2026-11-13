# Human evaluation

_2026-11-13 14:14 · 1 rater(s): aditi · 15 script ratings · 69 sentence labels · blind: raters saw the audience, not the search mode, the metrics or the checker's verdict_

## 1. Scripts (1-5, higher is better)

**Per audience** (hybrid search)

| audience | scripts | factuality | audience_fit | helpfulness |
|---|---|---|---|---|
| grad_students | 3 | 5.0 | 4.7 | 4.3 |
| policymakers | 3 | 4.3 | 4.7 | 4.7 |
| press | 3 | 4.3 | 4.0 | 5.0 |

**Per search mode** (policymakers)

| search mode | scripts | factuality | audience_fit | helpfulness |
|---|---|---|---|---|
| bm25 | 3 | 4.7 | 4.7 | 4.7 |
| dense | 3 | 5.0 | 3.7 | 4.0 |
| hybrid | 3 | 4.3 | 4.7 | 4.7 |

## 2. Sentences the checker doubted: what did the human say?

| checker verdict | n | true | hype | wrong | no_claim |
|---|---|---|---|---|---|
| supported | 13 | 54% | 31% | 0% | 15% |
| weak | 36 | 56% | 28% | 11% | 6% |
| unsupported | 6 | 50% | 17% | 33% | 0% |
| uncited | 8 | 100% | 0% | 0% | 0% |

_supported = 1 random supported sentence per script (a control: can 'supported' be trusted?)_

## 3. How many claims are really true? (checker vs human)

| audience | scripts | supported (strict) | grounded (lenient) | **true according to the human** |
|---|---|---|---|---|
| grad_students | 3 | 87% | 100% | **50%** |
| policymakers | 6 | 69% | 90% | **60%** |
| press | 3 | 39% | 86% | **61%** |

_true = supported claims x (share of controls rated true) + doubtful claims rated true; hype counts as NOT true_

## 4. Do the automatic metrics agree with the human? (Spearman, all scripts)

| human score | metric | n | rho | p |
|---|---|---|---|---|
| factuality | supported_share | 15 | +0.38 | 0.16 |
| factuality | grounded_share | 15 | -0.02 | 0.95 |
| audience_fit | reading_ease | 15 | +0.15 | 0.59 |
| helpfulness | bertscore | 15 | -0.03 | 0.91 |
| helpfulness | rougeL | 15 | +0.46 | 0.08 |

_rho: +1 = the metric ranks the scripts like the human, 0 = unrelated. With ~15 scripts only a large rho (about 0.5+) means much._

## 5. Do the raters agree with each other?

_Needs at least 2 raters (ask a friend: `python rate.py --rater <their name>`)._

## Rubric

```
  factuality: Is everything it says true to the paper?
      5 = everything correct · 3 = mostly correct, a small slip or exaggeration · 1 = major errors or invented facts  (2 and 4 are in between)
  audience_fit: Is it right for THIS audience (words, depth, tone)?
      5 = exactly right for them · 3 = OK, but parts are too technical or too simple · 1 = written for the wrong audience  (2 and 4 are in between)
  helpfulness: Would you use it as a 90-second talk?
      5 = use it as it is · 3 = usable after some editing · 1 = start over  (2 and 4 are in between)
```

## Comments

- **aditi** on `P1_policymakers_plain_english_dense_90s`: 1