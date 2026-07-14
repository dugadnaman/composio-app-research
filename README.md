# Composio AI Product Ops Intern Take-Home: 100-App Buildability Research

This repository contains the autonomous research agent, findings dataset, pattern analysis, and the generated case study for evaluating the buildability of agent toolkits across 100 applications in 10 categories.

## Case Study Deliverable
The compiled case study is available locally at [docs/index.html](docs/index.html).

### Summary Takeaway
1. **Auth is Solved**: 85% of apps offer API keys, personal access tokens, or Basic Auth, and 62% support OAuth2.
2. **High Self-Serve Rate**: 80% of credentials are self-serve, meaning toolkits for most of the 100 apps are build-ready today.
3. **Outreach & Approvals Block Gated Apps**: For the remaining ~20% of apps, the primary blocker is access (e.g., admin approvals, paid enterprise plans, sales/partnership loops), not API surface quality.

---

## Repository Structure
```
composio-app-research/
├── agent/
│   ├── __init__.py
│   ├── llm.py              # Model-agnostic backend interface (Gemini & Claude support)
│   ├── research.py         # Multi-stage research pipeline (Draft -> Ground -> Confirm)
│   ├── verify.py           # Verification and human check metrics
│   ├── run.py              # Orchestrator to run research over apps.yaml
│   └── web.py              # Document fetching and BeautifulSoup cleaning helper
├── analysis/
│   ├── __init__.py
│   └── patterns.py         # Aggregates findings into pattern stats for docs/
├── data/
│   ├── findings.json       # All 100 app findings (resumable, cached dataset)
│   ├── patterns.json       # Aggregated stats and headlines
│   ├── seed.py             # Script to initialize seed data
│   ├── verification.json   # 23-app hand-checked sample accuracy metrics
│   └── verification_build.py # Builds the verification dataset
├── docs/
│   ├── index.html          # Self-contained case study page
│   └── build.py            # Site generator script (embeds JSONs into HTML template)
├── apps.yaml               # Original 100-app input list
├── requirements.txt        # Project dependencies
├── schema.py               # Pydantic schema enforcing controlled vocabs
└── README.md               # Run instructions & setup guide (this file)
```

---

## Agent Pipeline: Draft $\rightarrow$ Ground $\rightarrow$ Confirm
The research agent executes in three stages to guarantee high-fidelity data extraction:
1. **DRAFT**: The LLM analyzes the app from its internal knowledge to draft a structured profile containing categories, auth, access models, and proposes a single authoritative documentation URL.
2. **GROUND**: The orchestrator fetches the proposed documentation URL using `agent/web.py` (via HTTP request + BeautifulSoup HTML parser).
3. **CONFIRM**: The LLM reviews the fetched webpage content and the draft profile. It corrects any errors, self-rates confidence (low confidence triggers human-in-the-loop review), and records any changed fields.

---

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dugadnaman/composio-app-research.git
   cd composio-app-research
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys**:
   The default free backend is Gemini. Get a free API key from Google AI Studio.
   ```bash
   export LLM_BACKEND=gemini
   export GEMINI_API_KEY="your-gemini-api-key"
   ```

---

## Running the Agent & Rebuilding

### 1. Research Specific Apps
You can research a subset of apps to test the pipeline live (e.g., Shopify [ID 41], Notion [ID 71], Stripe [ID 81]):
```bash
python -m agent.run --ids 41,71,81
```

### 2. Research All Apps
Run the pipeline over all 100 apps. The orchestrator is **incremental and cached**; it writes findings to `data/findings.json` after every single app. If the run is interrupted, re-running the command resumes from where it left off:
```bash
python -m agent.run
```
*Note: Use the `--force` flag to overwrite existing entries.*

### 3. Rebuild Analysis, Verification, and HTML Page
After updating findings, rebuild the verification, pattern stats, and compile the final HTML file:
```bash
# 1. Update verification stats
python data/verification_build.py

# 2. Update pattern analyses
python analysis/patterns.py

# 3. Compile data into docs/index.html
python docs/build.py
```

---

## Deployment to GitHub Pages
To deploy the case study to GitHub Pages:
1. Ensure the code is pushed to your GitHub repository.
2. Go to **Settings** $\rightarrow$ **Pages** on your repository on GitHub.
3. Under **Build and deployment** $\rightarrow$ **Branch**:
   - Select `main`.
   - Select the `/docs` folder as the source directory instead of root `/`.
4. Save the configuration. GitHub will deploy `docs/index.html` as the root of your Pages site.
