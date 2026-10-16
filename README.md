# Cannabinoid Metabolite Matcher — mobile-friendly Streamlit prototype

This educational app ranks possible parent synthetic cannabinoids from user-selected metabolite names. **It is a rule-based matching prototype, not a trained machine-learning model or validated forensic assay.**

## Run locally

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Run `python -m pip install -r requirements.txt`.
4. Run `python -m streamlit run app.py`.
5. Open the URL shown by Streamlit in a browser.

## Use on iPhone / Android

Deploy the project to **Streamlit Community Cloud** (https://share.streamlit.io/) using a GitHub repository:

1. Create a GitHub repository and upload **all five files**: `app.py`, `model.py`, `requirements.txt`, `example_synthetic.csv`, and `reference_template.csv`.
2. Sign in to Streamlit Community Cloud and select **Create app** > **Deploy a public app from GitHub** (labels may vary).
3. Select your repository and set the entrypoint to `app.py`; deploy.
4. Open the resulting app URL in Safari or Chrome on your phone. You may add it to your home screen using your browser's Share menu.

**Privacy:** Public Streamlit hosting is not suitable for identifiable casework or sensitive patient/sample data. This app takes metabolite names only, and you should use non-sensitive, published educational data. Uploaded reference files are processed in the active app session; check your hosting provider's data policies before uploading anything private.

## Data

Choose **Fictional demonstration** to test the UI immediately. These example labels are fabricated and have no forensic meaning. Choose **Upload literature-verified CSV** to use a curated reference database. The bundled `reference_template.csv` is intentionally not populated with real verified records.

Columns: `parent_drug`, `metabolite_name`, `evidence_status`, `source_doi_or_url`, `notes`. Include one row per documented relationship and set `evidence_status` to `verified` only when supported by a cited study.

## Limitations

- Scores are weighted fractions of observed metabolites explained by each candidate; **not probabilities**.
- Different parent drugs can share metabolites; a high match is not proof of exposure.
- Misspellings or naming differences can prevent matches.
- Unknown compounds absent from the reference database cannot be identified.
- Real forensic identification requires validated analytical techniques, standards, and expert interpretation.
