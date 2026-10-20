Paper 3: "Distilling the Knowledge in a Neural Network"
Hinton, Vinyals, Dean (Google), 2015

1. PROBLEM (Abstract + Introduction, p.1)
   - Best accuracy often comes from an ENSEMBLE (many models averaged)
     or one huge model.
   - But these are too slow/expensive to deploy to many users.
   - Insect analogy (p.1): larva is built for eating, adult for travel ->
     training and deployment have different needs, so models can differ too.
   - Question: can we move the knowledge of a big "cumbersome" model into
     a small, fast one?

2. MAIN IDEA (Introduction p.2 + Section 2, p.2-3)
   - "Knowledge" = the mapping from inputs to outputs, not the weights.
   - Big model's probabilities for WRONG answers carry information:
     a BMW is rarely mistaken for a garbage truck, but that is still far
     more likely than mistaking it for a carrot (p.2).
   - Train the small model on these "soft targets" instead of only the
     hard 0/1 labels.
   - Temperature T in softmax (Eq. 1, p.2): higher T -> softer
     probabilities -> small differences become visible.
   - Use the same high T when training the small model, then T = 1 when
     using it.
   - Best: weighted mix of (a) soft-target loss and (b) normal loss on true
     labels; multiply the soft part by T^2 (p.3).
   - Matching logits (Caruana) is a special case at high T (Sec 2.1, p.3).

3. RESULT (Sections 3, 4, 6; Tables 1 & 5)
   - MNIST (p.3-4): big net 67 errors; small net alone 146 errors;
     small net trained with soft targets (T=20) 74 errors.
   - Never saw a "3" in training, yet gets 98.6% of test 3s right after a
     bias fix (p.4).
   - Speech recognition (Table 1, p.5): baseline 58.9% frame accuracy;
     10-model ensemble 61.1%; distilled single model 60.8% -> >80% of the
     ensemble's gain kept in ONE model. WER 10.9% -> 10.7%.
   - Only 3% of data (Table 5, p.8): hard targets 44.5% test accuracy
     (overfits) vs soft targets 57.0% (close to 58.9% with all data).
   - Specialist models on JFT (100M images, 15K classes): 61 specialists
     give 4.4% relative accuracy gain (Table 3, p.7).

4. WHY IT MATTERS (Discussion, Section 8, p.8)
   - Big model for training, small model for deployment.
   - Soft targets work as a strong regularizer (learn from less data).
   - Foundation of "knowledge distillation", now used to make smaller,
     faster versions of large models (e.g. DistilBERT).

5. HOOK IDEA (fill in your own)
   -

KEY EQUATIONS (for testing math preservation later)
   - Softmax with temperature (Eq. 1, p.2):
       q_i = exp(z_i / T) / sum_j exp(z_j / T)
   - Gradient (Eq. 2, p.3): dC/dz_i = (1/T)(q_i - p_i)
   - High-T approximation (Eq. 4, p.3): dC/dz_i ≈ (1/(N T^2)) (z_i - v_i)
