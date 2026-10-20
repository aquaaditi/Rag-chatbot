"""
Day 1 checkpoint: can we talk to the LLM?

Run:  python hello_llm.py
"""

from src.llm import MODEL, ask_llm

print(f"Using model: {MODEL}\n")

# 1) A plain question - the model answers from its own memory (no retrieval yet)
answer = ask_llm("In 2 sentences, what is Retrieval-Augmented Generation (RAG)?")
print("Q1 (no context):\n", answer, "\n")

# 2) A tiny preview of RAG: we GIVE the model some text and tell it to use only that.
#    This is exactly what our chatbot will do later - except the text will come
#    from a retriever searching the uploaded paper.
context = (
    "[chunk P1_p2_c01] Our model achieves 91.2% accuracy on the test set, "
    "compared to 85.4% for the baseline."
)
answer = ask_llm(
    f"Context:\n{context}\n\nQuestion: How much better is the model than the baseline?",
    system_prompt=(
        "Answer ONLY using the given context. "
        "Cite the chunk ID in square brackets after your answer."
    ),
)
print("Q2 (with context - mini RAG!):\n", answer)
