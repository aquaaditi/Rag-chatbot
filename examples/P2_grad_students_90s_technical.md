# Script: how the model works and why it is fast

_Generated 2026-10-25 18:01_

## Input
- **Topic:** how the model works and why it is fast
- **Paper:** P2
- **Audience:** grad_students  |  **Length:** 90s (target ~225 words)  |  **Style:** technical

## Output

Let us examine fastText, a simple and efficient linear baseline for text classification that matches deep learning accuracy while remaining orders of magnitude faster [P2_p1_c02][P2_p1_c03]. 

The model architecture resembles the continuous bag-of-words model, where a sentence's features are embedded and averaged to create a hidden variable [P2_p2_c01]. Specifically, for a document with $N$ n-gram features, the model minimizes the negative log-likelihood over the classes using the objective $-\frac{1}{N}\sum_{n=1}^{N} y_n \log(f(BAx_n))$, where $x_n$ is the normalized bag of features, $y_n$ is the label, $f$ is the softmax function, and $A$ and $B$ are weight matrices [P2_p2_c01]. 

To capture local word order without high computational costs, fastText uses a bag of n-grams as additional features, managed efficiently via the hashing trick with 10M bins for bigrams and 100M otherwise [P2_p2_c03]. Training is performed asynchronously across multiple CPUs using stochastic gradient descent with a linearly decaying learning rate [P2_p2_c01].

Why is it so fast? Unlike Tagspace, which must compute scores for all classes and struggles when the output space is large, fastText uses fast inference to achieve massive speed-ups—for instance, a 600 times speedup during the test phase on YFCC100M with 312K classes [P2_p2_c03][P2_p4_c03]. Overall, fastText trains on over one billion words in under ten minutes using a standard multicore CPU, and classifies half a million sentences in under a minute [P2_p1_c02].

## Checks
- Words: 219 (target ~225)
- Chunks cited: 5 of 6 provided
- Unknown (invented) citations: none

## Sources given to the LLM

- `P2_p1_c02` — page 1, Abstract (✅ cited)
- `P2_p4_c03` — page 4, 3.2 Tag prediction (✅ cited)
- `P2_p2_c01` — page 2, 2 Model architecture (✅ cited)
- `P2_p2_c03` — page 2, 2.2 N-gram features (✅ cited)
- `P2_p1_c03` — page 1, 1 Introduction (✅ cited)
- `P2_p2_c04` — page 2, 3 Experiments (not cited)

## Full prompt

```text
TASK: Write a spoken script about: how the model works and why it is fast

AUDIENCE: graduate students in machine learning: they know the basics and want the method, the key equations and the experimental evidence
STYLE: technical: precise terms, mention the method and equations where they help
LENGTH: about 225 words (90s when read aloud at 150 words per minute).

SOURCES:
[P2_p1_c02] (paper P2, page 1, section "Abstract")
This paper explores a simple and efficient baseline for text classification. Our experiments show that our fast text classifier fastText is often on par with deep learning classifiers in terms of accuracy, and many orders of magnitude faster for training and evaluation. We can train fastText on more than one billion words in less than ten minutes using a standard multicore CPU, and classify half a million sentences among 312K classes in less than a minute.

[P2_p4_c03] (paper P2, page 4, section "3.2 Tag prediction")
Freq. baseline 2.2 - - Tagspace, h = 50 30.1 3h8 6h Tagspace, h = 200 35.6 5h32 15h fastText, h = 50 31.2 6m40 48s fastText, h = 50, bigram 36.7 7m47 50s fastText, h = 200 41.1 10m34 1m29 fastText, h = 200, bigram 46.1 13m38 1m37 Table 5: Prec@1 on the test set for tag prediction on YFCC100M. We also report the training time and test time. Test time is reported for a single thread, while training uses 20 threads for both models. and 200. Both models achieve a similar performance with a small hidden layer, but adding bigrams gives us a significant boost in accuracy. At test time, Tagspace needs to compute the scores for all the classes which makes it relatively slow, while our fast inference gives a significant speed-up when the number of classes is large (more than 300K here). Overall, we are more than an order of magnitude faster to obtain model with a better quality. The speedup of the test phase is even more significant (a 600× speedup). Table 4 shows some qualitative examples.

[P2_p2_c01] (paper P2, page 2, section "2 Model architecture")
x1 x2 . . . xN−1 xN hidden output Figure 1: Model architecture of fastText for a sentence with N ngram features x1, . . . , xN. The features are embedded and averaged to form the hidden variable. tion is an hidden variable which can be potentially be reused. This architecture is similar to the cbow model of Mikolov et al. (2013), where the middle word is replaced by a label. We use the softmax function f to compute the probability distribution over the predefined classes. For a set of N documents, this leads to minimizing the negative loglikelihood over the classes: −1 N N X n=1 yn log(f(BAxn)), where xn is the normalized bag of features of the nth document, yn the label, A and B the weight matrices. This model is trained asynchronously on multiple CPUs using stochastic gradient descent and a linearly decaying learning rate.

[P2_p2_c03] (paper P2, page 2, section "2.2 N-gram features")
Bag of words is invariant to word order but taking explicitly this order into account is often computationally very expensive. Instead, we use a bag of n-grams as additional features to capture some partial information about the local word order. This is very efficient in practice while achieving comparable results to methods that explicitly use the order (Wang and Manning, 2012). We maintain a fast and memory efficient mapping of the n-grams by using the hashing trick (Weinberger et al., 2009) with the same hashing function as in Mikolov et al. (2011) and 10M bins if we only used bigrams, and 100M otherwise.

[P2_p1_c03] (paper P2, page 1, section "1 Introduction")
Text classification is an important task in Natural Language Processing with many applications, such as web search, information retrieval, ranking and document classification (Deerwester et al., 1990; Pang and Lee, 2008). Recently, models based on neural networks have become increasingly popular (Kim, 2014; Zhang and LeCun, 2015; Conneau et al., 2016). While these models achieve very good performance in practice, they tend to be relatively slow both at train and test time, limiting their use on very large datasets. Meanwhile, linear classifiers are often considered as strong baselines for text classification problems (Joachims, 1998; McCallum and Nigam, 1998; Fan et al., 2008). Despite their simplicity, they often obtain stateof-the-art performances if the right features are used (Wang and Manning, 2012). They also have the potential to scale to very large corpus (Agarwal et al., 2014). In this work, we explore ways to scale these baselines to very large corpus with a large output space, in the context of text classification. Inspired by the recent work in efficient word representation learning (Mikolov et al., 2013; Levy et al., 2015), we show that linear models with a rank constraint and a fast loss approximation can train on a billion words within ten minutes, while achieving performance on par with the state-of-the-art. We evaluate the quality of our approach fastText1 on two different tasks, namely tag prediction and sentiment analysis.

[P2_p2_c04] (paper P2, page 2, section "3 Experiments")
We evaluate fastText on two different tasks. First, we compare it to existing text classifers on the problem of sentiment analysis. Then, we evaluate its capacity to scale to large output space on a tag prediction dataset. Note that our model could be implemented with the Vowpal Wabbit library,2 but we observe in practice, that our tailored implementation is at least 2-5× faster.
```
