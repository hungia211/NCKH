"""Small synthetic regression case for missing, orphan, mismatch and chunking."""
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import pandas as pd

def test_links():
    with tempfile.TemporaryDirectory() as temp:
        root=Path(temp); data=root/'data'; data.mkdir()
        tables={
            'patients':(['subject_id'],[['1'],['2']]),
            'admissions':(['hadm_id','subject_id'],[['10','1'],['11','1'],['20','2'],['21','2']]),
            'd_labitems':(['itemid'],[['5']]),
            'd_icd_diagnoses':(['icd_code','icd_version'],[['001','9']]),
            'diagnoses_icd':(['hadm_id','subject_id','icd_code','icd_version'],[['10','1','001','9'],['20','2','001','9']]),
            'labevents':(['hadm_id','subject_id','itemid'],[['10','1','5'],['10','1','5'],['11','1','5'],['','1','5'],['99','1','5'],['10','2','5'],['10','','5'],['','99','9']])}
        for name,(cols,rows) in tables.items():
            pd.DataFrame(rows,columns=cols).to_csv(data/f'{name}.csv.gz',index=False)
        script = Path(__file__).resolve().parents[1] / 'scripts' / 'task2_links.py'
        subprocess.run([sys.executable,str(script),'--data-dir',str(data),'--output-dir',str(root/'out'),'--chunksize','2'],check=True)
        result=json.loads((root/'out/results.json').read_text())
        c={(x['table'],x['metric']):x['count'] for x in result['checks']}
        for metric,expected in [('missing_hadm_id',2),('hadm_orphan',1),('subject_mismatch_to_admission',1),('known_hadm_missing_subject',1),('matched_admission_and_subject',3),('dictionary_orphan',1)]:
            assert c['labevents',metric]==expected,(metric,c['labevents',metric])
        assert c['diagnoses_icd','dictionary_orphan']==0,'Leading zero ICD lost'
        assert {x['group']:x['admissions'] for x in result['overlap']}==dict(both=1,lab_only=1,diagnosis_only=1,neither=1)
        assert result['projected_raw_lab_diagnosis_join_rows']==2
        # Stop before events if a dictionary key is ambiguous.
        pd.DataFrame([['5'],['5']],columns=['itemid']).to_csv(data/'d_labitems.csv.gz',index=False)
        bad=subprocess.run([sys.executable,str(script),'--data-dir',str(data),'--output-dir',str(root/'bad')],capture_output=True,text=True)
        assert bad.returncode!=0 and 'Reference keys missing/duplicated' in bad.stderr
        print('PASS: missing/orphan/mismatch, four overlap groups, chunk totals, ICD leading zero, duplicate dictionary gate')

if __name__=='__main__':test_links()
