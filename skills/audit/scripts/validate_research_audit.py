#!/usr/bin/env python3
"""Validate research audit schema and exact quotes before writing a report."""
from __future__ import annotations
import argparse,json,re,sys
from pathlib import Path
CHECKS={f'RC{i:02d}' for i in range(1,11)}; STAT={'found','not_found','not_assessable','not_applicable'}; SEV={'critical','major','moderate','minor'}; FSTAT={'confirmed','likely','potential'}; CONF={'high','medium','low'}
def norm(s):return re.sub(r'\s+',' ',s.replace('**','').replace('`','')).strip()
def quote_line(quote,lines):
 q=norm(quote)
 if len(q)<8:return None
 clean=[norm(re.sub(r'^L\d{5}\|\s?','',x)) for x in lines]
 for i,line in enumerate(clean):
  if q in line:return i+1
 for i in range(len(clean)):
  win=norm(' '.join(clean[i:i+6]));pos=win.find(q)
  if 0<=pos<len(clean[i]):return i+1
 return None
def validate(ws,a):
 errors=[];mp=ws/'manuscript.md';sp=ws/'sections.json'
 if not mp.is_file() or not sp.is_file():return ['Workspace requires manuscript.md and sections.json'],[]
 lines=mp.read_text(encoding='utf-8').splitlines();sections=json.loads(sp.read_text(encoding='utf-8'));checks=a.get('checks',{})
 if not isinstance(checks,dict):return ["'checks' must be an object"],[]
 if CHECKS-set(checks):errors.append('Missing checks: '+', '.join(sorted(CHECKS-set(checks))))
 if set(checks)-CHECKS:errors.append('Unknown checks: '+', '.join(sorted(set(checks)-CHECKS)))
 findings=a.get('findings',[]);ids=set();counts={};valid=[]
 if not isinstance(findings,list):return ["'findings' must be a list"],[]
 for i,f in enumerate(findings,1):
  fid=f.get('id',f'#{i}')
  if fid in ids:errors.append(f'{fid}: duplicate ID')
  ids.add(fid)
  for k in ('id','check','title','severity','status','confidence','location','quote','problem','impact','recommendation'):
   if not f.get(k):errors.append(f'{fid}: missing {k}')
  ck=f.get('check')
  if ck not in CHECKS:errors.append(f'{fid}: invalid check {ck}');continue
  counts[ck]=counts.get(ck,0)+1
  if f.get('severity') not in SEV:errors.append(f'{fid}: invalid severity')
  if f.get('status') not in FSTAT:errors.append(f'{fid}: invalid finding status')
  if f.get('confidence') not in CONF:errors.append(f'{fid}: invalid confidence')
  if f.get('severity')=='critical' and not(f.get('status')=='confirmed' and f.get('confidence')=='high'):errors.append(f'{fid}: critical requires confirmed + high')
  if f.get('severity')=='major' and f.get('status')=='potential':errors.append(f'{fid}: potential cannot be major')
  loc=f.get('location') or {};line=quote_line(str(f.get('quote','')),lines)
  if line is None:errors.append(f'{fid}: quote not found verbatim in manuscript.md');continue
  section=next((s['title'] for s in reversed(sections) if s['start']<=line<=s['end']),'(heading unknown)')
  valid.append({**f,'location':{'file':'manuscript.md','line':line,'section':section}})
 for ck in CHECKS & set(checks):
  c=checks[ck]
  if c.get('status') not in STAT:errors.append(f'{ck}: invalid status')
  if c.get('status') in ('found','not_found') and c.get('coverage') not in ('full','partial','limited'):errors.append(f'{ck}: coverage missing/invalid')
  if not c.get('basis'):errors.append(f'{ck}: basis required')
  if c.get('status')=='not_assessable' and not c.get('missing'):errors.append(f'{ck}: not_assessable needs missing input')
  if c.get('status')=='found' and not counts.get(ck):errors.append(f'{ck}: found without valid finding')
  if c.get('status')!='found' and counts.get(ck):errors.append(f'{ck}: finding exists but status is not found')
 if not a.get('summary'):errors.append('summary required')
 return errors,valid
def report(a,fs):
 rank={'critical':0,'major':1,'moderate':2,'minor':3};fs=sorted(fs,key=lambda f:(rank[f['severity']],f['location']['line']))
 out=['# Research Coherence Audit Report','',f"**Level:** {a.get('level','unspecified')}  ",f"**Research type:** {a.get('research_type','not classified')}",'','## Summary','',a['summary'],'','## Check status','','| ID | Status | Coverage | Basis |','|---|---|---|---|']
 for ck,c in sorted(a['checks'].items()):
  basis=str(c.get('basis','')).replace('|','\\|');out.append(f"| {ck} | {c.get('status')} | {c.get('coverage','—')} | {basis} |")
 out+=['','## Findings','']
 if not fs:out.append('No validated findings.')
 for f in fs:
  l=f['location'];out += [f"### {f['id']} — {f['title']}",f"- **Severity/status/confidence:** {f['severity']} / {f['status']} / {f['confidence']}",f"- **Location:** {l['file']} line {l['line']} — {l['section']}",f"> {f['quote']}",f"- **Problem:** {f['problem']}",f"- **Impact:** {f['impact']}",f"- **Recommendation:** {f['recommendation']}"]
  if f.get('evidence_needed'):out.append('- **Additional evidence:** '+f['evidence_needed'])
  out.append('')
 out+=['## Audit limits','','This report covers only the files and evidence available. The validator checks structure and quotes, not academic correctness. An AI audit is not a substitute for a supervisor, examiner, subject expert, or re-analysis of the data.']
 return '\n'.join(out)+'\n'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('workspace',type=Path);p.add_argument('--audit',type=Path);a=p.parse_args();ws=a.workspace.resolve();ap=a.audit or ws/'audit.json'
 try:data=json.loads(ap.read_text(encoding='utf-8'));errors,fs=validate(ws,data)
 except Exception as e:print('ERROR:',e,file=sys.stderr);return 2
 if errors:
  print(f'INVALID: {len(errors)} issue(s); no report written.')
  for e in errors:print('-',e)
  return 1
 out=ws/'audit-report.md';out.write_text(report(data,fs),encoding='utf-8');print(f'OK: report written to {out}');return 0
if __name__=='__main__':raise SystemExit(main())
