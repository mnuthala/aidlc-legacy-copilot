"""Synthetic controller tests; these do not test a real legacy application."""
import base64, contextlib, copy, importlib.util, io, os, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
PACKAGE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('aidlc',PACKAGE/'harness/aidlc.py')
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class ControllerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.keys=tempfile.TemporaryDirectory();cls.key=Path(cls.keys.name)/'reviewer.key';cls.pub=Path(cls.keys.name)/'reviewer.pub'
  subprocess.run(['openssl','genpkey','-algorithm','RSA','-pkeyopt','rsa_keygen_bits:2048','-out',str(cls.key)],capture_output=True,check=True)
  subprocess.run(['openssl','pkey','-in',str(cls.key),'-pubout','-out',str(cls.pub)],capture_output=True,check=True)
 @classmethod
 def tearDownClass(cls):cls.keys.cleanup()
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'repo';self.root.mkdir()
  for f in ['harness','.github']:shutil.copytree(PACKAGE/f,self.root/f,ignore=shutil.ignore_patterns('__pycache__'))
  old=a.ROOT;a.ROOT=self.root;self.addCleanup(setattr,a,'ROOT',old);self.addCleanup(self.tmp.cleanup)
  (self.root/'src').mkdir();(self.root/'src/Example.java').write_text('class Example {}')
  cfg=a.config();cfg['source_roots']=['src'];cfg['repository_id']='test/repo';a.write(self.root/'harness/config.json',cfg)
  brs=Path(self.tmp.name)/'brs.md';brs.write_text('Synthetic BRS for controller tests only.');self.brs=brs
  a.init('CHANGE-1',brs,brs);self.c=a.change_dir('CHANGE-1')
  for f in a.DOCS:(self.c/f).write_text('# Synthetic fixture\n\n'+'Evidence fixture for structural controller checks only. '*8)
  a.write(self.c/'requirements.json',[{'id':'REQ-1','type':'functional','text':'Synthetic observable behaviour','source':'Synthetic section 1'}])
  assessment={kind:{d:{'score':4,'reason':'Synthetic complete assessment','evidence':'Synthetic BRS section 1'} for d in dims} for kind,dims in [('clarity',a.CLARITY),('quality',a.QUALITY)]}
  a.write(self.c/'stories.json',[{'id':'ST-1','title':'Synthetic story','actor':'Test operator','capability':'Validate controller','benefit':'Check workflow correctness','scope':'Synthetic artifacts','exclusions':'Real application behaviour','requirement_ids':['REQ-1'],'acceptance_criteria':[{'id':'AC-1','given':'Complete fixture','when':'Validation runs','then':'It succeeds'}],'dependencies':[],'blocking_questions':[],'assessment':assessment}])
  a.write(self.c/'tasks.json',[{'id':'TASK-1','title':'Synthetic task','story_ids':['ST-1'],'design_refs':['LLD.md'],'depends_on':[],'deliverable':'Fixture','done_when':'Fixture validated','verification':'Unit test'}])
  a.write(self.c/'test-cases.json',[{'id':'TC-1','story_ids':['ST-1'],'acceptance_criteria_ids':['AC-1'],'suite':'unit','scenario':'Synthetic result','expected':'Pass','fixture':'Synthetic input','automation_id':'SyntheticTest#passes'}])
  self.trust=Path(self.tmp.name)/'trust.json'
  a.write(self.trust,{'repository_id':'test/repo','required_roles':{'plan':['business','technical','qa'],'release':['technical','qa','release']},'reviewers':{'reviewer':{'public_key':str(self.pub),'roles':['business','technical','qa','release']}}})
  env=patch.dict(os.environ,{'AIDLC_TRUST_STORE':str(self.trust)});env.start();self.addCleanup(env.stop)
 def edit(self,file,fn):
  x=a.read(self.c/file);fn(x);a.write(self.c/file,x)
 def sign(self,gate='plan'):
  payload=a.payload(self.c,gate)
  sig=subprocess.run(['openssl','dgst','-sha256','-sign',str(self.key)],input=a.canonical(payload),capture_output=True,check=True).stdout
  p=self.c/'approvals'/gate/'reviewer.json';a.write(p,{'reviewer':'reviewer','payload':payload,'signature':base64.b64encode(sig).decode()});return p
 def adapter(self,suite,xml=None,exit_code=0):
  xml=xml if xml is not None else '<testsuite><testcase classname="SyntheticTest" name="passes"/></testsuite>'
  code="import os,pathlib; p=pathlib.Path(os.environ['AIDLC_RUN_DIR'])/'reports'; p.mkdir(); (p/'results.xml').write_text("+repr(xml)+"); raise SystemExit("+str(exit_code)+")"
  cfg=a.config();cfg['adapters'][suite]={'argv':[sys.executable,'-c',code],'report_glob':'reports/*.xml','timeout_seconds':10};a.write(self.root/'harness/config.json',cfg)
 def all_runs(self):
  for s in ['build']+a.SUITES:self.adapter(s)
  self.sign();(self.c/'implementation-review.md').write_text('Synthetic independent review fixture. '*8)
  for s in ['build']+a.SUITES:a.run(self.c,s)
 def test_complete_plan_scores(self):self.assertEqual(a.validate(self.c)[0]['clarity_index'],100)
 def test_blockers_override_scores(self):
  self.edit('stories.json',lambda x:x[0].update(blocking_questions=['Who approves?']))
  with self.assertRaisesRegex(a.GateError,'Blocking'):a.validate(self.c)
 def test_low_quality_blocks(self):
  for d in ['value','size']:self.edit('stories.json',lambda x:x[0]['assessment']['quality'][d].update(score=0))
  with self.assertRaisesRegex(a.GateError,'threshold'):a.validate(self.c)
 def test_score_without_evidence_blocks(self):
  self.edit('stories.json',lambda x:x[0]['assessment']['clarity']['scope'].update(evidence=''))
  with self.assertRaisesRegex(a.GateError,'evidence'):a.validate(self.c)
 def test_uncovered_ac(self):
  self.edit('stories.json',lambda x:x[0]['acceptance_criteria'].append({'id':'AC-2','given':'Input','when':'Action','then':'Outcome'}))
  with self.assertRaisesRegex(a.GateError,'without tests'):a.validate(self.c)
 def test_unknown_requirement(self):
  self.edit('stories.json',lambda x:x[0].update(requirement_ids=['REQ-404']))
  with self.assertRaisesRegex(a.GateError,'Unknown reference'):a.validate(self.c)
 def test_uncovered_requirement(self):
  self.edit('requirements.json',lambda x:x.append({'id':'REQ-2','text':'Other','source':'Section 2','type':'functional'}))
  with self.assertRaisesRegex(a.GateError,'without story'):a.validate(self.c)
 def test_task_cycle(self):
  def cycle(x):
   y=copy.deepcopy(x[0]);y['id']='TASK-2';y['depends_on']=['TASK-1'];x[0]['depends_on']=['TASK-2'];x.append(y)
  self.edit('tasks.json',cycle)
  with self.assertRaisesRegex(a.GateError,'Cyclic'):a.validate(self.c)
 def test_draft_document(self):
  (self.c/'HLD.md').write_text('TODO: '+'Draft '*30)
  with self.assertRaisesRegex(a.GateError,'placeholder'):a.validate(self.c)
 def test_missing_approval(self):
  with self.assertRaisesRegex(a.GateError,'Missing valid'):a.approvals(self.c,'plan')
 def test_signed_approval(self):self.sign();self.assertIn('business',a.approvals(self.c,'plan'))
 def test_bad_signature(self):
  p=self.sign();r=a.read(p);r['signature']=base64.b64encode(b'wrong').decode();a.write(p,r)
  with self.assertRaises(a.GateError):a.approvals(self.c,'plan')
 def test_changed_plan_invalidates_approval(self):
  self.sign();p=self.c/'HLD.md';p.write_text(p.read_text()+'\nMaterial design change')
  with self.assertRaisesRegex(a.GateError,'Missing valid'):a.approvals(self.c,'plan')
 def test_changed_controls_invalidates_approval(self):
  self.sign();cfg=a.config();cfg['max_repairs_total']=10;a.write(self.root/'harness/config.json',cfg)
  with self.assertRaises(a.GateError):a.approvals(self.c,'plan')
 def test_missing_role(self):
  self.sign();cfg=a.read(self.trust);cfg['reviewers']['reviewer']['roles']=['business'];a.write(self.trust,cfg)
  with self.assertRaisesRegex(a.GateError,'technical'):a.approvals(self.c,'plan')
 def test_in_repo_trust_rejected(self):
  with patch.dict(os.environ,{'AIDLC_TRUST_STORE':str(self.root/'trust.json')}):
   with self.assertRaisesRegex(a.GateError,'outside'):a.trust()
 def test_disabled_adapter(self):
  self.sign()
  with self.assertRaisesRegex(a.GateError,'not configured'):a.run(self.c,'unit')
 def test_zero_tests(self):
  self.adapter('unit','<testsuite/>');self.sign()
  with self.assertRaisesRegex(a.GateError,'Zero tests'):a.run(self.c,'unit')
 def test_xml_failure_despite_exit_zero(self):
  self.adapter('unit','<testsuite><testcase name="x"><failure/></testcase></testsuite>');self.sign()
  with self.assertRaisesRegex(a.GateError,'failures'):a.run(self.c,'unit')
 def test_skipped_tests(self):
  self.adapter('unit','<testsuite><testcase name="x"><skipped/></testcase></testsuite>');self.sign()
  with self.assertRaisesRegex(a.GateError,'Skipped'):a.run(self.c,'unit')
 def test_nonzero_exit(self):
  self.adapter('unit',exit_code=1);self.sign()
  with self.assertRaisesRegex(a.GateError,'nonzero'):a.run(self.c,'unit')
 def test_baseline_not_candidate(self):
  self.adapter('unit');a.run(self.c,'unit',baseline=True);self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_complete_evidence_and_release(self):
  self.all_runs();self.assertTrue(a.evidence(self.c)['ready_for_review']);self.sign('release');self.assertIn('release',a.approvals(self.c,'release'))
 def test_source_changes_invalidate_evidence(self):
  self.all_runs();(self.root/'src/Example.java').write_text('class Example {int changed;}');self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_report_tampering(self):
  self.all_runs();p=next((self.c/'runs').glob('*/reports/results.xml'));p.write_text('<testsuite/>');self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_planned_test_must_be_observed(self):
  self.edit('test-cases.json',lambda x:x[0].update(automation_id='Absent#test'));self.all_runs();self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_failed_latest_run_supersedes_pass(self):
  self.all_runs();r=a.run(self.c,'unit');r['status']='failed';a.write(self.c/'runs'/r['id']/'result.json',r);self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_changed_review_invalidates_release(self):
  self.all_runs();self.sign('release');(self.c/'implementation-review.md').write_text('New review content. '*20)
  with self.assertRaises(a.GateError):a.approvals(self.c,'release')
 def test_repair_budget(self):
  self.sign()
  def repair():
   with patch.object(sys,'argv',['aidlc','repair','CHANGE-1','--failure','FAIL-1','--diagnosis','Reproduced defect']),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):return a.main()
  self.assertEqual([repair() for _ in range(4)],[0,0,0,2])
 def test_path_traversal(self):
  with self.assertRaises(a.GateError):a.change_dir('../ESCAPE')
 def test_bad_init_leaves_no_partial_change(self):
  cfg=a.config();cfg['source_roots']=['missing'];a.write(self.root/'harness/config.json',cfg)
  with self.assertRaises(a.GateError):a.init('CHANGE-2',self.brs,self.brs)
  self.assertFalse((self.root/'changes/CHANGE-2').exists())
 def test_missing_fresh_report(self):
  cfg=a.config();cfg['adapters']['unit']={'argv':[sys.executable,'-c','pass'],'report_glob':'reports/*.xml'};a.write(self.root/'harness/config.json',cfg);self.sign()
  with self.assertRaisesRegex(a.GateError,'No fresh'):a.run(self.c,'unit')
 def test_source_mutation_during_run(self):
  cfg=a.config();cfg['adapters']['unit']={'argv':[sys.executable,'-c',"from pathlib import Path; Path('src/Example.java').write_text('changed')"],'report_glob':'reports/*.xml'};a.write(self.root/'harness/config.json',cfg);self.sign()
  with self.assertRaisesRegex(a.GateError,'Source changed'):a.run(self.c,'unit')
 def test_release_request_without_evidence(self):
  with self.assertRaisesRegex(a.GateError,'passing current evidence'):a.payload(self.c,'release')
 def test_unknown_reviewer(self):
  p=self.sign();r=a.read(p);r['reviewer']='untrusted';a.write(p,r)
  with self.assertRaisesRegex(a.GateError,'Missing valid'):a.approvals(self.c,'plan')
 def test_same_second_runs_use_completion_time(self):
  self.all_runs();p=self.c/'runs'/'0000-later'/'result.json'
  a.write(p,{'id':'0000-later','suite':'unit','status':'failed','baseline':False,'source_digest':a.source_digest(),'plan_digest':a.plan_digest(self.c),'finished_at':'9999-01-01T00:00:00+00:00'})
  self.assertFalse(a.evidence(self.c)['ready_for_review'])
 def test_xml_report_wrong_suite_does_not_cover_case(self):
  self.edit('test-cases.json',lambda x:x[0].update(suite='functional',automation_id='Functional#expected'))
  self.all_runs();self.assertFalse(a.evidence(self.c)['ready_for_review'])
if __name__=='__main__':unittest.main()
