#!/usr/bin/env python3
"""AIDLC stage controller. Python 3.10+ standard library; OpenSSL for approvals."""
import argparse
import base64
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
CLARITY = ['actor_purpose', 'scope', 'behaviour', 'acceptance_criteria', 'dependencies']
QUALITY = ['value', 'completeness', 'testability', 'feasibility', 'consistency', 'traceability', 'size']
DOCS = ['requirements.md', 'impact-analysis.md', 'HLD.md', 'LLD.md', 'integration-design.md',
        'data-design.md', 'security-design.md', 'nfr-design.md', 'decisions.md',
        'deployment-design.md', 'test-plan.md', 'review-record.md']
PLAN_FILES = DOCS + ['requirements.json', 'stories.json', 'tasks.json', 'test-cases.json']
SUITES = ['unit', 'functional', 'integration', 'regression']

class GateError(Exception):
    pass

def require(ok, message):
    if not ok:
        raise GateError(message)

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def read(path):
    return json.loads(Path(path).read_text())

def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)

def config():
    return read(ROOT / 'harness/config.json')

def change_dir(change):
    require(bool(re.fullmatch(r'[A-Z][A-Z0-9_-]{1,63}', change)), 'Invalid change ID')
    p = ROOT / 'changes' / change
    require(p.is_dir(), 'Change does not exist; use init')
    return p

def digest_paths(paths):
    h = hashlib.sha256()
    for p in sorted(set(paths)):
        require(not p.is_symlink(), 'Symlinks are not supported in evidence inputs: ' + str(p))
        h.update(str(p.relative_to(ROOT)).encode() + b'\0' + p.read_bytes() + b'\0')
    return h.hexdigest()

def files_under(path):
    return [p for p in path.rglob('*') if p.is_file() and '__pycache__' not in p.parts]

def source_digest():
    paths = []
    roots = config()['source_roots']
    require(bool(roots), 'Configure at least one source root')
    for name in roots:
        p = (ROOT / name).resolve()
        require(p.is_relative_to(ROOT) and p != ROOT, 'Source roots must be subpaths inside repository')
        require(p.exists(), 'Missing configured source root: ' + name)
        paths.extend(files_under(p) if p.is_dir() else [p])
    require(bool(paths), 'Configured source roots contain no files')
    return digest_paths(paths)

def plan_digest(c):
    paths = [c / f for f in PLAN_FILES] + files_under(c / 'inputs') + [c / 'baseline.json']
    for folder in ['harness', '.github']:
        paths += files_under(ROOT / folder)
    return digest_paths(paths)

def nonempty(value, label):
    require(isinstance(value, str) and bool(value.strip()), 'Missing ' + label)
    require(not re.search(r'\b(TODO|TBD|PLACEHOLDER)\b', value, re.I), 'Unresolved placeholder in ' + label)

def indexed(items, label):
    require(isinstance(items, list) and bool(items), label + ' must be a nonempty list')
    result = {}
    for x in items:
        require(isinstance(x, dict), label + ' entry must be an object')
        nonempty(x.get('id'), label + '.id')
        require(x['id'] not in result, 'Duplicate ID: ' + x['id'])
        result[x['id']] = x
    return result

def references(ids, target, label):
    require(isinstance(ids, list) and bool(ids), 'Missing references: ' + label)
    require(all(i in target for i in ids), 'Unknown reference in ' + label)

def score(story, kind, dimensions):
    review = story.get('assessment', {}).get(kind, {})
    vals = []
    for d in dimensions:
        x = review.get(d, {})
        v = x.get('score')
        require(type(v) is int and 0 <= v <= 4, 'Invalid score: ' + story['id'] + '/' + d)
        nonempty(x.get('reason'), 'score rationale ' + d)
        nonempty(x.get('evidence'), 'score evidence ' + d)
        vals.append(v)
    return round(sum(vals) / (4 * len(vals)) * 100, 2)

def validate(c):
    reqs = indexed(read(c / 'requirements.json'), 'requirements')
    stories = indexed(read(c / 'stories.json'), 'stories')
    tasks = indexed(read(c / 'tasks.json'), 'tasks')
    cases = indexed(read(c / 'test-cases.json'), 'test cases')
    for name in DOCS:
        text = (c / name).read_text()
        nonempty(text, name)
        require(len(text.strip()) >= 100, 'Document too short: ' + name)
    for r in reqs.values():
        for f in ['text', 'source', 'type']:
            nonempty(r.get(f), 'requirement.' + f)
    assessments = []
    criteria = {}
    for s in stories.values():
        for f in ['title', 'actor', 'capability', 'benefit', 'scope', 'exclusions']:
            nonempty(s.get(f), s['id'] + '.' + f)
        references(s.get('requirement_ids'), reqs, 'story requirements')
        require(s.get('blocking_questions') == [], 'Blocking questions: ' + s['id'])
        require(isinstance(s.get('dependencies'), list), 'Story dependencies must be listed')
        for d in s['dependencies']:
            require(d in stories and d != s['id'], 'Unknown/self story dependency')
        acs = indexed(s.get('acceptance_criteria'), 'acceptance criteria')
        for ac in acs.values():
            require(ac['id'] not in criteria, 'Duplicate acceptance criterion')
            for f in ['given', 'when', 'then']:
                nonempty(ac.get(f), 'acceptance criterion.' + f)
            criteria[ac['id']] = s['id']
        a, b = score(s, 'clarity', CLARITY), score(s, 'quality', QUALITY)
        require(min(a, b) >= config()['readiness_threshold'], 'Story below readiness threshold: ' + s['id'])
        assessments.append({'id': s['id'], 'clarity_index': a, 'quality_score': b, 'status': 'ready'})
    covered_req = {i for s in stories.values() for i in s['requirement_ids']}
    require(set(reqs) == covered_req, 'Requirements without story coverage')
    for t in tasks.values():
        references(t.get('story_ids'), stories, 'task stories')
        for f in ['title', 'deliverable', 'done_when', 'verification']:
            nonempty(t.get(f), 'task.' + f)
        require(isinstance(t.get('depends_on'), list), 'Task dependencies must be listed')
        require(all(d in tasks and d != t['id'] for d in t['depends_on']), 'Unknown/self task dependency')
        references(t.get('design_refs'), {f: True for f in DOCS}, 'task design')
    visited, active = set(), set()
    def visit(key):
        require(key not in active, 'Cyclic task dependencies')
        if key in visited:
            return
        active.add(key)
        for dep in tasks[key]['depends_on']:
            visit(dep)
        active.remove(key)
        visited.add(key)
    for key in tasks:
        visit(key)
    covered_ac, covered_stories = set(), set()
    for t in cases.values():
        references(t.get('story_ids'), stories, 'test stories')
        references(t.get('acceptance_criteria_ids'), criteria, 'test acceptance criteria')
        require(all(criteria[a] in t['story_ids'] for a in t['acceptance_criteria_ids']), 'Criterion belongs to another story')
        require(t.get('suite') in SUITES, 'Invalid test suite')
        for f in ['scenario', 'expected', 'fixture', 'automation_id']:
            nonempty(t.get(f), 'test.' + f)
        covered_ac.update(t['acceptance_criteria_ids'])
        covered_stories.update(t['story_ids'])
    require(set(criteria) == covered_ac, 'Acceptance criteria without tests')
    require(set(stories) == covered_stories, 'Stories without tests')
    require(set(stories) <= {s for t in tasks.values() for s in t['story_ids']}, 'Stories without tasks')
    write(c / 'quality-report.json', assessments)
    return assessments

def trust():
    loc = os.environ.get('AIDLC_TRUST_STORE')
    require(bool(loc), 'Set AIDLC_TRUST_STORE to reviewer trust JSON outside the repository')
    p = Path(loc).resolve()
    require(not p.is_relative_to(ROOT), 'Trust store must be outside agent-editable repository')
    cfg = read(p)
    require(cfg.get('repository_id') == config()['repository_id'], 'Trust store repository mismatch')
    return cfg, p.parent

def payload(c, gate):
    validate(c)
    cfg, _ = trust()
    result = {'schema': 1, 'repository_id': cfg['repository_id'], 'change': c.name,
              'gate': gate, 'plan_digest': plan_digest(c)}
    if gate == 'release':
        report = evidence(c)
        require(report['ready_for_review'], 'Release request requires passing current evidence')
        result['source_digest'] = source_digest()
        result['evidence_digest'] = hashlib.sha256(canonical(report)).hexdigest()
    return result

def approvals(c, gate):
    cfg, parent = trust()
    expected = canonical(payload(c, gate))
    roles = set()
    for path in (c / 'approvals' / gate).glob('*.json'):
        receipt = read(path)
        if canonical(receipt.get('payload')) != expected:
            continue
        who = cfg.get('reviewers', {}).get(receipt.get('reviewer'))
        if not who:
            continue
        pub = (parent / who['public_key']).resolve()
        require(not pub.is_relative_to(ROOT), 'Public keys must be outside repository')
        try:
            signature = base64.b64decode(receipt['signature'], validate=True)
        except (ValueError, KeyError):
            continue
        with tempfile.TemporaryDirectory() as tmp:
            msg, sig = Path(tmp) / 'payload', Path(tmp) / 'signature'
            msg.write_bytes(expected)
            sig.write_bytes(signature)
            p = subprocess.run(['openssl', 'dgst', '-sha256', '-verify', str(pub), '-signature', str(sig), str(msg)], capture_output=True)
            if p.returncode == 0:
                roles.update(who['roles'])
    required = set(cfg['required_roles'][gate])
    require(bool(required) and required <= roles, 'Missing valid approvals: ' + ', '.join(sorted(required - roles)))
    return sorted(roles)

def junit(paths):
    total = failures = errors = skipped = 0
    names = set()
    for p in paths:
        tree = ET.parse(p).getroot()
        for case in tree.iter('testcase'):
            total += 1
            failures += int(case.find('failure') is not None)
            errors += int(case.find('error') is not None)
            skipped += int(case.find('skipped') is not None)
            names.add(case.get('classname', '') + '#' + case.get('name', ''))
    require(total > 0, 'Zero tests executed')
    require(failures + errors == 0, 'Test failures/errors detected in XML')
    require(skipped == 0, 'Skipped tests need an explicit human decision; cannot report pass')
    return {'tests': total, 'failures': failures, 'errors': errors, 'skipped': skipped, 'automation_ids': sorted(names)}

def run(c, suite, baseline=False):
    if not baseline:
        approvals(c, 'plan')
    cfg = config()['adapters'].get(suite)
    require(cfg and cfg.get('argv'), 'Adapter not configured: ' + suite)
    before = source_digest()
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8]
    folder = c / 'runs' / run_id
    folder.mkdir(parents=True)
    result = {'id': run_id, 'suite': suite, 'baseline': baseline, 'started_at': now(),
              'source_digest': before, 'plan_digest': None if baseline else plan_digest(c), 'status': 'failed'}
    env = os.environ.copy()
    env.update(AIDLC_CHANGE=c.name, AIDLC_RUN_DIR=str(folder), AIDLC_SUITE=suite)
    try:
        report_glob = cfg.get('report_glob', '')
        require(suite == 'build' or report_glob, 'Test adapter needs report_glob')
        # Only fresh reports under the unique run directory are accepted.
        if report_glob:
            require(not Path(report_glob).is_absolute() and '..' not in Path(report_glob).parts, 'Report glob must be relative to run directory')
        with (folder / 'command.log').open('w') as log:
            p = subprocess.run(cfg['argv'], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                               timeout=cfg.get('timeout_seconds', 900), check=False)
        result['exit_code'] = p.returncode
        require(p.returncode == 0, 'Adapter returned nonzero status; inspect command.log')
        require(source_digest() == before, 'Source changed during execution; evidence rejected')
        if suite != 'build':
            reports = list(folder.glob(report_glob))
            require(bool(reports), 'No fresh JUnit XML reports in run directory')
            result['summary'] = junit(reports)
            result['reports'] = {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest() for p in reports}
        result['status'] = 'passed'
    except (GateError, subprocess.TimeoutExpired, OSError, ET.ParseError) as exc:
        result['reason'] = str(exc)
    result['finished_at'] = now()
    write(folder / 'result.json', result)
    require(result['status'] == 'passed', result.get('reason', 'Execution failed'))
    return result

def evidence(c):
    validate(c)
    current, plan = source_digest(), plan_digest(c)
    runs = sorted([read(p) for p in (c / 'runs').glob('*/result.json')],
                  key=lambda r: (r.get('finished_at', ''), r.get('id', '')))
    latest = {}
    for r in runs:
        if not r.get('baseline') and r.get('source_digest') == current and r.get('plan_digest') == plan:
            latest[r['suite']] = r
    issues = []
    observed = set()
    for suite in ['build'] + SUITES:
        r = latest.get(suite)
        if not r or r['status'] != 'passed':
            issues.append('Missing passing current run: ' + suite)
            continue
        for name, sha in r.get('reports', {}).items():
            p = c / 'runs' / r['id'] / name
            if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest() != sha:
                issues.append('Missing/modified report: ' + str(p))
        observed.update(r.get('summary', {}).get('automation_ids', []))
    for t in read(c / 'test-cases.json'):
        r = latest.get(t['suite'], {})
        if t['automation_id'] not in r.get('summary', {}).get('automation_ids', []):
            issues.append('Planned test not observed in assigned suite: ' + t['id'])
    review = c / 'implementation-review.md'
    if not review.exists() or len(review.read_text().strip()) < 100 or re.search(r'\b(TODO|TBD|PLACEHOLDER)\b', review.read_text(), re.I):
        issues.append('Independent implementation review missing/incomplete')
    return {'change': c.name, 'source_digest': current, 'plan_digest': plan,
            'ready_for_review': not issues, 'issues': issues,
            'runs': {k: v['id'] for k, v in latest.items()},
            'review_sha256': hashlib.sha256(review.read_bytes()).hexdigest() if review.exists() else None}

def init(change, brs, context):
    require(bool(re.fullmatch(r'[A-Z][A-Z0-9_-]{1,63}', change)), 'Invalid change ID')
    c = ROOT / 'changes' / change
    require(not c.exists(), 'Change already exists')
    baseline = source_digest()
    require(Path(brs).is_file() and Path(context).is_file(), 'Both input files must exist')
    import shutil
    c.mkdir(parents=True)
    (c / 'inputs').mkdir()
    for name, p in [('business-requirements', brs), ('sample-design-context', context)]:
        src = Path(p)
        require(src.is_file(), 'Missing input file: ' + str(src))
        shutil.copy2(src, c / 'inputs' / (name + src.suffix))
    for name in PLAN_FILES:
        shutil.copy2(ROOT / 'harness/templates' / name, c / name)
    write(c / 'baseline.json', {'created_at': now(), 'source_digest': baseline, 'change': change})
    return {'change': change, 'stage': 'analysis', 'next': 'Run aidlc-requirements, then the design and test planning agents'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'validate', 'status', 'approval-request', 'authorize', 'run', 'baseline', 'evidence', 'repair', 'prompt', 'invoke'])
    parser.add_argument('change')
    parser.add_argument('--brs')
    parser.add_argument('--context')
    parser.add_argument('--gate', choices=['plan', 'release'], default='plan')
    parser.add_argument('--suite', choices=['build'] + SUITES, default='unit')
    parser.add_argument('--agent', default='aidlc-coordinator')
    parser.add_argument('--failure')
    parser.add_argument('--diagnosis')
    args = parser.parse_args()
    try:
        if args.command == 'init':
            require(args.brs and args.context, 'init requires --brs and --context')
            out = init(args.change, args.brs, args.context)
        else:
            c = change_dir(args.change)
            if args.command == 'validate':
                out = validate(c)
            elif args.command == 'approval-request':
                out = payload(c, args.gate)
                p = c / ('approval-request-' + args.gate + '.json')
                p.write_bytes(canonical(out))
            elif args.command == 'authorize':
                out = {'approved_roles': approvals(c, args.gate), 'gate': args.gate}
            elif args.command in ['run', 'baseline']:
                out = run(c, args.suite, args.command == 'baseline')
            elif args.command == 'evidence':
                out = evidence(c)
                write(c / 'evidence.json', out)
                require(out['ready_for_review'], '; '.join(out['issues']))
            elif args.command == 'repair':
                approvals(c, 'plan')
                nonempty(args.failure, '--failure')
                nonempty(args.diagnosis, '--diagnosis')
                history = c / 'repair-history.json'
                attempts = read(history) if history.exists() else []
                require(sum(x['failure'] == args.failure for x in attempts) < config()['max_repairs_per_failure'], 'Repair limit reached; human intervention required')
                require(len(attempts) < config()['max_repairs_total'], 'Overall repair budget reached')
                attempts.append({'failure': args.failure, 'diagnosis': args.diagnosis, 'at': now(), 'source_digest': source_digest()})
                write(history, attempts)
                out = attempts[-1]
            elif args.command in ['prompt', 'invoke']:
                profiles = {p.name.removesuffix('.agent.md') for p in (ROOT / '.github/agents').glob('*.agent.md')}
                require(args.agent in profiles, 'Unknown agent')
                if args.agent in ['aidlc-implementation', 'aidlc-test-implementation', 'aidlc-execution', 'aidlc-fix']:
                    approvals(c, 'plan')
                prompt = ('Work only on changes/' + c.name + '. Read .github/agents/' + args.agent + '.agent.md, '
                          '.github/copilot-instructions.md and docs/OPERATING_GUIDE.md. Inspect inputs and current artifacts. '
                          'Follow your stage contract. Never invent requirements or repository evidence. '
                          'Stop at human gates and report blocking questions. Do not invoke other agents automatically.')
                if args.command == 'invoke':
                    # No blanket tool or path auto-approval; Copilot manages its normal permissions.
                    sys.exit(subprocess.run(['copilot', '--agent=' + args.agent, '--prompt', prompt], cwd=ROOT).returncode)
                out = {'agent': args.agent, 'prompt': prompt}
            else:
                out = {'change': c.name, 'baseline': read(c / 'baseline.json'), 'stage': 'inferred from validated artifacts; no self-approval',
                       'next': 'validate; approval-request; authorize; run; evidence; release authorize'}
        print(json.dumps(out, indent=2))
    except (GateError, OSError, ValueError, KeyError, TypeError) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    sys.exit(main())
