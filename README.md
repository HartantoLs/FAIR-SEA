# FAIR-SEA: Fairness Assessment in Representation for Southeast Asia

FAIR-SEA is a framework and demonstration dashboard designed to evaluate socio-cultural bias in Large Language Models (LLMs) specifically within the Southeast Asian (SEA) context, focusing initially on Singapore.

## Background & Purpose

Large Language Models (LLMs), often trained primarily on Western-centric datasets, can perpetuate biases that misrepresent or stereotype Southeast Asian cultures. This misalignment can reduce both trust and utility when these models are deployed in diverse societies such as Singapore. Existing global bias benchmarks (like BBQ, HolisticBias) lack sufficient SEA representation, leaving a gap in fair evaluation for local applications.

Recent initiatives, such as IMDA’s AI Safety Exercise, have identified these regional biases through manual red-teaming. However, such methods are difficult to scale.

**FAIR-SEA seeks to address this challenge by providing:**

1.  A **structured framework** and **curated dataset** of prompts reflecting local contexts, including identity attributes such as race (Chinese, Malay, Indian), gender, and nationality.
2.  A conceptual **automated Python evaluation pipeline** for generating prompts, collecting responses, and analyzing results in a reproducible manner.
3.  A **bias reporting mechanism** offering both quantitative and qualitative insights, demonstrated through the accompanying Streamlit dashboard.

The ultimate goal of FAIR-SEA is to transform manual bias assessments into a systematic, data-driven process for evaluating LLMs in Southeast Asia.

---

## Framework Overview & Validation

Our methodology involves several key stages:

### 1. Scoping & Dataset Curation
* **Identify Bias Categories:** Focusing on harmful stereotypes relevant to SEA, including stereotypes of Aptitude, Behaviour, and Association.
* **Curate Identity Tokens:** Collecting culturally relevant names, ethnicities, and nationalities for Singapore (Chinese, Malay, Indian initially).
* **Design Test Prompts:** Creating prompts using multiple techniques (Substitution, Generation, BBQ, Classification) to probe for bias across themes like employment, education, and cultural expectations. Prompts utilize tokens to test for **intersectional bias** (e.g., assessing bias amplification when combining race and gender).

### 2. Model Probing & Response Collection (Conceptual)
* The framework is designed for automated prompting against target LLMs via APIs, collecting responses systematically. Reproducibility is key, using fixed parameters where possible.

### 3. Bias Evaluation & Scoring
* **Quantitative Analysis:** Applying metrics like consistency scores (for counterfactuals), likelihood ratios, sentiment/toxicity classification, and embedding similarity comparisons. Statistical tests (e.g., Chi-square, ANOVA) are used where appropriate based on prompt type.
* **Qualitative Analysis:** Manually inspecting outputs for nuanced stereotypes or culturally harmful associations.
* **Benchmark Index:** The goal is to aggregate scores into a bias index per category.

**Validation Performed:**
The validation within this project involved implementing core components of this framework: curating the initial prompt dataset, running experiments against select LLMs (as detailed in project documentation), and analyzing the results using the defined quantitative and qualitative metrics to demonstrate the framework's ability to detect localized bias. This Streamlit dashboard serves to illustrate these findings.

---

## Getting Started: Running the Dashboard Locally

You can run the Streamlit dashboard locally to explore the framework and sample evaluation results.

### 1. Installation Steps

* **Clone the Repository:**
    ```bash
    git clone [https://github.com/HartantoLs/fairsea.git](https://github.com/HartantoLs/fairsea.git)
    cd fairsea
    ```
* **Create & Activate Virtual Environment:**
    ```bash
    # Create the environment (use python3 on macOS/Linux if needed)
    python -m venv venv 
    
    # Activate (Command differs by OS)
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows (PowerShell/CMD):
    .\venv\Scripts\activate 
    ```
* **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
* **API Keys (Optional):** See the "Guide to Set Up API Key" section below if needed.

### 2. Example Command: Running the Dashboard

Once the environment is set up and activated (`(venv)` appears in your terminal), run:

```bash
streamlit run app.py

####
