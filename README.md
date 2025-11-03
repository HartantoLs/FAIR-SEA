# FAIR-SEA: Fairness Assessment in Representation for Southeast Asia

**Live Demo:** [fairsea.streamlit.app](https://fairsea.streamlit.app)

FAIR-SEA is a comprehensive framework and interactive dashboard designed to evaluate socio-cultural bias in Large Language Models (LLMs) specifically within the Southeast Asian context, with an initial focus on Singapore's multicultural society.

---

## Table of Contents
- [Background & Purpose](#background--purpose)
- [What FAIR-SEA Provides](#what-fair-sea-provides)
- [Framework Overview](#framework-overview)
- [Validation Approach](#validation-approach)
- [Using the Dashboard](#using-the-dashboard)
- [Running Locally](#running-locally)
---

## Background & Purpose

Large Language Models (LLMs), predominantly trained on Western-centric datasets, can perpetuate biases that misrepresent or stereotype Southeast Asian cultures. This misalignment reduces both trust and utility when these models are deployed in diverse societies like Singapore.

**The Challenge:**
- Existing global bias benchmarks (BBQ, HolisticBias) lack sufficient SEA representation
- Manual red-teaming efforts (e.g., IMDA's AI Safety Exercise) are difficult to scale
- Regional biases remain largely unmeasured and unaddressed

**FAIR-SEA's Solution:**
Transform manual bias assessments into a systematic, data-driven, and reproducible evaluation process for LLMs deployed in Southeast Asia.

---

## What FAIR-SEA Provides

### 1. Structured Framework
- Curated dataset of prompts reflecting local contexts
- Identity attributes: race (Chinese, Malay, Indian), gender, nationality
- Multiple testing techniques: Substitution, Generation, BBQ, Classification

### 2. Automated Pipeline
- Python-based evaluation workflow
- Systematic prompt generation and response collection
- Reproducible analysis with fixed parameters

### 3. Comprehensive Reporting
- Interactive Streamlit dashboard for visualization
- Quantitative metrics (Chi-square, ANOVA, sentiment analysis)
- Qualitative insights through manual inspection
- Intersectional bias detection

---

## Framework Overview

### Stage 1: Scoping & Dataset Curation
**Bias Categories:**
- **Aptitude Stereotypes:** Assumptions about innate abilities based on demographics
- **Behavioral Stereotypes:** Expected behaviors tied to identity
- **Association Stereotypes:** Problematic correlations between groups and attributes

**Identity Tokens:**
- Names culturally representative of Singapore's major ethnic groups
- Gender markers (Male, Female)
- Nationality indicators (Singaporean, Malaysian, Indonesian, etc.)

**Prompt Design:**
Prompts are crafted across multiple domains:
- Employment & hiring decisions
- Educational aptitude assessments
- Customer service interactions
- Cultural expectations & family dynamics

### Stage 2: Model Probing & Response Collection
- Automated API-based prompting
- Systematic response logging
- Version control for reproducibility
- Multiple model comparison capability

### Stage 3: Bias Evaluation & Scoring

**Quantitative Metrics:**
- **Demographic Bias Index (DBI):** Standardized measure of bias intensity
- **Fairness Deviation Index (FDI):** Deviation from expected fair distribution
- **Jensen-Shannon Divergence (JSD):** Statistical distance between distributions
- **Chi-square tests:** Independence testing for categorical outcomes
- **ANOVA:** Variance analysis for continuous outcomes
- **Sentiment Analysis:** Polarity and emotional tone classification

**Qualitative Analysis:**
- Manual review of nuanced stereotypes
- Cultural sensitivity assessment
- Context-specific harm evaluation

---

## Validation Approach

### Validation Performed
This project implements and validates the FAIR-SEA framework through:

1. **Dataset Curation:**
   - 8 distinct analysis types (D1-D4, I1-I4)
   - 500+ curated prompts with identity token variations
   - Ground truth data for comparative analysis (I1, I2)

2. **Model Testing:**
   - Experiments conducted on multiple LLMs (GPT-4, GPT-3.5, etc.)
   - Systematic variation of identity attributes
   - Response collection with consistent parameters

3. **Statistical Analysis:**
   - Implementation of all quantitative metrics
   - Intersectional bias detection across Race × Gender × Nationality
   - Visualization of bias patterns through heatmaps and charts

4. **Dashboard Development:**
   - Interactive interface for exploring results
   - Real-time analysis capability
   - Export functionality for further research

### Key Findings Demonstrated
The validation successfully demonstrates the framework's ability to:
- Detect statistically significant bias patterns
- Identify intersectional amplification effects
- Compare model outputs against ground truth
- Provide actionable insights for model improvement

---

## Using the Dashboard

### Accessing the Live Demo
Visit **[fairsea.streamlit.app](https://fairsea.streamlit.app)** to explore the dashboard immediately—no installation required!

### Dashboard Features

#### 1. Home Page
- Overview of the FAIR-SEA framework
- Quick navigation to analysis tools
- Background on methodology and purpose

#### 2. Analysis Dashboard

**Step 1: Choose Your Data Source**
- **Demo Data:** Pre-loaded dataset with sample LLM outputs
  - Ready to explore immediately
  - Covers all 8 analysis types
  - Includes multiple demographic combinations

- **Upload Custom CSV:** Analyze your own LLM outputs
  - Required columns:
    - `Gender`: Male, Female, etc.
    - `Race`: Chinese, Malay, Indian, etc.
    - `Nationality`: Singaporean, Malaysian, etc.
    - `prompt_text`: The prompt sent to the LLM
    - `prompt_id_full`: Format `[AnalysisType]-[Nationality]-[Race]-[Gender]-[Name]-[Number]`
    - `llm_output`: The LLM's response
    - `model`: Model name (e.g., gpt-4o-mini)

**Step 2: Select Analysis Type**
Choose from 8 specialized bias analyses:

**Direct Bias Tests (D1-D4):**
- **D1:** Leadership Style Perception
- **D2:** Aptitude & Suitability Assessment
- **D3:** Tone Interpretation Bias
- **D4:** Cultural & Career Choice Perception

**Indirect Bias Tests (I1-I4):**
- **I1:** Occupation Prediction Bias
- **I2:** Industry Classification Bias
- **I3:** Scholarship Decision Bias
- **I4:** Workplace Professionalism Perception

**Step 3: Run Analysis**
Click "Run Analysis" to generate:
- Summary statistics across demographic groups
- Statistical significance tests (Chi-square, ANOVA)
- Bias indices (DBI, FDI, JSD)
- Interactive visualizations
- Intersectional bias analysis

**Step 4: Interpret Results**
Navigate through tabs to explore:
- **By Gender:** Gender-specific bias patterns
- **By Race:** Racial bias distributions
- **By Nationality:** National origin bias
- **Intersectional:** Combined effects across multiple attributes

#### 3. About Page
- Detailed framework explanation
- Methodology documentation
- Validation approach
- Research background

### Tips for Best Results
1. **Start with Demo Data:** Familiarize yourself with the interface and metrics
2. **Review Analysis Descriptions:** Each analysis type has specific use cases
3. **Check Statistical Significance:** p-values < 0.05 indicate significant bias
4. **Compare Across Demographics:** Look for disproportionate impacts
5. **Examine Intersectional Results:** Bias often amplifies at intersections

---

## Running Locally

For development or offline analysis, you can run FAIR-SEA on your local machine.

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Installation Steps

**1. Clone the Repository:**
```bash
git clone https://github.com/HartantoLs/fairsea.git
cd fairsea
```

**2. Create Virtual Environment:**
```bash
# Create environment
python -m venv venv

# Activate environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\activate
# On Windows (CMD):
.\venv\Scripts\activate.bat
```

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run the Dashboard:**
```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`
