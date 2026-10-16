import csv
import io
from collections import defaultdict
import streamlit as st
from model import rank_candidates

st.set_page_config(page_title='Cannabinoid Metabolite Matcher', page_icon='🧪', layout='centered')
st.title('🧪 Cannabinoid Metabolite Matcher')
st.caption('Educational candidate-ranking tool • Not a validated forensic identification system')
st.warning('Matches are heuristic scores, NOT probabilities. Shared metabolites, incomplete reference data, and spelling differences can cause ambiguity. Confirm using validated laboratory methods.')

@st.cache_data
def bundled_csv(filename):
    from pathlib import Path
    return Path(__file__).with_name(filename).read_text(encoding='utf-8-sig')

def parse_reference(csv_text):
    records = defaultdict(set)
    rows = csv.DictReader(io.StringIO(csv_text))
    required = {'parent_drug', 'metabolite_name', 'evidence_status'}
    if not rows.fieldnames or not required.issubset(rows.fieldnames):
        raise ValueError('CSV must contain parent_drug, metabolite_name, evidence_status columns.')
    verified_count = 0
    for row in rows:
        if (row.get('evidence_status') or '').strip().casefold() != 'verified':
            continue
        parent = (row.get('parent_drug') or '').strip()
        metabolite = (row.get('metabolite_name') or '').strip()
        if parent and metabolite:
            records[parent].add(metabolite.casefold())
            verified_count += 1
    return dict(records), verified_count

mode = st.radio('Reference data', ['Fictional demonstration', 'Upload literature-verified CSV', 'Bundled reference template'], horizontal=False)
if mode == 'Fictional demonstration':
    csv_text = bundled_csv('example_synthetic.csv')
    st.info('DEMO MODE: All compound names and metabolite markers are fictional.')
elif mode == 'Upload literature-verified CSV':
    uploaded = st.file_uploader('Upload CSV reference database', type=['csv'])
    if not uploaded:
        st.stop()
    csv_text = uploaded.getvalue().decode('utf-8-sig')
else:
    csv_text = bundled_csv('reference_template.csv')

try:
    reference, count = parse_reference(csv_text)
except (ValueError, UnicodeDecodeError, csv.Error) as exc:
    st.error(f'Could not read reference file: {exc}')
    st.stop()

st.caption(f'{len(reference)} parent candidates • {count} verified relationship rows')
if not reference:
    st.info('No verified records yet. Upload a completed CSV or select Fictional demonstration.')
    st.stop()

all_markers = sorted(set().union(*reference.values()))
chosen = st.multiselect('Select detected metabolites', all_markers, default=[], help='Names must match the reference database. Select multiple metabolites if detected.')
other = st.text_input('Optional additional metabolite names (semicolon-separated)', placeholder='e.g., unknown_marker')
observed = list(chosen) + [m.strip() for m in other.split(';') if m.strip()]
if st.button('Rank possible parent cannabinoids', type='primary', use_container_width=True):
    if not observed:
        st.error('Select or enter at least one metabolite.')
    else:
        results = rank_candidates(observed, reference)
        if not results:
            st.warning('No matching candidates in this reference database. This does not exclude exposure.')
        else:
            st.subheader('Candidate ranking')
            if len(results) > 1 and abs(results[0]['score'] - results[1]['score']) < 1e-12:
                st.warning('Top candidates are tied: these observations do not distinguish them.')
            for i, item in enumerate(results[:10], 1):
                with st.container(border=True):
                    st.markdown(f"**{i}. {item['parent']}**")
                    st.progress(max(0.0, min(1.0, item['score'])))
                    st.caption(f"Heuristic match score: {item['score']:.3f} (not a probability)")
                    st.write('Matching:', ', '.join(item['matched']))
                    if item['unexplained']:
                        st.write('Not explained:', ', '.join(item['unexplained']))
            st.caption('A candidate with a high score is not a confirmed identity. Results are limited to the uploaded reference records.')

with st.expander('CSV format and scientific limitations'):
    st.code('parent_drug,metabolite_name,evidence_status,source_doi_or_url,notes\nDRUG_NAME,METABOLITE_NAME,verified,https://doi.org/...,literature evidence', language='csv')
    st.write('Use one row per documented parent–metabolite pair. Keep evidence sources. Only verified rows are used. This tool does not analyze mass spectra, infer molecular structures, or perform trained machine learning.')
    st.download_button('Download blank reference template', bundled_csv('reference_template.csv'), file_name='reference_template.csv', mime='text/csv')
