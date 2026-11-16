#!/usr/bin/env python3
"""Compare two Markdown drafts; flag stale numeric/acronym candidates conservatively."""
from __future__ import annotations
import argparse,difflib,re,sys
from pathlib import Path
NUM=re.compile(r'(?<![\w.])\d+(?:[.,]\d+)*%?(?![\w])');ACR=re.compile(r'\b[A-Z][A-Za-z0-9-]*[A-Z][A-Za-z0-9-]*\b');HEAD=re.compile(r'^(#{1,6})\s+(.+)$')
def load(p):
 if p.is_dir():p=p/'manuscript.md'
 return p.read_text(encoding='utf-8').splitlines()
def section_map(lines):
 hs=[(i,len(m.group(1)),m.group(2)) for i,x in enumerate(lines,1) if (m:=HEAD.match(x))];out=[]
 for j,(st,lv,title) in enumerate(hs):
  en=next((n-1 for n,l,_ in hs[j+1:] if l<=lv),len(lines));out.append((st,en,title))
 return out
def sect(n,ss):
 m=[x for x in ss if x[0]<=n<=x[1]];return m[-1][2] if m else '(document start)'
def vals(s):return set(NUM.findall(s))|{x for x in ACR.findall(s) if sum(c.isupper() for c in x)>=2}
def compare(old,new):
 sm=difflib.SequenceMatcher(a=old,b=new,autojunk=False);ss=section_map(new);changed={};replaced=set()
 for op,i1,i2,j1,j2 in sm.get_opcodes():
  if op not in ('replace','insert','delete'):continue
  if op=='delete':
   k=sect(max(1,min(j1+1,len(new) or 1)),ss);changed[k]=changed.get(k,0)+i2-i1;continue
  for n in range(j1+1,j2+1):k=sect(n,ss);changed[k]=changed.get(k,0)+1
  if op=='replace':replaced|=vals(' '.join(old[i1:i2]))-vals(' '.join(new[j1:j2]))
 candidates=[]
 for t in sorted(replaced):
  occ=[(n,sect(n,ss),line.strip()) for n,line in enumerate(new,1) if re.search(r'(?<![\w.])'+re.escape(t)+r'(?![\w])',line)]
  if occ:candidates.append((t,occ))
 return changed,[x[2] for x in ss if x[2] not in changed],candidates
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('old',type=Path);p.add_argument('new',type=Path);p.add_argument('-o','--output',type=Path);a=p.parse_args()
 try:old=load(a.old);new=load(a.new);changed,unchanged,cands=compare(old,new)
 except Exception as e:print('ERROR:',e,file=sys.stderr);return 2
 out=['# Revision Impact Review','', '## Changed sections','', '| Section | Changed lines |','|---|---:|']+[f'| {k} | {v} |' for k,v in changed.items()]+['','## Unchanged sections','']+['- '+x for x in unchanged]+['','## Candidate stale values/acronyms','']
 if cands:
  for t,occ in cands:out.append(f'### `{t}`');out += [f'- Line {n} — {s}: {line}' for n,s,line in occ];out.append('')
 else:out.append('No automatic candidates.')
 out+=['','All candidates need checking in context. A repeated number or term is not automatically an error.'];text='\n'.join(out)+'\n'
 if a.output:a.output.write_text(text,encoding='utf-8');print('Report:',a.output)
 else:sys.stdout.write(text)
 return 0
if __name__=='__main__':raise SystemExit(main())
