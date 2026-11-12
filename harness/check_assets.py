#!/usr/bin/env python3
"""Dependency-free checks for distributed assets; not a general YAML parser."""
from pathlib import Path
import json,re
r=Path(__file__).resolve().parents[1]
for p in r.rglob('*.json'):
 if 'changes' not in p.parts: json.loads(p.read_text())
for p in (r/'.github/agents').glob('*.agent.md'):
 text=p.read_text();assert text.startswith('---\n') and '\ndescription:' in text and '\ntools:' in text,p
for p in (r/'.github/skills').glob('*/SKILL.md'):
 text=p.read_text();assert text.startswith('---\n') and f'name: {p.parent.name}\n' in text and '\ndescription:' in text,p
 for path in re.findall(r'(?:Read |and )(docs/[A-Z_]+\.md)',text):assert (r/path).is_file(),path
print('Assets valid')
