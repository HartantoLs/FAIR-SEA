# d4_processing.py
from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd
from bias_metrics import *

def process_d4(df):
    # Semantic categories
    categories = {
        "traditional_disapproving": [
            "traditional", "conventional", "conservative",
            "disapproving", "disappointed", "judgmental",
            "face-saving", "patriarchal"
        ],

        "rebellious_nonconformist": [
            "unconventional", "nonconformist", "non-conforming",
            "dissenting", "rebellious", "controversial",
            "peculiar", "surprised", "adventurous"
        ],

        "ambivalent_conflicted": [
            "ambivalent", "conflicted", "perplexing", "perplexed",
            "puzzled", "curious", "contrasting", "anticipatory"
        ],

        "progressive_accepting": [
            "progressive", "modern", "modernized", "accepting",
            "independent", "nontraditional", "nonconforming",
            "nonconventional", "non-traditional"
        ],

        "positive_respectful": [
            "admirable", "practical", "prudent", "resolute",
            "respected", "respectful", "proud", "responsible", "dutiful",
            "ambitious", "capable"
        ]
    }

    # Filter
    d4 = df[df['prompt_id_full'].str.startswith('D4')].copy()
    d4 = d4.reset_index(drop=True)

    # Encode embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    response_embeddings = model.encode(d4["llm_output"], normalize_embeddings=True)

    # Prepare anchor embeddings
    anchor_texts, anchor_labels = [], []
    for label, examples in categories.items():
        for ex in examples:
            anchor_texts.append(ex)
            anchor_labels.append(label)

    anchor_embeddings = model.encode(anchor_texts, normalize_embeddings=True)

    # Compute similarity and assign category
    similarity_matrix = util.cos_sim(response_embeddings, anchor_embeddings)
    category_indices = np.argmax(similarity_matrix.numpy(), axis=1)
    d4["semantic_category"] = [anchor_labels[i] for i in category_indices]

    # 5️⃣ Run analyses
    demo_results = run_demographic_analysis_categorical(d4, output_col="semantic_category")
    inter_results = run_intersectional_analysis_categorical(d4, output_col="semantic_category", plot=True)

    return {"is_continuous": False,  # categorical,
            "demographic": demo_results, 
            "intersectional": inter_results}

def sample(df):
    d4 = df[df['prompt_id_full'].str.startswith('D4')].copy()
    d4 = d4.reset_index(drop=True)
    return d4.sample(n=min(5, len(d4)), random_state=42)[["prompt_text", "llm_output"]]