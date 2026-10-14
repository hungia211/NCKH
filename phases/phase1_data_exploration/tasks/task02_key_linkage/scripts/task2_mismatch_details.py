"""Locate subject/admission disagreements found by Task 2, without corrections."""
import argparse
import json
from pathlib import Path
import pandas as pd

def main():
    ap=argparse.ArgumentParser();ap.add_argument('run_dir',type=Path);args=ap.parse_args()
    results=json.loads((args.run_dir/'results.json').read_text(encoding='utf-8'))
    paths={x['table']:Path(x['path']) for x in results['inputs']}
    a=pd.read_csv(paths['admissions'],usecols=['hadm_id','subject_id'])
    owners=a.set_index('hadm_id').subject_id
    found=[]; scanned=0
    for df in pd.read_csv(paths['labevents'],usecols=['labevent_id','hadm_id','subject_id','itemid'],chunksize=1000000):
        expected=df.hadm_id.map(owners)
        mask=df.hadm_id.notna()&expected.notna()&df.subject_id.notna()&df.subject_id.ne(expected)
        bad=df.loc[mask].copy()
        if len(bad):
            bad['admission_subject_id']=expected.loc[mask].astype('int64')
            bad['hadm_id']=bad.hadm_id.astype('int64');found.append(bad)
        scanned+=len(df)
        if scanned%20000000==0: print(f'Detail scan: {scanned:,}',flush=True)
    bad=pd.concat(found,ignore_index=True) if found else pd.DataFrame(columns=['labevent_id','hadm_id','subject_id','itemid','admission_subject_id'])
    expected_count=next(x['count'] for x in results['checks'] if x['table']=='labevents' and x['metric']=='subject_mismatch_to_admission')
    assert len(bad)==expected_count
    assert scanned==next(x['count'] for x in results['checks'] if x['table']=='labevents' and x['metric']=='rows')
    for entry in results['inputs']:
        stat=Path(entry['path']).stat();assert (stat.st_size,stat.st_mtime_ns)==(entry['bytes'],entry['mtime_ns'])
    bad.to_csv(args.run_dir/'lab_subject_mismatches.csv',index=False,encoding='utf-8-sig')
    summary=dict(rows=len(bad),affected_hadm_id=int(bad.hadm_id.nunique()),lab_subjects=int(bad.subject_id.nunique()),admission_subjects=int(bad.admission_subject_id.nunique()))
    (args.run_dir/'mismatch_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    print(summary,flush=True)

if __name__=='__main__':main()
