1. PROBLEM (Introduction, p.1)
   - Task: sentence classification = give each sentence a label
     (positive/negative review, type of question, subjective/objective...).
   - Deep learning for language often relied on large, heavily engineered models.
   - Open question: can a very SIMPLE model do well if it starts from good
     pre-trained word vectors?

2. MAIN IDEA (Abstract + Figure 1, p.1–2)
   - Each word → a word vector from word2vec (pre-trained on Google News).
   - Sentence = a stack of word vectors (one row per word).
   - ONE convolution layer: small filters slide over windows of a few words
     (3, 4, 5 words) and detect useful phrase patterns.
   - Max-over-time pooling: keep only the strongest signal from each filter
     → works for any sentence length.
   - Then a final layer (with dropout) picks the label.
   - Variants: static (word vectors frozen) vs non-static (fine-tuned for the
     task); multichannel = both at once.

3. RESULT (Abstract, last sentence + Table 2)
   - Beats the previous best on 4 of 7 benchmarks, including sentiment
     analysis and question classification.
   - Even the static version, with little tuning, does very well.
   - Fine-tuning the vectors gives extra gains.
   - [YOU ADD: one accuracy number from Table 2 + its page number]

4. WHY IT MATTERS (Conclusion, Section 5)
   - A simple one-layer CNN works remarkably well with little tuning.
   - Shows that pre-trained word vectors are a key ingredient in deep
     learning for NLP.

5. HOOK IDEA (my own)
   - Every day millions of reviews and messages need sorting: is this
     complaint angry? Is this review positive? Doing it well usually sounds
     like it needs a big, complicated model. This paper shows it doesn't.