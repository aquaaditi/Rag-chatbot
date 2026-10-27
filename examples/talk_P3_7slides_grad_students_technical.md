# Distilling Knowledge in Neural Networks

_Generated 2026-10-28 00:00_

## Request
- **Topic:** the paper's motivation, method, key equations and results  |  **Focus:** methods
- **Paper:** P3  |  **Audience:** grad_students  |  **Style:** technical
- **Slides:** 7  |  **Notes per slide:** 3  |  **Preserve equations:** yes  |  **Script:** 5min (~750 words)

## Slides

### Slide 1: Motivation: Ensembles vs. Deployment

- A simple way to improve machine learning performance is averaging predictions from an ensemble [P3_p1_c02].
- Ensemble models are cumbersome and too computationally expensive for large-scale deployment [P3_p1_c02].
- We can transfer knowledge from a cumbersome ensemble into a single small model called distillation [P3_p1_c03].
- We can also use specialist models to learn fine-grained classes that full models confuse [P3_p1_c02].

**Speaker notes:**

1. Training many different models on the same data and averaging their predictions is a reliable way to boost performance [P3_p1_c02].
2. However, deploying massive neural net ensembles to millions of users creates severe latency and computational challenges [P3_p1_c03].
3. Drawing inspiration from biological insects that have entirely different larval and adult forms, we can decouple training from deployment [P3_p1_c03].

### Slide 2: The Distillation Method

- Neural networks typically produce class probabilities using a softmax output layer [P3_p2_c06].
- We raise the temperature $T$ of the final softmax to produce soft targets containing rich similarity data [P3_p2_c04].
- The same high temperature is used when training the distilled model to match these soft targets [P3_p3_c02].
- After training, the distilled model uses a temperature of 1 for standard inference tasks [P3_p3_c02].

$$ qi = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} $$

**Speaker notes:**

1. The softmax function converts raw logit scores $z_i$ into probabilities $q_i$ using $q_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}$ [P3_p2_c06].
2. By raising the temperature $T$, we reveal small probabilities that show which classes look like others, such as a 2 looking like a 3 [P3_p2_c04].
3. Once distillation training completes, we reset the temperature back to 1 for deployment [P3_p3_c02].

### Slide 3: Distillation Objective Function

- Performance improves by jointly training on soft targets and correct true labels [P3_p3_c02].
- The first objective uses cross-entropy with soft targets at a high temperature $T$ [P3_p3_c02].
- The second objective uses cross-entropy with correct labels at a temperature of 1 [P3_p3_c02].
- Gradients from soft targets scale as $1/T^2$, so they are multiplied by $T^2$ when combining objectives [P3_p3_c02].

**Speaker notes:**

1. We utilize a weighted average of two different objective functions to leverage both teacher guidance and ground truth [P3_p3_c02].
2. A considerably lower weight is generally used on the second objective function involving the correct labels [P3_p3_c02].
3. Multiplying by $T^2$ ensures that the relative contributions of hard and soft targets remain constant when experimenting with the temperature parameter [P3_p3_c02].

### Slide 4: Matching Logits as a Special Case

- Each transfer case contributes a cross-entropy gradient with respect to each logit $z_i$ [P3_p3_c03].
- The general gradient equation links the distilled model probabilities $q_i$ and cumbersome probabilities $p_i$ [P3_p3_c03].
- When the temperature is very high, the gradient expression can be cleanly approximated [P3_p3_c03].
- Assuming zero-meaned logits, matching logits becomes a direct mathematical special case of distillation [P3_p3_c03].

$$ \frac{\partial C}{\partial z_i} = \frac{1}{T}(q_i - p_i) = \frac{1}{T} \left( \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} - \frac{\exp(v_i/T)}{\sum_j \exp(v_j/T)} \right) $$

$$ \frac{\partial C}{\partial z_i} \approx \frac{1}{T} \left( \frac{1 + z_i/T}{N + \sum_j z_j/T} - \frac{1 + v_i/T}{N + \sum_j v_j/T} \right) $$

$$ \frac{\partial C}{\partial z_i} \approx \frac{1}{NT^2}(z_i - v_i) $$

**Speaker notes:**

1. The gradient of the cost function with respect to the logits is given by $\frac{\partial C}{\partial z_i} = \frac{1}{T}(q_i - p_i)$ [P3_p3_c03].
2. When $T$ is high compared to logit magnitudes, we apply a first-order Taylor expansion approximation [P3_p3_c03].
3. Minimizing the squared difference between logits, as explored by Caruana, emerges naturally as $\frac{1}{NT^2}(z_i - v_i)$ when the logits are zero-meaned [P3_p2_c04][P3_p3_c03].

### Slide 5: Specialist Models and Grouping

- We introduce a new ensemble type with a generalist model and multiple specialist models [P3_p1_c02].
- Specialist models focus on learning to distinguish fine-grained classes that the full model confuses [P3_p1_c02].
- We apply an on-line K-means algorithm to the covariance matrix of generalist predictions to find clusters [P3_p6_c03].
- Specialists train completely independently and extremely fast compared to massive base models [P3_p7_c02].

**Speaker notes:**

1. Specialists allow us to tackle enormous output spaces by specializing in subsets of confusable categories [P3_p1_c02][P3_p6_c03].
2. Clustering is performed directly on the covariance matrix of the generalist predictions without requiring true labels [P3_p6_c03].
3. Each specialist trains independently in just a few days instead of weeks, making parallel training highly efficient [P3_p7_c02].

### Slide 6: Inference with Ensembles of Specialists

- Given an input image $x$, top-one classification is performed in two distinct steps [P3_p6_c04].
- Step 1 finds the $n$ most probable classes according to the generalist model [P3_p6_c04].
- Step 2 activates all specialist models whose confusable subset intersects with the generalist top classes [P3_p6_c04].
- The final distribution $q$ minimizes the KL divergence sum across the generalist and active specialists [P3_p6_c04].

$$ KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q) $$

**Speaker notes:**

1. During inference, we identify an active set of specialists $A_k$ whose target classes overlap with the generalist prediction [P3_p6_c04].
2. We then find the full probability distribution $q$ that minimizes the combined objective $KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q)$ [P3_p6_c04].
3. Specialist probability distributions include a special dustbin class to absorb probabilities assigned to non-target categories [P3_p6_c04].

### Slide 7: Experimental Results and Takeaways

- More than 80% of the ensemble accuracy improvement transfers to distilled speech acoustic models [P3_p5_c02].
- On MNIST, soft targets successfully transfer generalization knowledge even without explicit translation data [P3_p4_c01].
- Using 61 specialist models yields a 4.4% relative improvement in overall test accuracy on the JFT dataset [P3_p7_c02].
- Distillation successfully compresses cumbersome ensembles into single models suitable for high-throughput deployment [P3_p1_c02][P3_p1_c03].

**Speaker notes:**

1. Experiments confirm that distillation captures more useful information than training a single model from hard labels alone [P3_p5_c02].
2. On the internal JFT dataset with 100 million images, accuracy improvements grow larger when more specialists cover a particular class [P3_p7_c02].
3. Ultimately, knowledge distillation provides a powerful, practical bridge between high-capacity ensemble training and low-latency user deployment [P3_p1_c02][P3_p1_c03].

## Full speaker script

Now let's look at the motivation behind knowledge distillation. A simple way to improve the performance of almost any machine learning algorithm is to train many different models on the same data and then to average their predictions [P3_p1_c02]. Unfortunately, making predictions using a whole ensemble of models is cumbersome and may be too computationally expensive to allow deployment to a large number of users, especially if the individual models are large neural nets [P3_p1_c02]. Drawing an analogy with insects that have a larval form optimized for feeding and an adult form optimized for travel, we can afford to train very cumbersome models to extract structure, and then transfer that knowledge into a small model suitable for deployment via a process called distillation [P3_p1_c03]. We can also introduce a new type of ensemble composed of a generalist model and many specialist models which learn to distinguish fine-grained classes that the full models confuse [P3_p1_c02]. Now let's explore the distillation method itself. Neural networks typically produce class probabilities by using a softmax output layer that converts the logit $z_i$ computed for each class into a probability $q_i$ using $q_i = \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)}$ [P3_p2_c06]. By raising the temperature $T$ of the final softmax, the cumbersome model produces a suitably soft set of targets containing valuable similarity information about small probabilities [P3_p2_c04]. We then use that same high temperature when training the small model to match these soft targets [P3_p3_c02]. After the distilled model has been trained, it uses a temperature of 1 for standard predictions [P3_p3_c02]. Moving on to the objective function, we find that performance is significantly improved when we train the distilled model to also produce correct labels [P3_p3_c02]. This is achieved by using a weighted average of two different objective functions, where the first uses cross-entropy with soft targets at high temperature, and the second uses cross-entropy with correct labels at a temperature of 1 [P3_p3_c02]. Because the magnitudes of gradients produced by soft targets scale as $1/T^2$, we must multiply them by $T^2$ to keep relative contributions roughly unchanged when experimenting with temperatures [P3_p3_c02]. Next, let's examine how matching logits relates to distillation. Each case in the transfer set contributes a cross-entropy gradient with respect to each logit $z_i$, which is expressed generally as $\frac{\partial C}{\partial z_i} = \frac{1}{T}(q_i - p_i) = \frac{1}{T} \left( \frac{\exp(z_i/T)}{\sum_j \exp(z_j/T)} - \frac{\exp(v_i/T)}{\sum_j \exp(v_j/T)} \right)$ [P3_p3_c03]. When the temperature is high compared to the magnitude of the logits, this can be approximated as $\frac{\partial C}{\partial z_i} \approx \frac{1}{T} \left( \frac{1 + z_i/T}{N + \sum_j z_j/T} - \frac{1 + v_i/T}{N + \sum_j v_j/T} \right)$ [P3_p3_c03]. If we assume the logits have been zero-meaned separately for each transfer case, this equation simplifies neatly to $\frac{\partial C}{\partial z_i} \approx \frac{1}{NT^2}(z_i - v_i)$, showing that matching logits is just a special case of distillation [P3_p2_c04][P3_p3_c03]. Now let's turn to specialist models. To handle large datasets, we combine a generalist model with specialist models that focus on confusable categories [P3_p1_c02][P3_p6_c04]. We derive groupings by applying an online K-means clustering algorithm to the columns of the covariance matrix of the generalist model's predictions, bypassing the need for true labels during clustering [P3_p6_c03]. Starting from the baseline network, all specialists are trained completely independently and extremely fast, taking only a few days instead of many weeks [P3_p7_c02]. To perform inference with ensembles of specialists, we execute a two-step process for each input image $x$ [P3_p6_c04]. First, we find the $n$ most probable classes according to the generalist model [P3_p6_c04]. Second, we gather the active set of specialists whose confusable subset intersects with the generalist top classes, and find the full probability distribution $q$ that minimizes $KL(p_g, q) + \sum_{m \in A_k} KL(p_m, q)$ [P3_p6_c04]. Finally, looking at the experimental results, our distillation approach successfully extracts more useful information from the training set than hard labels alone [P3_p5_c02]. More than 80% of the acoustic model improvement achieved by a 10-model ensemble is successfully transferred to the distilled model [P3_p5_c02]. Furthermore, training with 61 specialist models on Google's internal JFT dataset results in a 4.4% relative improvement in overall test accuracy [P3_p7_c02]. These results demonstrate that knowledge distillation provides a robust and scalable solution for deploying high-performance machine learning models [P3_p1_c02][P3_p1_c03].

## Checks
- Attempts: 2 (self-corrected once)
- Script words: 699 (target ~750)
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
- `P3_p5_c05` — page 5, 5.1 The JFT dataset (not cited)
- `P3_p5_c03` — page 5, 4.1 Results (not cited)
- `P3_p2_c05` — page 2, 1 Introduction (not cited)
- `P3_p3_c03` — page 3, 2.1 Matching logits is a special case of distillation (cited, equation)
- `P3_p2_c06` — page 2, 2 Distillation (cited, equation)

## Provenance (every claim -> its source)

- Claims checked: 77   ✅ supported 53  ⚠️ weak 19  ❌ unsupported 1  ➖ uncited 4
- Citation coverage: 95%   Supported (factuality proxy): 69%   Mean similarity: 0.85   Number errors: 1

| | Where | Claim | Cited | Score | Best source sentence (page) |
|---|---|---|---|---|---|
| ✅ | slide 1 · bullet 1 | A simple way to improve machine learning performance is averaging predictions from an ensemble. | P3_p1_c02 | 0.89 | A very simple way to improve the performance of almost any machine learning algorithm is … (`P3_p1_c02`, p.1) |
| ✅ | slide 1 · bullet 2 | Ensemble models are cumbersome and too computationally expensive for large-scale deployment. | P3_p1_c02 | 0.91 | Unfortunately, making predictions using a whole ensemble of models is cumbersome and may … (`P3_p1_c02`, p.1) |
| ✅ | slide 1 · bullet 3 | We can transfer knowledge from a cumbersome ensemble into a single small model called distillation. | P3_p1_c03 | 0.87 | Once the cumbersome model has been trained, we can then use a different kind of training,… (`P3_p1_c03`, p.1) |
| ✅ | slide 1 · bullet 4 | We can also use specialist models to learn fine-grained classes that full models confuse. | P3_p1_c02 | 0.87 | We also introduce a new type of ensemble composed of one or more full models and many spe… (`P3_p1_c02`, p.1) |
| ✅ | slide 1 · note 1 | Training many different models on the same data and averaging their predictions is a reliable way to boost pe… | P3_p1_c02 | 0.90 | A very simple way to improve the performance of almost any machine learning algorithm is … (`P3_p1_c02`, p.1) |
| ⚠️ | slide 1 · note 2 | However, deploying massive neural net ensembles to millions of users creates severe latency and computational… | P3_p1_c03 | 0.77 | Deployment to a large number of users, however, has much more stringent requirements on l… (`P3_p1_c03`, p.1) |
| ⚠️ | slide 1 · note 3 | Drawing inspiration from biological insects that have entirely different larval and adult forms, we can decou… | P3_p1_c03 | 0.78 | Many insects have a larval form that is optimized for extracting energy and nutrients fro… (`P3_p1_c03`, p.1) |
| ✅ | slide 2 · bullet 1 | Neural networks typically produce class probabilities using a softmax output layer. | P3_p2_c06 | 0.86 | Neural networks typically produce class probabilities by using a “softmax” output layer t… (`P3_p2_c06`, p.2) |
| ⚠️ | slide 2 · bullet 2 | We raise the temperature $T$ of the final softmax to produce soft targets containing rich similarity data. | P3_p2_c04 | 0.79 | This is valuable information that defines a rich similarity structure over the data (i. e… (`P3_p2_c04`, p.2) |
| ✅ | slide 2 · bullet 3 | The same high temperature is used when training the distilled model to match these soft targets. | P3_p3_c02 | 0.86 | The same high temperature is used when training the distilled model, but after it has bee… (`P3_p3_c02`, p.3) |
| ✅ | slide 2 · bullet 4 | After training, the distilled model uses a temperature of 1 for standard inference tasks. | P3_p3_c02 | 0.88 | The same high temperature is used when training the distilled model, but after it has bee… (`P3_p3_c02`, p.3) |
| ✅ | slide 2 · note 1 | The softmax function converts raw logit scores $z_i$ into probabilities $q_i$ using $q_i = \frac{\exp(z_i/T)}… | P3_p2_c06 | 0.82 | Neural networks typically produce class probabilities by using a “softmax” output layer t… (`P3_p2_c06`, p.2) |
| ⚠️ | slide 2 · note 2 | By raising the temperature $T$, we reveal small probabilities that show which classes look like others, such … | P3_p2_c04 | 0.76 | For example, one version of a 2 may be given a probability of 10−6 of being a 3 and 10−9 … (`P3_p2_c04`, p.2) |
| ⚠️ | slide 2 · note 3 | Once distillation training completes, we reset the temperature back to 1 for deployment. | P3_p3_c02 | 0.79 | The same high temperature is used when training the distilled model, but after it has bee… (`P3_p3_c02`, p.3) |
| ⚠️ | slide 3 · bullet 1 | Performance improves by jointly training on soft targets and correct true labels. | P3_p3_c02 | 0.75 | When the correct labels are known for all or some of the transfer set, this method can be… (`P3_p3_c02`, p.3) |
| ✅ | slide 3 · bullet 2 | The first objective uses cross-entropy with soft targets at a high temperature $T$. | P3_p3_c02 | 0.89 | The first objective function is the cross entropy with the soft targets and this cross en… (`P3_p3_c02`, p.3) |
| ✅ | slide 3 · bullet 3 | The second objective uses cross-entropy with correct labels at a temperature of 1. | P3_p3_c02 | 0.92 | The second objective function is the cross entropy with the correct labels. (`P3_p3_c02`, p.3) |
| ✅ | slide 3 · bullet 4 | Gradients from soft targets scale as $1/T^2$, so they are multiplied by $T^2$ when combining objectives. | P3_p3_c02 | 0.90 | We found that the best results were generally obtained by using a condiderably lower weig… (`P3_p3_c02`, p.3) |
| ⚠️ | slide 3 · note 1 | We utilize a weighted average of two different objective functions to leverage both teacher guidance and grou… | P3_p3_c02 | 0.77 | One way to do this is to use the correct labels to modify the soft targets, but we found … (`P3_p3_c02`, p.3) |
| ✅ | slide 3 · note 2 | A considerably lower weight is generally used on the second objective function involving the correct labels. | P3_p3_c02 | 0.85 | We found that the best results were generally obtained by using a condiderably lower weig… (`P3_p3_c02`, p.3) |
| ✅ | slide 3 · note 3 | Multiplying by $T^2$ ensures that the relative contributions of hard and soft targets remain constant when ex… | P3_p3_c02 | 0.83 | Since the magnitudes of the gradients produced by the soft targets scale as 1/T 2 it is i… (`P3_p3_c02`, p.3) |
| ✅ | slide 4 · bullet 1 | Each transfer case contributes a cross-entropy gradient with respect to each logit $z_i$. | P3_p3_c03 | 0.91 | Each case in the transfer set contributes a cross-entropy gradient, dC/dzi, with respect … (`P3_p3_c03`, p.3) |
| ✅ | slide 4 · bullet 2 | The general gradient equation links the distilled model probabilities $q_i$ and cumbersome probabilities $p_i… | P3_p3_c03 | 0.81 | If the cumbersome model has logits vi which produce soft target probabilities pi and the … (`P3_p3_c03`, p.3) |
| ⚠️ | slide 4 · bullet 3 | When the temperature is very high, the gradient expression can be cleanly approximated. | P3_p3_c03 | 0.80 | (2) If the temperature is high compared with the magnitude of the logits, we can approxim… (`P3_p3_c03`, p.3) |
| ✅ | slide 4 · bullet 4 | Assuming zero-meaned logits, matching logits becomes a direct mathematical special case of distillation. | P3_p3_c03 | 0.88 | Matching logits is a special case of distillation (`P3_p3_c03`, p.3) |
| ⚠️ | slide 4 · note 1 | The gradient of the cost function with respect to the logits is given by $\frac{\partial C}{\partial z_i} = \… | P3_p3_c03 | 0.79 | If the cumbersome model has logits vi which produce soft target probabilities pi and the … (`P3_p3_c03`, p.3) |
| ⚠️ | slide 4 · note 2 | When $T$ is high compared to logit magnitudes, we apply a first-order Taylor expansion approximation. | P3_p3_c03 | 0.79 | (2) If the temperature is high compared with the magnitude of the logits, we can approxim… (`P3_p3_c03`, p.3) |
| ⚠️ | slide 4 · note 3 | Minimizing the squared difference between logits, as explored by Caruana, emerges naturally as $\frac{1}{NT^2… | P3_p2_c04, P3_p3_c03 | 0.80 | Caruana and his collaborators circumvent this problem by using the logits (the inputs to … (`P3_p2_c04`, p.2) |
| ✅ | slide 5 · bullet 1 | We introduce a new ensemble type with a generalist model and multiple specialist models. | P3_p1_c02 | 0.89 | We also introduce a new type of ensemble composed of one or more full models and many spe… (`P3_p1_c02`, p.1) |
| ✅ | slide 5 · bullet 2 | Specialist models focus on learning to distinguish fine-grained classes that the full model confuses. | P3_p1_c02 | 0.87 | We also introduce a new type of ensemble composed of one or more full models and many spe… (`P3_p1_c02`, p.1) |
| ✅ | slide 5 · bullet 3 | We apply an on-line K-means algorithm to the covariance matrix of generalist predictions to find clusters. | P3_p6_c03 | 0.92 | In particular, we apply a clustering algorithm to the covariance matrix of the prediction… (`P3_p6_c03`, p.6) |
| ✅ | slide 5 · bullet 4 | Specialists train completely independently and extremely fast compared to massive base models. | P3_p7_c02 | 0.81 | Also, all the specialists are trained completely independently. (`P3_p7_c02`, p.7) |
| ⚠️ | slide 5 · note 1 | Specialists allow us to tackle enormous output spaces by specializing in subsets of confusable categories. | P3_p1_c02, P3_p6_c03 | 0.73 | In order to derive groupings of object categories for the specialists, we decided to focu… (`P3_p6_c03`, p.6) |
| ✅ | slide 5 · note 2 | Clustering is performed directly on the covariance matrix of the generalist predictions without requiring tru… | P3_p6_c03 | 0.87 | Even though we could have computed the confusion matrix and used it as a way to find such… (`P3_p6_c03`, p.6) |
| ⚠️ | slide 5 · note 3 | Each specialist trains independently in just a few days instead of weeks, making parallel training highly eff… | P3_p7_c02 | 0.79 | Starting from the trained baseline full network, the specialists train extremely fast (a … (`P3_p7_c02`, p.7) |
| ✅ | slide 6 · bullet 1 | Given an input image $x$, top-one classification is performed in two distinct steps. | P3_p6_c04 | 0.90 | Given an input image x, we do top-one classification in two steps: Step 1: For each test … (`P3_p6_c04`, p.6) |
| ✅ | slide 6 · bullet 2 | Step 1 finds the $n$ most probable classes according to the generalist model. | P3_p6_c04 | 0.84 | Given an input image x, we do top-one classification in two steps: Step 1: For each test … (`P3_p6_c04`, p.6) |
| ⚠️ | slide 6 · bullet 3 | Step 2 activates all specialist models whose confusable subset intersects with the generalist top classes. | P3_p6_c04 | 0.79 | Step 2: We then take all the specialist models, m, whose special subset of confusable cla… (`P3_p6_c04`, p.6) |
| ✅ | slide 6 · bullet 4 | The final distribution $q$ minimizes the KL divergence sum across the generalist and active specialists. | P3_p6_c04 | 0.87 | We then find the full probability distribution q over all the classes that minimizes: KL(… (`P3_p6_c04`, p.6) |
| ✅ | slide 6 · note 1 | During inference, we identify an active set of specialists $A_k$ whose target classes overlap with the genera… | P3_p6_c04 | 0.84 | Performing inference with ensembles of specialists (`P3_p6_c04`, p.6) |
| ✅ | slide 6 · note 2 | We then find the full probability distribution $q$ that minimizes the combined objective $KL(p_g, q) + \sum_{… | P3_p6_c04 | 0.88 | We then find the full probability distribution q over all the classes that minimizes: KL(… (`P3_p6_c04`, p.6) |
| ⚠️ | slide 6 · note 3 | Specialist probability distributions include a special dustbin class to absorb probabilities assigned to non-… | P3_p6_c04 | 0.76 | We then find the full probability distribution q over all the classes that minimizes: KL(… (`P3_p6_c04`, p.6) |
| ✅ | slide 7 · bullet 1 | More than 80% of the ensemble accuracy improvement transfers to distilled speech acoustic models. | P3_p5_c02 | 0.82 | More than 80% of the improvement in frame classification accuracy achieved by using an en… (`P3_p5_c02`, p.5) |
| ⚠️ | slide 7 · bullet 2 | On MNIST, soft targets successfully transfer generalization knowledge even without explicit translation data. | P3_p4_c01 | 0.78 | This shows that soft targets can transfer a great deal of knowledge to the distilled mode… (`P3_p4_c01`, p.4) |
| ✅ | slide 7 · bullet 3 | Using 61 specialist models yields a 4.4% relative improvement in overall test accuracy on the JFT dataset. | P3_p7_c02 | 0.90 | With 61 specialist models, there is a 4.4% relative improvement in test accuracy overall. (`P3_p7_c02`, p.7) |
| ✅ | slide 7 · bullet 4 | Distillation successfully compresses cumbersome ensembles into single models suitable for high-throughput dep… | P3_p1_c02, P3_p1_c03 | 0.80 | Once the cumbersome model has been trained, we can then use a different kind of training,… (`P3_p1_c03`, p.1) |
| ✅ | slide 7 · note 1 | Experiments confirm that distillation captures more useful information than training a single model from hard… | P3_p5_c02 | 0.87 | Table 1 shows that, indeed, our distillation approach is able to extract more useful info… (`P3_p5_c02`, p.5) |
| ❌ | slide 7 · note 2 | On the internal JFT dataset with 100 million images, accuracy improvements grow larger when more specialists …<br>_number(s) not in the cited source: 100_ | P3_p7_c02 | 0.80 | Table 4 shows the number of test set examples, the change in the number of examples corre… (`P3_p7_c02`, p.7) |
| ⚠️ | slide 7 · note 3 | Ultimately, knowledge distillation provides a powerful, practical bridge between high-capacity ensemble train… | P3_p1_c02, P3_p1_c03 | 0.76 | Once the cumbersome model has been trained, we can then use a different kind of training,… (`P3_p1_c03`, p.1) |
| ➖ | script | Now let's look at the motivation behind knowledge distillation.<br>_no valid citation (closest source: P3_p1_c03, similarity 0.77)_ | — | 0.00 | Once the cumbersome model has been trained, we can then use a different kind of training,… (`P3_p1_c03`, p.1) |
| ✅ | script | A simple way to improve the performance of almost any machine learning algorithm is to train many different m… | P3_p1_c02 | 0.99 | A very simple way to improve the performance of almost any machine learning algorithm is … (`P3_p1_c02`, p.1) |
| ✅ | script | Unfortunately, making predictions using a whole ensemble of models is cumbersome and may be too computational… | P3_p1_c02 | 1.00 | Unfortunately, making predictions using a whole ensemble of models is cumbersome and may … (`P3_p1_c02`, p.1) |
| ✅ | script | Drawing an analogy with insects that have a larval form optimized for feeding and an adult form optimized for… | P3_p1_c03 | 0.83 | Many insects have a larval form that is optimized for extracting energy and nutrients fro… (`P3_p1_c03`, p.1) |
| ✅ | script | We can also introduce a new type of ensemble composed of a generalist model and many specialist models which … | P3_p1_c02 | 0.96 | We also introduce a new type of ensemble composed of one or more full models and many spe… (`P3_p1_c02`, p.1) |
| ➖ | script | Now let's explore the distillation method itself.<br>_no valid citation (closest source: P3_p2_c04, similarity 0.75)_ | — | 0.00 | We show later that matching the logits of the cumbersome model is actually a special case… (`P3_p2_c04`, p.2) |
| ✅ | script | Neural networks typically produce class probabilities by using a softmax output layer that converts the logit… | P3_p2_c06 | 0.96 | Neural networks typically produce class probabilities by using a “softmax” output layer t… (`P3_p2_c06`, p.2) |
| ✅ | script | By raising the temperature $T$ of the final softmax, the cumbersome model produces a suitably soft set of tar… | P3_p2_c04 | 0.82 | For tasks like MNIST in which the cumbersome model almost always produces the correct ans… (`P3_p2_c04`, p.2) |
| ⚠️ | script | We then use that same high temperature when training the small model to match these soft targets. | P3_p3_c02 | 0.75 | The same high temperature is used when training the distilled model, but after it has bee… (`P3_p3_c02`, p.3) |
| ✅ | script | After the distilled model has been trained, it uses a temperature of 1 for standard predictions. | P3_p3_c02 | 0.89 | The same high temperature is used when training the distilled model, but after it has bee… (`P3_p3_c02`, p.3) |
| ✅ | script | Moving on to the objective function, we find that performance is significantly improved when we train the dis… | P3_p3_c02 | 0.86 | When the correct labels are known for all or some of the transfer set, this method can be… (`P3_p3_c02`, p.3) |
| ✅ | script | This is achieved by using a weighted average of two different objective functions, where the first uses cross… | P3_p3_c02 | 0.90 | One way to do this is to use the correct labels to modify the soft targets, but we found … (`P3_p3_c02`, p.3) |
| ✅ | script | Because the magnitudes of gradients produced by soft targets scale as $1/T^2$, we must multiply them by $T^2$… | P3_p3_c02 | 0.89 | Since the magnitudes of the gradients produced by the soft targets scale as 1/T 2 it is i… (`P3_p3_c02`, p.3) |
| ➖ | script | Next, let's examine how matching logits relates to distillation.<br>_no valid citation (closest source: P3_p3_c03, similarity 0.90)_ | — | 0.00 | Matching logits is a special case of distillation (`P3_p3_c03`, p.3) |
| ✅ | script | Each case in the transfer set contributes a cross-entropy gradient with respect to each logit $z_i$, which is… | P3_p3_c03 | 0.90 | Each case in the transfer set contributes a cross-entropy gradient, dC/dzi, with respect … (`P3_p3_c03`, p.3) |
| ✅ | script | When the temperature is high compared to the magnitude of the logits, this can be approximated as $\frac{\par… | P3_p3_c03 | 0.93 | (2) If the temperature is high compared with the magnitude of the logits, we can approxim… (`P3_p3_c03`, p.3) |
| ✅ | script | If we assume the logits have been zero-meaned separately for each transfer case, this equation simplifies nea… | P3_p2_c04, P3_p3_c03 | 0.89 | Matching logits is a special case of distillation (`P3_p3_c03`, p.3) |
| ➖ | script | Now let's turn to specialist models.<br>_no valid citation (closest source: P3_p6_c04, similarity 0.80)_ | — | 0.00 | Before investigating what happens when specialist models are distilled, we wanted to see … (`P3_p6_c04`, p.6) |
| ✅ | script | To handle large datasets, we combine a generalist model with specialist models that focus on confusable categ… | P3_p1_c02, P3_p6_c04 | 0.81 | We also introduce a new type of ensemble composed of one or more full models and many spe… (`P3_p1_c02`, p.1) |
| ✅ | script | We derive groupings by applying an online K-means clustering algorithm to the columns of the covariance matri… | P3_p6_c03 | 0.91 | We applied an on-line version of the K-means algorithm to the columns of the covariance m… (`P3_p6_c03`, p.6) |
| ✅ | script | Starting from the baseline network, all specialists are trained completely independently and extremely fast, … | P3_p7_c02 | 0.86 | Starting from the trained baseline full network, the specialists train extremely fast (a … (`P3_p7_c02`, p.7) |
| ✅ | script | To perform inference with ensembles of specialists, we execute a two-step process for each input image $x$. | P3_p6_c04 | 0.87 | Performing inference with ensembles of specialists (`P3_p6_c04`, p.6) |
| ✅ | script | First, we find the $n$ most probable classes according to the generalist model. | P3_p6_c04 | 0.81 | Given an input image x, we do top-one classification in two steps: Step 1: For each test … (`P3_p6_c04`, p.6) |
| ✅ | script | Second, we gather the active set of specialists whose confusable subset intersects with the generalist top cl… | P3_p6_c04 | 0.89 | Step 2: We then take all the specialist models, m, whose special subset of confusable cla… (`P3_p6_c04`, p.6) |
| ✅ | script | Finally, looking at the experimental results, our distillation approach successfully extracts more useful inf… | P3_p5_c02 | 0.89 | Table 1 shows that, indeed, our distillation approach is able to extract more useful info… (`P3_p5_c02`, p.5) |
| ✅ | script | More than 80% of the acoustic model improvement achieved by a 10-model ensemble is successfully transferred t… | P3_p5_c02 | 0.85 | More than 80% of the improvement in frame classification accuracy achieved by using an en… (`P3_p5_c02`, p.5) |
| ✅ | script | Furthermore, training with 61 specialist models on Google's internal JFT dataset results in a 4.4% relative i… | P3_p7_c02 | 0.86 | With 61 specialist models, there is a 4.4% relative improvement in test accuracy overall. (`P3_p7_c02`, p.7) |
| ⚠️ | script | These results demonstrate that knowledge distillation provides a robust and scalable solution for deploying h… | P3_p1_c02, P3_p1_c03 | 0.78 | Once the cumbersome model has been trained, we can then use a different kind of training,… (`P3_p1_c03`, p.1) |
