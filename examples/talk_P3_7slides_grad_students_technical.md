# Distilling Knowledge in Neural Networks

_Generated 2026-10-26 16:25_

## Request
- **Topic:** the paper's motivation, method, key equations and results  |  **Focus:** methods
- **Paper:** P3  |  **Audience:** grad_students  |  **Style:** technical
- **Slides:** 7  |  **Notes per slide:** 3  |  **Preserve equations:** yes  |  **Script:** 5min (~750 words)

## Slides

### Slide 1: Motivation: Ensembles vs. Deployment

- A simple way to improve machine learning performance is to average predictions from an ensemble of models [P3_p1_c02].
- Ensembles are cumbersome and computationally expensive for large-scale deployment to many users [P3_p1_c02].
- We want to transfer knowledge from a cumbersome model into a single small model, a process called distillation [P3_p1_c03].

**Speaker notes:**

1. Training many different models on the same data and averaging their predictions is a reliable technique to boost performance [P3_p1_c02].
2. However, deploying these large ensembles requires too much computation and causes high latency for users [P3_p1_c03].
3. Our goal is to capture the knowledge of a large ensemble or a regularized large model and compress it into a deployable small model [P3_p1_c03].

### Slide 2: Method: The Softmax Temperature

- Neural networks produce class probabilities using a softmax output layer that converts logits into probabilities [P3_p2_c06].
- The standard softmax is generalized by introducing a temperature $T$ that is normally set to 1 [P3_p2_c06].
- Raising the temperature produces a much softer set of target probabilities that reveal rich similarity structures [P3_p2_c04][P3_p2_c06].

$$ qi = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} $$

**Speaker notes:**

1. The softmax converts the logit $z_i$ computed for each class into a probability $q_i$ [P3_p2_c06].
2. By raising the temperature $T$ in $q_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}$, we soften the probability distribution [P3_p2_c04][P3_p2_c06].
3. This soft output exposes valuable information about how classes relate, such as which 2 looks like a 3 or a 7 [P3_p2_c04].

### Slide 3: Method: Training the Distilled Model

- The distilled model is trained using the same high temperature $T$ used by the cumbersome model [P3_p3_c02].
- Performance improves by using a weighted average of two different objective functions [P3_p3_c02].
- Gradients from soft targets scale as $1/T^2$, so they are multiplied by $T^2$ when combining objectives [P3_p3_c02].

**Speaker notes:**

1. After training, the distilled model uses a temperature of 1 for standard deployment [P3_p3_c02].
2. The first objective function uses cross-entropy with the soft targets at high temperature $T$ [P3_p3_c02].
3. The second objective function uses cross-entropy with correct labels at a temperature of 1, typically with a lower weight [P3_p3_c02].

### Slide 4: Key Equations: Matching Logits as a Special Case

- Each case contributes a cross-entropy gradient with respect to each logit of the distilled model [P3_p3_c03].
- At high temperatures compared to logit magnitude, the gradient can be approximated via Taylor expansion [P3_p3_c03].
- Assuming zero-meaned logits, the distillation gradient simplifies to a squared difference form [P3_p3_c03].

$$ \frac{\partial C}{\partial z_i} = \frac{1}{T} (q_i - p_i) = \frac{1}{T} \left( \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} - \frac{\exp(v_i/T)}{\sum_j \exp(v_j/T)} \right) $$

$$ \frac{\partial C}{\partial z_i} \approx \frac{1}{NT^2} (z_i - v_i) $$

**Speaker notes:**

1. The general gradient formula is $\frac{\partial C}{\partial z_i} = \frac{1}{T} (q_i - p_i)$, linking distilled logits $z_i$ and cumbersome logits $v_i$ [P3_p3_c03].
2. When the temperature is very high, we can approximate the softmax expansion to get $\frac{\partial C}{\partial z_i} \approx \frac{1}{T} \left( 1 + \frac{z_i}{T} / N + \sum_j \frac{z_j}{T} - 1 + \frac{v_i}{T} / N + \sum_j \frac{v_j}{T} \right)$ [P3_p3_c03].
3. When logits are zero-meaned, this reduces to minimizing the squared difference $\frac{1}{NT^2} (z_i - v_i)$, proving that matching logits is a special case of distillation [P3_p2_c04][P3_p3_c03].

### Slide 5: Results: MNIST and Speech Recognition

- A small net regularized by soft targets from a large net achieved 74 test errors compared to 146 without it [P3_p4_c01].
- More than 80% of the ensemble's accuracy improvement on acoustic frame classification is transferred to the distilled model [P3_p5_c02].
- Distillation successfully extracts more useful information from the training set than training with hard labels alone [P3_p5_c02].

**Speaker notes:**

1. On MNIST, soft targets transferred generalization knowledge even when the transfer set contained no translated data [P3_p4_c01].
2. For speech recognition, 10 separate DNN models were trained to create an ensemble baseline [P3_p5_c02].
3. The distilled model successfully captured the performance gains of the large ensemble despite a mismatch with the ultimate Word Error Rate objective [P3_p5_c02].

### Slide 6: Method Extension: Ensembles of Specialists

- We introduce a new type of ensemble composed of a generalist model and multiple specialist models [P3_p1_c02][P3_p6_c04].
- Specialist models learn to distinguish fine-grained classes that the full models frequently confuse [P3_p1_c02].
- Specialist clusters are derived by applying online K-means to the covariance matrix of the generalist model's predictions [P3_p6_c03].

$$ KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q) $$

**Speaker notes:**

1. Specialists focus on fine-grained classes and can be trained rapidly and in parallel unlike a mixture of experts [P3_p1_c02].
2. During inference, we find the active set of specialists $A_k$ and minimize $KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q)$ [P3_p6_c04].
3. This formulation sums the probabilities assigned by $q$ to all classes in a specialist's dustbin class [P3_p6_c04].

### Slide 7: Results: Specialists on the JFT Dataset

- Google's JFT dataset contains 100 million labeled images with 15,000 labels [P3_p5_c05].
- Training 61 specialist models yields a 4.4% relative improvement in overall test accuracy [P3_p7_c02].
- Accuracy improvements are larger when more specialist models cover a particular image class [P3_p7_c02].

**Speaker notes:**

1. The baseline JFT model is a deep convolutional neural network trained for about six months using asynchronous SGD [P3_p5_c05].
2. Specialists train extremely fast, taking only a few days compared to weeks for the full model [P3_p7_c02].
3. Because specialist training is completely independent, it offers an easily parallelizable path to scaling up performance [P3_p7_c02].

## Full speaker script

Now let's look at the motivation behind our work. A very simple way to improve the performance of almost any machine learning algorithm is to train many different models on the same data and then to average their predictions [P3_p1_c02]. Unfortunately, making predictions using a whole ensemble of models is cumbersome and may be too computationally expensive to allow deployment to a large number of users, especially if individual models are large neural nets [P3_p1_c02]. To solve this, we develop an approach to compress the knowledge in an ensemble into a single model that is much easier to deploy, which we call distillation [P3_p1_c02][P3_p1_c03]. Moving on to the method, neural networks typically produce class probabilities by using a softmax output layer that converts the logit $z_i$ computed for each class into a probability $q_i$ [P3_p2_c06]. We generalize this by raising the temperature of the final softmax until the cumbersome model produces a suitably soft set of targets [P3_p2_c04]. The equation for this softmax probability is given by $q_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}$ [P3_p2_c06]. Raising the temperature reveals a rich similarity structure over the data, showing which classes look like others [P3_p2_c04]. Next, let us examine how we train the distilled model itself. The same high temperature is used when training the distilled model, but after it has been trained it uses a temperature of 1 [P3_p3_c02]. We found that a better way to incorporate correct labels is to use a weighted average of two different objective functions, where the first is cross-entropy with soft targets at high temperature, and the second is cross-entropy with correct labels at a temperature of 1 [P3_p3_c02]. Because the magnitudes of the gradients produced by the soft targets scale as $1/T^2$, it is important to multiply them by $T^2$ when using both hard and soft targets [P3_p3_c02]. Let us now dive into the key equations that explain the mechanics of distillation. Each case in the transfer set contributes a cross-entropy gradient with respect to each logit of the distilled model, expressed as $\frac{\partial C}{\partial z_i} = \frac{1}{T} (q_i - p_i) = \frac{1}{T} \left( \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} - \frac{\exp(v_i/T)}{\sum_j \exp(v_j/T)} \right)$ [P3_p3_c03]. If the temperature is high compared with the magnitude of the logits, we can approximate this gradient using a Taylor expansion [P3_p3_c03]. Assuming the logits have been zero-meaned separately for each transfer case, this simplifies to $\frac{\partial C}{\partial z_i} \approx \frac{1}{NT^2} (z_i - v_i)$ [P3_p3_c03]. This proves that matching the logits of the cumbersome model is actually a special case of distillation [P3_p2_c04][P3_p3_c03]. Turning to our empirical results, on MNIST tasks, a smaller net regularized solely by matching soft targets at a temperature of 20 achieved 74 test errors compared to 146 errors without regularization [P3_p4_c01]. Furthermore, when applied to speech recognition, more than 80% of the improvement in frame classification accuracy achieved by a 10-model ensemble is successfully transferred to the distilled model [P3_p5_c02]. Beyond simple distillation, we also introduce a new type of ensemble composed of one or more full models and many specialist models which learn to distinguish fine-grained classes that the full models confuse [P3_p1_c02]. These specialist models can be trained rapidly and in parallel [P3_p1_c02]. During inference, we find the active set of specialists $A_k$ and find the full probability distribution $q$ that minimizes $KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q)$ [P3_p6_c04]. Finally, looking at results on Google's internal JFT dataset containing 100 million labeled images, training 61 specialist models gives a 4.4% relative improvement in test accuracy overall [P3_p7_c02][P3_p5_c05]. We are encouraged by the general trend that accuracy improvements are larger when we have more specialists covering a particular class, since training independent specialist models is very easy to parallelize [P3_p7_c02].

## Checks
- Attempts: 1 (right first time)
- Script words: 612 (target ~750)
- Remaining problems: none

## Sources given to the LLM

- `P3_p1_c02` — page 1, Abstract (cited)
- `P3_p1_c04` — page 1, 1 Introduction (not cited)
- `P3_p2_c04` — page 2, 1 Introduction (cited)
- `P3_p3_c02` — page 3, 2 Distillation (cited)
- `P3_p5_c02` — page 5, 4.1 Results (cited)
- `P3_p1_c03` — page 1, 1 Introduction (cited)
- `P3_p4_c01` — page 4, 3 Preliminary experiments on MNIST (cited)
- `P3_p6_c04` — page 6, 5.4 Performing inference with ensembles of specialists (cited, equation)
- `P3_p6_c03` — page 6, 5.3 Assigning classes to specialists (cited)
- `P3_p4_c03` — page 4, 4 Experiments on speech recognition (not cited, equation)
- `P3_p7_c02` — page 7, 5.5 Results (cited)
- `P3_p5_c05` — page 5, 5.1 The JFT dataset (cited)
- `P3_p5_c03` — page 5, 4.1 Results (not cited)
- `P3_p2_c05` — page 2, 1 Introduction (not cited)
- `P3_p3_c03` — page 3, 2.1 Matching logits is a special case of distillation (cited, equation)
- `P3_p2_c06` — page 2, 2 Distillation (cited, equation)

## Full prompt

```text
TASK: Create a 7-slide talk about: the paper's motivation, method, key equations and results
FOCUS: spend most slides on methods.

AUDIENCE: graduate students in machine learning: they know the basics and want the method, the key equations and the experimental evidence
STYLE: technical: precise terms, mention the method and equations where they help

STRUCTURE:
- Exactly 7 slides in a logical order (e.g. motivation -> method -> results -> takeaway).
- Each slide: a short title, 3-5 bullets, and EXACTLY 3 speaker notes.
- PRESERVE KEY EQUATIONS: put the important equations from the sources in the slides' "equations" lists (LaTeX, no $ signs) and explain them in the speaker notes with inline LaTeX $...$. Copy every term; do not simplify an equation.
- Speaker notes ADD to the bullets (an example, an explanation, a "why it matters") - never
  just repeat a bullet.
- "script": the full spoken talk covering all slides in order, about 750 words
  (5min when read aloud at 150 words per minute). Write it as natural speech for this
  audience, with transitions between slides ("Now let's look at..."). Do NOT paste the bullets
  and notes together, and never say the same sentence twice.
- Cite chunk IDs in square brackets after every bullet, speaker note and script sentence that
  states a fact.

SOURCES:
[P3_p1_c02] (paper P3, page 1, section "Abstract")
A very simple way to improve the performance of almost any machine learning algorithm is to train many different models on the same data and then to average their predictions [3]. Unfortunately, making predictions using a whole ensemble of models is cumbersome and may be too computationally expensive to allow deployment to a large number of users, especially if the individual models are large neural nets. Caruana and his collaborators [1] have shown that it is possible to compress the knowledge in an ensemble into a single model which is much easier to deploy and we develop this approach further using a different compression technique. We achieve some surprising results on MNIST and we show that we can significantly improve the acoustic model of a heavily used commercial system by distilling the knowledge in an ensemble of models into a single model. We also introduce a new type of ensemble composed of one or more full models and many specialist models which learn to distinguish fine-grained classes that the full models confuse. Unlike a mixture of experts, these specialist models can be trained rapidly and in parallel.

[P3_p1_c04] (paper P3, page 1, section "1 Introduction")
In their important paper they demonstrate convincingly that the knowledge acquired by a large ensemble of models can be transferred to a single small model. A conceptual block that may have prevented more investigation of this very promising approach is that we tend to identify the knowledge in a trained model with the learned parameter values and this makes it hard to see how we can change the form of the model but keep the same knowledge. A more abstract view of the knowledge, that frees it from any particular instantiation, is that it is a learned ∗Also affiliated with the University of Toronto and the Canadian Institute for Advanced Research. †Equal contribution.

[P3_p2_c04] (paper P3, page 2, section "1 Introduction")
For tasks like MNIST in which the cumbersome model almost always produces the correct answer with very high confidence, much of the information about the learned function resides in the ratios of very small probabilities in the soft targets. For example, one version of a 2 may be given a probability of 10−6 of being a 3 and 10−9 of being a 7 whereas for another version it may be the other way around. This is valuable information that defines a rich similarity structure over the data (i. e. it says which 2’s look like 3’s and which look like 7’s) but it has very little influence on the cross-entropy cost function during the transfer stage because the probabilities are so close to zero. Caruana and his collaborators circumvent this problem by using the logits (the inputs to the final softmax) rather than the probabilities produced by the softmax as the targets for learning the small model and they minimize the squared difference between the logits produced by the cumbersome model and the logits produced by the small model. Our more general solution, called “distillation”, is to raise the temperature of the final softmax until the cumbersome model produces a suitably soft set of targets. We then use the same high temperature when training the small model to match these soft targets. We show later that matching the logits of the cumbersome model is actually a special case of distillation.

[P3_p3_c02] (paper P3, page 3, section "2 Distillation")
The same high temperature is used when training the distilled model, but after it has been trained it uses a temperature of 1. When the correct labels are known for all or some of the transfer set, this method can be significantly improved by also training the distilled model to produce the correct labels. One way to do this is to use the correct labels to modify the soft targets, but we found that a better way is to simply use a weighted average of two different objective functions. The first objective function is the cross entropy with the soft targets and this cross entropy is computed using the same high temperature in the softmax of the distilled model as was used for generating the soft targets from the cumbersome model. The second objective function is the cross entropy with the correct labels. This is computed using exactly the same logits in softmax of the distilled model but at a temperature of 1. We found that the best results were generally obtained by using a condiderably lower weight on the second objective function. Since the magnitudes of the gradients produced by the soft targets scale as 1/T 2 it is important to multiply them by T 2 when using both hard and soft targets. This ensures that the relative contributions of the hard and soft targets remain roughly unchanged if the temperature used for distillation is changed while experimenting with meta-parameters.

[P3_p5_c02] (paper P3, page 5, section "4.1 Results")
We trained 10 separate models to predict P(ht|st; θ), using exactly the same architecture and training procedure as the baseline. The models are randomly initialized with different initial parameter values and we find that this creates sufficient diversity in the trained models to allow the averaged predictions of the ensemble to significantly outperform the individual models. We have explored adding diversity to the models by varying the sets of data that each model sees, but we found this to not significantly change our results, so we opted for the simpler approach. For the distillation we tried temperatures of [1, 2, 5, 10] and used a relative weight of 0.5 on the cross-entropy for the hard targets, where bold font indicates the best value that was used for table 1 . Table 1 shows that, indeed, our distillation approach is able to extract more useful information from the training set than simply using the hard labels to train a single model. More than 80% of the improvement in frame classification accuracy achieved by using an ensemble of 10 models is transferred to the distilled model which is similar to the improvement we observed in our preliminary experiments on MNIST. The ensemble gives a smaller improvement on the ultimate objective of WER (on a 23K-word test set) due to the mismatch in the objective function, but again, the improvement in WER achieved by the ensemble is transferred to the distilled model.

[P3_p1_c03] (paper P3, page 1, section "1 Introduction")
Many insects have a larval form that is optimized for extracting energy and nutrients from the environment and a completely different adult form that is optimized for the very different requirements of traveling and reproduction. In large-scale machine learning, we typically use very similar models for the training stage and the deployment stage despite their very different requirements: For tasks like speech and object recognition, training must extract structure from very large, highly redundant datasets but it does not need to operate in real time and it can use a huge amount of computation. Deployment to a large number of users, however, has much more stringent requirements on latency and computational resources. The analogy with insects suggests that we should be willing to train very cumbersome models if that makes it easier to extract structure from the data. The cumbersome model could be an ensemble of separately trained models or a single very large model trained with a very strong regularizer such as dropout [9]. Once the cumbersome model has been trained, we can then use a different kind of training, which we call “distillation” to transfer the knowledge from the cumbersome model to a small model that is more suitable for deployment. A version of this strategy has already been pioneered by Rich Caruana and his collaborators [1]. In their important paper they demonstrate convincingly that the knowledge acquired by a large ensemble of models can be transferred to a single small model.

[P3_p4_c01] (paper P3, page 4, section "3 Preliminary experiments on MNIST")
jittered by up to two pixels in any direction. This net achieved 67 test errors whereas a smaller net with two hidden layers of 800 rectified linear hidden units and no regularization achieved 146 errors. But if the smaller net was regularized solely by adding the additional task of matching the soft targets produced by the large net at a temperature of 20, it achieved 74 test errors. This shows that soft targets can transfer a great deal of knowledge to the distilled model, including the knowledge about how to generalize that is learned from translated training data even though the transfer set does not contain any translations. When the distilled net had 300 or more units in each of its two hidden layers, all temperatures above 8 gave fairly similar results. But when this was radically reduced to 30 units per layer, temperatures in the range 2.5 to 4 worked significantly better than higher or lower temperatures.

[P3_p6_c04] (paper P3, page 6, section "5.4 Performing inference with ensembles of specialists")
Before investigating what happens when specialist models are distilled, we wanted to see how well ensembles containing specialists performed. In addition to the specialist models, we always have a generalist model so that we can deal with classes for which we have no specialists and so that we can decide which specialists to use. Given an input image x, we do top-one classification in two steps: Step 1: For each test case, we find the n most probable classes according to the generalist model. Call this set of classes k. In our experiments, we used n = 1. Step 2: We then take all the specialist models, m, whose special subset of confusable classes, Sm, has a non-empty intersection with k and call this the active set of specialists Ak (note that this set may be empty). We then find the full probability distribution q over all the classes that minimizes: KL(pg, q) + X m∈Ak KL(pm, q) (5) where KL denotes the KL divergence, and pm pg denote the probability distribution of a specialist model or the generalist full model. The distribution pm is a distribution over all the specialist classes of m plus a single dustbin class, so when computing its KL divergence from the full q distribution we sum all of the probabilities that the full q distribution assigns to all the classes in m’s dustbin.

[P3_p6_c03] (paper P3, page 6, section "5.3 Assigning classes to specialists")
In order to derive groupings of object categories for the specialists, we decided to focus on categories that our full network often confuses. Even though we could have computed the confusion matrix and used it as a way to find such clusters, we opted for a simpler approach that does not require the true labels to construct the clusters. In particular, we apply a clustering algorithm to the covariance matrix of the predictions of our generalist model, so that a set of classes Sm that are often predicted together will be used as targets for one of our specialist models, m. We applied an on-line version of the K-means algorithm to the columns of the covariance matrix, and obtained reasonable clusters (shown in Table 2). We tried several clustering algorithms which produced similar results.

[P3_p4_c03] (paper P3, page 4, section "4 Experiments on speech recognition")
In this section, we investigate the effects of ensembling Deep Neural Network (DNN) acoustic models that are used in Automatic Speech Recognition (ASR). We show that the distillation strategy that we propose in this paper achieves the desired effect of distilling an ensemble of models into a single model that works significantly better than a model of the same size that is learned directly from the same training data. State-of-the-art ASR systems currently use DNNs to map a (short) temporal context of features derived from the waveform to a probability distribution over the discrete states of a Hidden Markov Model (HMM) [4]. More specifically, the DNN produces a probability distribution over clusters of tri-phone states at each time and a decoder then finds a path through the HMM states that is the best compromise between using high probability states and producing a transcription that is probable under the language model. Although it is possible (and desirable) to train the DNN in such a way that the decoder (and, thus, the language model) is taken into account by marginalizing over all possible paths, it is common to train the DNN to perform frame-by-frame classification by (locally) minimizing the cross entropy between the predictions made by the net and the labels given by a forced alignment with the ground truth sequence of states for each observation: θ = arg max θ′ P(ht|st; θ′)

[P3_p7_c02] (paper P3, page 7, section "5.5 Results")
Starting from the trained baseline full network, the specialists train extremely fast (a few days instead of many weeks for JFT). Also, all the specialists are trained completely independently. Table 3 shows the absolute test accuracy for the baseline system and the baseline system combined with the specialist models. With 61 specialist models, there is a 4.4% relative improvement in test accuracy overall. We also report conditional test accuracy, which is the accuracy by only considering examples belonging to the specialist classes, and restricting our predictions to that subset of classes. For our JFT specialist experiments, we trained 61 specialist models, each with 300 classes (plus the dustbin class). Because the sets of classes for the specialists are not disjoint, we often had multiple specialists covering a particular image class. Table 4 shows the number of test set examples, the change in the number of examples correct at position 1 when using the specialist(s), and the relative percentage improvement in top1 accuracy for the JFT dataset broken down by the number of specialists covering the class. We are encouraged by the general trend that accuracy improvements are larger when we have more specialists covering a particular class, since training independent specialist models is very easy to parallelize.

[P3_p5_c05] (paper P3, page 5, section "5.1 The JFT dataset")
JFT is an internal Google dataset that has 100 million labeled images with 15,000 labels. When we did this work, Google’s baseline model for JFT was a deep convolutional neural network [7] that had been trained for about six months using asynchronous stochastic gradient descent on a large number of cores. This training used two types of parallelism [2]. First, there were many replicas of the neural net running on different sets of cores and processing different mini-batches from the training set. Each replica computes the average gradient on its current mini-batch and sends this gradient to a sharded parameter server which sends back new values for the parameters. These new values reflect all of the gradients received by the parameter server since the last time it sent parameters to the replica. Second, each replica is spread over multiple cores by putting different subsets of the neurons on each core. Ensemble training is yet a third type of parallelism that can be wrapped

[P3_p5_c03] (paper P3, page 5, section "4.1 Results")
We have recently become aware of related work on learning a small acoustic model by matching the class probabilities of an already trained larger model [8]. However, they do the distillation at a temperature of 1 using a large unlabeled dataset and their best distilled model only reduces the error rate of the small model by 28% of the gap between the error rates of the large and small models when they are both trained with hard labels.

[P3_p2_c05] (paper P3, page 2, section "1 Introduction")
We show later that matching the logits of the cumbersome model is actually a special case of distillation. The transfer set that is used to train the small model could consist entirely of unlabeled data [1] or we could use the original training set. We have found that using the original training set works well, especially if we add a small term to the objective function that encourages the small model to predict the true targets as well as matching the soft targets provided by the cumbersome model. Typically, the small model cannot exactly match the soft targets and erring in the direction of the correct answer turns out to be helpful.

[P3_p3_c03] (paper P3, page 3, section "2.1 Matching logits is a special case of distillation")
Each case in the transfer set contributes a cross-entropy gradient, dC/dzi, with respect to each logit, zi of the distilled model. If the cumbersome model has logits vi which produce soft target probabilities pi and the transfer training is done at a temperature of T , this gradient is given by: ∂C ∂zi = 1 T (qi −pi) = 1 T ezi/T P j ezj/T − evi/T P j evj/T ! (2) If the temperature is high compared with the magnitude of the logits, we can approximate: ∂C ∂zi ≈1 T 1 + zi/T N + P j zj/T − 1 + vi/T N + P j vj/T ! (3) If we now assume that the logits have been zero-meaned separately for each transfer case so that P j zj = P j vj = 0 Eq. 3 simplifies to: ∂C ∂zi ≈ 1 NT 2 (zi −vi) (4)

[P3_p2_c06] (paper P3, page 2, section "2 Distillation")
Neural networks typically produce class probabilities by using a “softmax” output layer that converts the logit, zi, computed for each class into a probability, qi, by comparing zi with the other logits. qi = exp(zi/T ) P j exp(zj/T ) (1)
```
