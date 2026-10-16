import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).with_name('reference_template.csv')

def load_reference(path=DATA):
    records = defaultdict(set)
    with open(path, newline='', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            parent = row['parent_drug'].strip()
            metabolite = row['metabolite_name'].strip()
            status = row['evidence_status'].strip().lower()
            if status != 'verified' or not parent or not metabolite:
                continue
            records[parent].add(metabolite.casefold())
    return dict(records)

def rank_candidates(observed, reference):
    observed = {x.strip().casefold() for x in observed if x.strip()}
    if not observed or not reference:
        return []
    prevalence = defaultdict(int)
    for metabolites in reference.values():
        for m in metabolites:
            prevalence[m] += 1
    n = len(reference)
    weights = {m: math.log((n + 1) / (count + 0.5)) + 1 for m, count in prevalence.items()}
    results = []
    for parent, known in reference.items():
        matched = observed & known
        if not matched:
            continue
        # Weighted fraction of observed markers explained by each parent.
        score = sum(weights[m] for m in matched) / sum(weights.get(m, 1) for m in observed)
        results.append({'parent': parent, 'score': score, 'matched': sorted(matched),
                        'unexplained': sorted(observed - known)})
    return sorted(results, key=lambda r: (-r['score'], -len(r['matched']), r['parent']))

def main():
    parser = argparse.ArgumentParser(description='Educational parent synthetic cannabinoid candidate ranking')
    parser.add_argument('--data', type=Path, default=DATA, help='CSV of literature-verified relationships')
    parser.add_argument('--metabolites', nargs='+', help='Observed metabolite names (quote multiword names)')
    args = parser.parse_args()
    reference = load_reference(args.data)
    if not reference:
        print('No VERIFIED parent–metabolite records. Fill the CSV with cited literature records first.')
        return
    observed = args.metabolites or [x.strip() for x in input('Enter metabolite names, separated by semicolons: ').split(';')]
    ranked = rank_candidates(observed, reference)
    if not ranked:
        print('No matching candidates in this limited reference database. This does NOT rule out exposure.')
        return
    print('\nCandidate ranking (heuristic match scores, NOT probabilities):')
    for i, item in enumerate(ranked[:5], 1):
        print(f"{i}. {item['parent']} | score {item['score']:.3f} | matched: {', '.join(item['matched'])}")
        if item['unexplained']:
            print('   Unexplained input:', ', '.join(item['unexplained']))
    print('\nEducational screening only. Confirm with reference standards and validated analytical methods.')

if __name__ == '__main__':
    main()
