#!/usr/bin/env python3
"""Prepare a traceable audit workspace from Markdown or DOCX (standard library only)."""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
W="{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MAX_BYTES=50*1024*1024
PATTERNS={
 "problem":r"rumusan masalah|research question|problem statement|identifikasi masalah",
 "objective":r"tujuan penelitian|research objective|objectives of the study",
 "hypothesis":r"hipotesis|hypotheses|hypothesis",
 "literature":r"tinjauan pustaka|kajian pustaka|penelitian terdahulu|literature review|related work",
 "theory":r"landasan teori|kerangka teori|theoretical framework",
 "concepts":r"kerangka pemikiran|kerangka konseptual|variabel penelitian|operasional variabel",
 "method":r"metodologi penelitian|metode penelitian|methodology|research methods",
 "population":r"populasi dan sampel|populasi|sampel|informan|responden|participants",
 "instrument":r"instrumen penelitian|kuesioner|questionnaire|pedoman wawancara",
 "analysis":r"teknik analisis data|analisis data|data analysis",
 "results":r"hasil penelitian|hasil dan pembahasan|results|findings",
 "discussion":r"pembahasan|discussion",
 "conclusion":r"kesimpulan|simpulan|conclusion",
}
LIST=re.compile(r"^\s*(?:[-*+]\s+|\d{1,3}[.)]\s+|[•▪]\s+)(.+?)\s*$")
NUM=re.compile(r"^\s*(\d+(?:\.\d+){1,3})\s+(.{3,100})$")
class PrepError(Exception): pass
def text_docx(path):
 try:
  with zipfile.ZipFile(path) as z: root=ET.fromstring(z.read('word/document.xml'))
 except Exception as e: raise PrepError(f"DOCX cannot be read: {e}")
 body=root.find(W+'body'); out=[]
 if body is None: raise PrepError('DOCX body not found')
 for el in body:
  if el.tag==W+'p':
   txt=''.join(x.text or '' for x in el.iter(W+'t')).strip()
   if not txt: out.append(''); continue
   style=''; ppr=el.find(W+'pPr')
   if ppr is not None and ppr.find(W+'pStyle') is not None: style=ppr.find(W+'pStyle').get(W+'val','')
   m=re.search(r'(?:heading|judul)(\d)',style,re.I)
   if m: out += ['#'*min(int(m.group(1)),4)+' '+txt,'']
   elif re.match(r'^(BAB|CHAPTER)\s+[IVXLCDM0-9]+',txt,re.I) or (txt.isupper() and len(txt)<70): out += ['# '+txt,'']
   else: out.append(txt)
  elif el.tag==W+'tbl':
   out.append('')
   for i,row in enumerate(el.findall('.//'+W+'tr')):
    cells=[' '.join(''.join(t.text or '' for t in p.iter(W+'t')) for p in c.findall('.//'+W+'p')).replace('|','/') for c in row.findall(W+'tc')]
    out.append('| '+' | '.join(cells)+' |')
    if i==0: out.append('|'+'---|'*max(1,len(cells)))
 return '\n'.join(out)+'\n'
def kind(title):
 clean=re.sub(r'^\s*[\d.]+\s*','',title).lower()
 for k,p in PATTERNS.items():
  if re.search(p,clean,re.I): return k
 return 'chapter' if re.match(r'^(BAB|CHAPTER)\s+',title,re.I) else 'section'
def parse(md):
 lines=md.splitlines(); heads=[]
 for n,line in enumerate(lines,1):
  m=re.match(r'^(#{1,6})\s+(.+)',line.strip())
  if m: heads.append((n,len(m.group(1)),m.group(2).strip())); continue
  m=NUM.match(line)
  if m: heads.append((n,min(m.group(1).count('.')+1,4),m.group(0).strip()))
 if not heads and lines: heads=[(1,1,'Document')]
 sections=[]
 for i,(start,level,title) in enumerate(heads):
  end=next((s-1 for s,l,_ in heads[i+1:] if l<=level),len(lines))
  sections.append({'id':f'S{i+1:03d}','title':title,'level':level,'start':start,'end':max(start,end),'kind':kind(title)})
 return lines,sections
def items(lines,s):
 out=[]
 for n in range(s['start']+1,s['end']+1):
  m=LIST.match(lines[n-1])
  if m: out.append({'line':n,'text':m.group(1),'form':'list'})
 if out:return out[:40]
 for n in range(s['start']+1,s['end']+1):
  t=lines[n-1].strip()
  if t and not t.startswith(('#','|')):out.append({'line':n,'text':t,'form':'paragraph'})
 return out[:12]
def prepare(src,out,level,lang,force=False):
 src=src.expanduser().resolve(strict=True)
 if not src.is_file() or src.stat().st_size==0: raise PrepError('Input must be a non-empty file')
 if src.stat().st_size>MAX_BYTES: raise PrepError('Input exceeds the 50 MiB limit')
 if src.suffix.lower()=='.md': md=src.read_text(encoding='utf-8-sig')
 elif src.suffix.lower()=='.docx': md=text_docx(src)
 else: raise PrepError('Supported formats: .md and .docx; convert PDF first')
 if not md.strip():raise PrepError('No text could be extracted')
 lines,sections=parse(md); anchors={}
 for s in sections:
  if s['kind'] in PATTERNS:anchors.setdefault(s['kind'],[]).append({**s,'items':items(lines,s)})
 chain={k:[it for sec in anchors.get(k,[]) for it in sec['items']] for k in ('problem','objective','hypothesis','conclusion')}
 counts={k:len(v) for k,v in chain.items() if v and any(x['form']=='list' for x in v)}
 machine=[]
 if len(counts)>=2 and len(set(counts.values()))>1:machine.append({'id':'M-CHAIN-COUNT','type':'candidate_signal','status':'candidate','counts':counts,'message':'List item counts differ; check traceability, do not treat as automatically wrong.'})
 research='not-yet-classified'; low=md.lower()
 for label,pat in [('mixed',r'mixed methods|metode campuran'),('review',r'systematic literature review|slr|bibliometr'),('computational-ml',r'machine learning|deep learning|clustering|klasifikasi|prediksi'),('qualitative',r'wawancara|informan|fenomenologi|studi kasus'),('quantitative',r'regresi|regression|pls-sem|anova|kuesioner|hipotesis'),('system-development',r'waterfall|prototype|black-box|uml|rancang bangun')]:
  if re.search(pat,low): research=label; break
 out=out.expanduser().resolve()
 if out.exists():
  if not force:raise PrepError(f'Workspace already exists: {out}; use --force to replace')
  shutil.rmtree(out)
 out.mkdir(parents=True)
 normalized='\n'.join(lines).strip()+'\n'
 (out/'manuscript.md').write_text(normalized,encoding='utf-8')
 (out/'manuscript_numbered.md').write_text('\n'.join(f'L{i:05d}| {x}' for i,x in enumerate(normalized.splitlines(),1))+'\n',encoding='utf-8')
 (out/'sections.json').write_text(json.dumps(sections,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 mapping={'source':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'level':level,'language':lang,'research_type':research,'sections':sections,'anchors':anchors,'chain':chain,'limitations':['Page numbers are not guaranteed.','Headings are recognized heuristically; verify the extraction.','Machine signals are not academic conclusions.']}
 (out/'research_map.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (out/'machine_findings.json').write_text(json.dumps(machine,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 checks={f'RC{i:02d}':{'status':'not_assessable','coverage':'limited','basis':'Not yet assessed by a reviewer.','missing':'Academic assessment required.'} for i in range(1,11)}
 (out/'audit.json.template').write_text(json.dumps({'summary':'','level':level,'research_type':research,'checks':checks,'findings':[],'author_questions':[]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (out/'AUDIT.md').write_text('Read `manuscript_numbered.md` in full. Use `research_map.json` as an index, not a substitute for the manuscript. Run the Logic, Consistency, Methodology, Evidence, and Devil’s Advocate passes from `reviewer-protocol.md`. Fill in `audit.json` following `research-audit-schema.md`; validate with `python skills/audit/scripts/validate_research_audit.py WORKSPACE`. Automatic counts are candidate signals only. Do not invent pages, evidence, or conclusions.\n',encoding='utf-8')
 return out
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('--out',required=True,type=Path);p.add_argument('--level',default='undergraduate',choices=['undergraduate','masters','doctoral','unspecified']);p.add_argument('--lang',default='id',choices=['id','en']);p.add_argument('--force',action='store_true');a=p.parse_args()
 try:o=prepare(a.input,a.out,a.level,a.lang,a.force)
 except (OSError,PrepError) as e:print('ERROR:',e,file=sys.stderr);return 1
 print('Workspace:',o);print('Machine signals are candidates only. Read the full source document.');return 0
if __name__=='__main__':raise SystemExit(main())
