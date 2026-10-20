Paper 2: "Bag of Tricks for Efficient Text Classification"
Joulin, Grave, Bojanowski, Mikolov (Facebook AI Research), 2016 (fastText)

1. PROBLEM (Introduction, p.1)
   - Task: text classification (sentiment, tagging, search, ranking...).
   - Neural network models (e.g. Kim 2014 = our paper 1!) work well but are
     SLOW to train and test -> hard to use on very large datasets.
   - Simple linear classifiers are strong baselines and scale well.
   - Question: can a simple linear model be as accurate as deep models
     but much faster?

2. MAIN IDEA (Section 2 + Figure 1, p.1-2)
   - Look up a vector for each word (and each n-gram).
   - AVERAGE them into one "text vector" (the hidden layer).
   - Feed it to a linear classifier with softmax -> label.
   - Similar to word2vec's CBOW, but predicts the label instead of the
     middle word.
   - Loss (p.2): -(1/N) sum_n  y_n log(f(B A x_n))
     (A, B = weight matrices, f = softmax, x_n = bag of features)
   - Trick 1 - Hierarchical softmax (Sec 2.1, p.2): classes arranged in a
     tree -> cost drops from O(kh) to O(h log2 k). Matters when there are
     MANY classes.
   - Trick 2 - Bag of n-grams (Sec 2.2, p.2): add bigrams to capture some
     word order cheaply; hashing trick keeps memory small.
   - Trains on CPU (20 threads), not GPU.

3. RESULT (Section 3, p.2-4, Tables 1, 2, 5)
   - Sentiment (Table 1, p.3): with bigrams, accuracy on par with deep
     models, e.g. AG News 92.5% vs char-CNN 87.2%; slightly below VDCNN on
     some datasets.
   - Bigrams add 1-4% accuracy (p.3).
   - Speed (Table 2, p.3): one epoch on AG takes 1 second vs 24 minutes to
     several hours for deep CNNs; up to at least 15,000x faster (p.4).
   - Tag prediction (Table 5, p.4): ~91M examples, 312K tags.
     fastText (h=200, bigram) gets 46.1% prec@1 vs Tagspace 35.6%;
     trains in ~14 minutes vs 5.5 hours; test is ~600x faster.
   - Abstract: trains on >1 billion words in <10 minutes on a CPU.

4. WHY IT MATTERS (Discussion, Section 4, p.4-5)
   - A simple, shallow model can match deep learning on many text tasks
     while being orders of magnitude faster.
   - Questions whether simple tasks like sentiment are good tests of
     deep models.
   - Code released (fastText library) -> widely used in practice.

5. HOOK IDEA (fill in your own)
   -

KEY EQUATIONS (for testing math preservation later)
   - Loss: -(1/N) sum_{n=1}^{N} y_n log(f(B A x_n))          (p.2)
   - Node probability in tree: P(n_{l+1}) = prod_{i=1}^{l} P(n_i)  (p.2)
