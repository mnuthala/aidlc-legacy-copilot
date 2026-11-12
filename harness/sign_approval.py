#!/usr/bin/env python3
"""Run ONLY on the human reviewer workstation, never on the agent worker."""
import argparse, base64, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('request');p.add_argument('--reviewer',required=True);p.add_argument('--private-key',required=True);p.add_argument('--out',required=True)
a=p.parse_args()
payload=json.loads(Path(a.request).read_text())
msg=json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
print(json.dumps(payload,indent=2))
if input('Approve this exact reviewed payload? Type APPROVE: ') != 'APPROVE': raise SystemExit('Not approved')
signature=subprocess.run(['openssl','dgst','-sha256','-sign',a.private_key],input=msg,capture_output=True,check=True).stdout
Path(a.out).write_text(json.dumps({'reviewer':a.reviewer,'payload':payload,'signature':base64.b64encode(signature).decode()},indent=2)+'\n')
