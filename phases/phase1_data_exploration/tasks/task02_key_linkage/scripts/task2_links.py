"""Audit HOSP relational keys without modifying or filtering source files."""
import argparse
import hashlib
import json
import platform
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / 'AGENTS.md').is_file()
)
TASK_DIR = Path(__file__).resolve().parents[1]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-dir', type=Path, default=ROOT/'data/hosp')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--chunksize', type=int, default=500000)
    args = parser.parse_args()
    start = datetime.now(timezone.utc)
    out = args.output_dir or TASK_DIR/'outputs'/start.strftime('%Y%m%dT%H%M%SZ')
    out.mkdir(parents=True, exist_ok=False)
    checks=[]; refs={}; manifest=[]
    def check(table, metric, count, denominator, unit='rows'):
        checks.append(dict(table=table, metric=metric, count=int(count), denominator=int(denominator), unit=unit))
    def read(table, cols):
        path=args.data_dir/f'{table}.csv.gz'
        stat=path.stat()
        manifest.append(dict(table=table,path=str(path.resolve()),bytes=stat.st_size,mtime_ns=stat.st_mtime_ns))
        return pd.read_csv(path,usecols=cols,dtype=str,keep_default_na=False)
    definitions={'patients':['subject_id'],'admissions':['hadm_id','subject_id'],
                 'd_labitems':['itemid'],'d_icd_diagnoses':['icd_code','icd_version']}
    for table,cols in definitions.items():
        df=read(table,cols); keys=cols if table=='d_icd_diagnoses' else [cols[0]]
        missing=df[keys].eq('').any(axis=1)
        check(table,'missing_key',missing.sum(),len(df))
        check(table,'duplicate_key_excess_rows',df.duplicated(keys).sum(),len(df))
        check(table,'distinct_complete_keys',len(df.loc[~missing,keys].drop_duplicates()),len(df),'keys')
        refs[table]=df
    pd.DataFrame(checks).to_csv(out/'key_checks.csv',index=False,encoding='utf-8-sig')
    if any(c['count'] for c in checks if c['metric'] in ['missing_key','duplicate_key_excess_rows']):
        raise ValueError('Reference keys missing/duplicated: inspect key_checks.csv before joins.')
    patients=set(refs['patients'].subject_id)
    adm=refs['admissions']; owners=adm.set_index('hadm_id').subject_id
    check('admissions','missing_subject_id',adm.subject_id.eq('').sum(),len(adm))
    check('admissions','subject_orphan',((adm.subject_id!='')&~adm.subject_id.isin(patients)).sum(),len(adm))
    repeat=adm.groupby('subject_id').size()
    repeat.value_counts().sort_index().rename_axis('admissions_per_patient').reset_index(name='patients').to_csv(out/'admissions_per_patient.csv',index=False,encoding='utf-8-sig')
    check('admissions','patients_with_multiple_admissions',(repeat>1).sum(),len(repeat),'patients')
    check('admissions','max_admissions_per_patient',repeat.max(),len(repeat),'admissions')
    coverage={}; metadata={}
    for table in ['diagnoses_icd','labevents']:
        cols=['subject_id','hadm_id']+(['itemid'] if table=='labevents' else ['icd_code','icd_version'])
        path=args.data_dir/f'{table}.csv.gz'; stat=path.stat()
        manifest.append(dict(table=table,path=str(path.resolve()),bytes=stat.st_size,mtime_ns=stat.st_mtime_ns))
        totals=Counter(); linked_counts=Counter(); present=set(); missing_subjects=set(); valid_subjects=set()
        dictionary=set(refs['d_labitems'].itemid) if table=='labevents' else pd.MultiIndex.from_frame(refs['d_icd_diagnoses'][['icd_code','icd_version']])
        for n,df in enumerate(pd.read_csv(path,usecols=cols,dtype=str,keep_default_na=False,chunksize=args.chunksize),1):
            totals['rows']+=len(df)
            sh=df.subject_id.eq(''); mh=df.hadm_id.eq(''); mapped=df.hadm_id.map(owners)
            orphan=(~mh)&mapped.isna(); match=(~mh)&mapped.notna()&(~sh)&df.subject_id.eq(mapped)
            mismatch=(~mh)&mapped.notna()&(~sh)&~df.subject_id.eq(mapped)
            masks={'missing_subject_id':sh,'subject_orphan':(~sh)&~df.subject_id.isin(patients),
                   'missing_hadm_id':mh,'hadm_orphan':orphan,'subject_mismatch_to_admission':mismatch,
                   'known_hadm_missing_subject':(~mh)&mapped.notna()&sh,'matched_admission_and_subject':match}
            if table=='labevents':
                dk=df.itemid.eq(''); do=(~dk)&~df.itemid.isin(dictionary)
            else:
                dk=df[['icd_code','icd_version']].eq('').any(axis=1)
                do=(~dk)&~pd.MultiIndex.from_frame(df[['icd_code','icd_version']]).isin(dictionary)
            masks.update(dictionary_key_missing=dk,dictionary_orphan=do)
            for metric,mask in masks.items(): totals[metric]+=int(mask.sum())
            linked_counts.update(df.loc[match].groupby('hadm_id').size().to_dict())
            present.update(df.loc[~mh,'hadm_id'].unique())
            missing_subjects.update(df.loc[mh&~sh,'subject_id'].unique())
            valid_subjects.update(df.loc[match,'subject_id'].unique())
            if n%10==0: print(f'{table}: {totals["rows"]:,} rows',flush=True)
        assert totals['rows']==sum(totals[x] for x in ['missing_hadm_id','hadm_orphan','subject_mismatch_to_admission','known_hadm_missing_subject','matched_admission_and_subject'])
        for metric,count in totals.items(): check(table,metric,count,totals['rows'])
        check(table,'unique_nonmissing_hadm_id',len(present),totals['rows'],'admissions')
        check(table,'unique_matched_hadm_id',len(linked_counts),len(adm),'admissions')
        check(table,'patients_in_missing_hadm_rows',len(missing_subjects),len(patients),'patients')
        check(table,'patients_in_missing_hadm_rows_with_any_admission',len(missing_subjects & set(adm.subject_id)),len(missing_subjects),'patients')
        coverage[table]=linked_counts
        metadata[table]={'rows':totals['rows'],'valid_subjects':len(valid_subjects)}
        print(f'{table}: finished {totals["rows"]:,}',flush=True)
    counts=adm.copy()
    counts['lab_rows']=counts.hadm_id.map(coverage['labevents']).fillna(0).astype('int64')
    counts['diagnosis_rows']=counts.hadm_id.map(coverage['diagnoses_icd']).fillna(0).astype('int64')
    groups=[]
    for label,lab,diag in [('both',True,True),('lab_only',True,False),('diagnosis_only',False,True),('neither',False,False)]:
        subset=counts.loc[(counts.lab_rows.gt(0)==lab)&(counts.diagnosis_rows.gt(0)==diag)]
        groups.append(dict(group=label,admissions=len(subset),patients=subset.subject_id.nunique(),share=len(subset)/len(adm),lab_rows=int(subset.lab_rows.sum()),diagnosis_rows=int(subset.diagnosis_rows.sum())))
    assert sum(g['admissions'] for g in groups)==len(adm)
    pd.DataFrame(groups).to_csv(out/'admission_overlap.csv',index=False,encoding='utf-8-sig')
    pd.DataFrame(checks).to_csv(out/'key_checks.csv',index=False,encoding='utf-8-sig')
    # Counts only: do not materialize the many-to-many joined event table.
    projected=sum(int(a)*int(b) for a,b in zip(counts.lab_rows,counts.diagnosis_rows))
    for entry in manifest:
        stat=Path(entry['path']).stat()
        assert (stat.st_size,stat.st_mtime_ns)==(entry['bytes'],entry['mtime_ns']), 'Input changed during scan'
    result=dict(started_utc=start.isoformat(),finished_utc=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(),pandas=pd.__version__,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        inputs=manifest,checks=checks,overlap=groups,projected_raw_lab_diagnosis_join_rows=projected,
        rules=['No cohort filters or time window','Overlap requires hadm_id and subject_id agreement',
               'Empty CSV field is missing; no normalization of ICD strings',
               'Orphans exclude missing keys','Patient totals across overlap groups are not additive'],
        source_rows_removed=0)
    (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('OUTPUT',out,flush=True)

if __name__=='__main__': main()
