# Script: the problem the paper solves, its main idea, and its key results

_Generated 2026-10-25 18:28_

## Input
- **Topic:** the problem the paper solves, its main idea, and its key results
- **Paper:** P1
- **Audience:** grad_students  |  **Length:** 90s (target ~225 words)  |  **Style:** technical

## Output

This paper evaluates a simple convolutional neural network built on top of pre-trained word vectors for sentence-level classification tasks [P1_p1_c02]. 

Let a sentence be represented as $x_{1:n} = x_1 \oplus x_2 \oplus \dots \oplus x_n$, where $\oplus$ is the concatenation operator [P1_p2_c01]. A convolution operation applies a filter $w \in \mathbb{R}^{h \cdot k}$ to a window of $h$ words to produce a feature $c_i$ via the equation $c_i = f(w \cdot x_{i:i+h-1} + b)$, where $b \in \mathbb{R}$ is a bias term and $f$ is a non-linear function like the hyperbolic tangent [P1_p2_c01]. This filter slides over windows in the sentence to produce a feature map $c = [c_1, c_2, \dots, c_{n-h+1}]$ [P1_p2_c01]. A max-over-time pooling operation then takes the maximum value $\hat{c} = \max\{c\}$ as the feature for that filter [P1_p2_c01]. The architecture uses multiple filters with varying window sizes, passing these features to a fully connected softmax layer for classification [P1_p2_c02]. The authors also propose a multichannel variant where one channel of word vectors is kept static and another is fine-tuned via backpropagation [P1_p2_c02].

Experimentally, a baseline with randomly initialized words (CNN-rand) performs poorly on its own, but a model with static pre-trained vectors (CNN-static) achieves remarkable results and competes with sophisticated deep learning models that use complex pooling or parse trees [P1_p4_c03]. Fine-tuning the pre-trained vectors (CNN-non-static) yields further performance gains [P1_p4_c03]. Ultimately, these CNN models improve upon the state of the art on 4 out of 7 tasks, including sentiment analysis and question classification [P1_p1_c02].

## Checks
- Words: 249 (target ~225)
- Chunks cited: 4 of 6 provided
- Unknown (invented) citations: none

## Sources given to the LLM

- `P1_p1_c02` — page 1, Abstract (✅ cited)
- `P1_p2_c01` — page 2, 2 Model (✅ cited)
- `P1_p4_c03` — page 4, 4 Results and Discussion (✅ cited)
- `P1_p2_c02` — page 2, 2 Model (✅ cited)
- `P1_p1_c03` — page 1, 1 Introduction (not cited)
- `P1_p5_c04` — page 5, 5 Conclusion (not cited)
