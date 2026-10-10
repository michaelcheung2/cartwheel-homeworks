"""Focused checks of review evidence, selection and human judgment gates."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from analysis.review_app import server as app


def fake_trace(i, session='session-a'):
    return {'id': f'{i:032x}', 'timestamp': '2026-10-10T00:00:00Z',
            'input': [{'role': 'user', 'parts': [{'type': 'text', 'content': 'Where is my order?'}]}],
            'output': [{'role': 'assistant', 'parts': [{'type': 'text', 'content': 'The lookup failed.'}]}],
            'metadata': {'attributes': {'cartwheel.scenario_id': f'support-{i:04d}',
                                        'cartwheel.session_id': session, 'cartwheel.user_role': 'shopper'}},
            'observations': [{'id': 'tool-span', 'name': 'get_order', 'type': 'TOOL',
                              'startTime': '2026-10-10T00:00:01Z', 'parentObservationId': 'agent-span',
                              'input': {'order_id': 1}, 'output': None, 'level': 'ERROR',
                              'statusMessage': 'Database lookup failed', 'metadata': {}}]}


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {'CARTWHEEL_ANALYSIS_STATE': self.temp.name})
        self.env.start()
        self.old_corpus, self.old_client = app.CORPUS, app.CLIENT
        app.CORPUS = [app.prepare_record(fake_trace(i)) for i in range(1, 61)]
        app.CLIENT = None
        app.initialize_state()

    def tearDown(self):
        app.CORPUS, app.CLIENT = self.old_corpus, self.old_client
        self.env.stop()
        self.temp.cleanup()

    def test_trace_ids_and_missing_tool_outputs_preserved(self):
        records = [app.prepare_record(fake_trace(i)) for i in (1, 2)]
        self.assertEqual(len({r['id'] for r in records}), 2)
        self.assertEqual(records[0]['meta']['session_id'], records[1]['meta']['session_id'])
        tool = records[0]['steps'][1]
        self.assertIsNone(tool['output'])
        self.assertEqual(tool['error'], 'Database lookup failed')
        self.assertEqual(records[0]['raw_observations'][0]['parentObservationId'], 'agent-span')

    def test_first_batch_has_thirty_distinct_ids_and_exact_methods(self):
        app.initial_sample()
        manifest = app.read('sample_manifest.json')
        entries = manifest['batches'][0]['entries']
        self.assertEqual(len({e['trace_id'] for e in entries}), 30)
        self.assertEqual(sum(e['method'] == 'uniform' for e in entries), 15)
        self.assertEqual(sum(e['method'] == 'cluster_representative' for e in entries), 15)
        self.assertTrue(manifest['dimension_chosen_before_review'])
        app.initial_sample()
        self.assertEqual(app.read('sample_manifest.json'), manifest)

    def test_context_cannot_count_as_review_and_corrections_keep_history(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        context = next(r['id'] for r in app.CORPUS if r['id'] not in app.selected_ids())
        with self.assertRaises(ValueError):
            app.annotation({'trace_id': context, 'review_status': 'first_failure', 'note': 'context'})
        row = app.annotation({'trace_id': tid, 'review_status': 'no_failure_observed', 'note': 'no failure observed'})
        self.assertEqual(row['sync']['status'], 'pending')
        app.annotation({'trace_id': tid, 'review_status': 'first_failure', 'note': 'Revised observation'})
        data = app.read('annotations.json')
        self.assertEqual(len(data['annotations']), 1)
        self.assertEqual(data['history'][0]['note'], 'no failure observed')
        self.assertEqual(app.snapshot()['progress']['reviewed'], 1)

    def test_formal_labels_and_new_batch_require_human_prerequisites(self):
        app.initial_sample()
        with self.assertRaises(ValueError):
            app.label({'trace_id': app.selected_ids()[0], 'mode': 'invented', 'label': 1})
        with self.assertRaises(ValueError):
            app.next_batch()
        self.assertEqual(app.current_labels(), [])

    def test_withdrawal_preserves_note_but_removes_review_count(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        app.annotation({'trace_id': tid, 'review_status': 'first_failure', 'note': 'Original observation'})
        app.withdraw_annotation({'trace_id': tid})
        self.assertEqual(app.snapshot()['progress']['reviewed'], 0)
        self.assertEqual(app.read('annotations.json')['history'][-1]['note'], 'Original observation')

    def test_binary_correction_is_append_only_and_stale_version_does_not_count(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        app.annotation({'trace_id': tid, 'review_status': 'first_failure', 'note': 'Evidence'})
        mode = {'name': 'test_mode', 'status': 'final', 'human_confirmed': True, 'version': 1}
        app.write('patterns.json', {'modes': [mode], 'history': []})
        with patch.object(app, 'sync_score', return_value={'status': 'synced'}):
            for value in (1, 0):
                app.label({'trace_id': tid, 'mode': 'test_mode', 'label': value,
                           'inspected_complete_trace': True, 'note': 'Human test evidence'})
        path = Path(self.temp.name, 'labels/test_mode.jsonl')
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        self.assertEqual(len(rows), 4)
        self.assertEqual(app.current_labels()[0]['label'], 0)
        self.assertEqual(app.snapshot()['progress']['judgments'], 1)
        mode['version'] = 2
        app.write('patterns.json', {'modes': [mode], 'history': []})
        self.assertEqual(app.snapshot()['progress']['judgments_remaining'], 1)

    def test_existing_annotations_are_not_replaced(self):
        Path(self.temp.name, 'sample_manifest.json').unlink()
        app.write('annotations.json', {'annotations': [{'note': 'Existing student work'}]})
        with self.assertRaises(ValueError):
            app.initialize_state()
        self.assertEqual(app.read('annotations.json')['annotations'][0]['note'], 'Existing student work')

    def test_ai_draft_does_not_count_until_inspected_and_accepted(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        app.write('suggestions.json', [{'id': 'draft-1', 'kind': 'open_code_draft', 'trace_id': tid,
                   'author': 'ai', 'status': 'pending', 'proposed_review_status': 'first_failure',
                   'note': 'AI proposal'}])
        self.assertEqual(app.snapshot()['progress']['reviewed'], 0)
        with self.assertRaises(ValueError):
            app.suggestion_decision({'id': 'draft-1', 'decision': 'accepted', 'reason': 'My reviewed note'})
        self.assertEqual(app.snapshot()['progress']['reviewed'], 0)
        app.suggestion_decision({'id': 'draft-1', 'decision': 'accepted', 'reason': 'My revised observation',
                                'inspected_trace': True})
        row = app.read('annotations.json')['annotations'][0]
        self.assertEqual(row['note'], 'My revised observation')
        self.assertEqual(row['source'], 'accepted_ai_draft')
        self.assertEqual(row['source_suggestion_id'], 'draft-1')
        self.assertEqual(app.read('suggestions.json')[0]['author'], 'ai')
        self.assertEqual(app.snapshot()['progress']['reviewed'], 1)

    def test_score_retries_use_same_id_and_verify_text_value(self):
        captured = []
        def create(**kwargs):
            captured.append(kwargs)
        def get(**kwargs):
            last = captured[-1]
            return SimpleNamespace(data=[{'id': last['score_id'], 'stringValue': last['value']}])
        app.CLIENT = SimpleNamespace(create_score=create, flush=lambda: None,
                                     api=SimpleNamespace(score_v_2=SimpleNamespace(get=get)))
        row = {'id': 'note-1', 'trace_id': f'{1:032x}', 'note': 'Observed evidence'}
        self.assertEqual(app.sync_score(row, 'annotation')['status'], 'synced')
        row['note'] = 'Corrected evidence'
        app.sync_score(row, 'annotation')
        self.assertEqual(captured[0]['score_id'], captured[1]['score_id'])
        self.assertEqual(captured[1]['data_type'], 'TEXT')
        app.sync_score(row, 'annotation')
        self.assertEqual(len(captured), 2, 'A verified matching score should not be written again')

    def test_confirmed_package_requires_explicit_ids_and_validates_before_writing(self):
        app.initial_sample()
        tids = app.selected_ids()[:2]
        app.write('suggestions.json', [{'id': f'draft-{i}', 'trace_id': tid,
                   'kind': 'open_code_draft', 'status': 'pending',
                   'proposed_review_status': 'no_failure_observed', 'note': 'no failure observed'}
                  for i, tid in enumerate(tids)])
        with self.assertRaises(ValueError):
            app.confirm_drafts({'ids': ['draft-0', 'missing'], 'human_reviewed_and_confirmed': True})
        with self.assertRaises(ValueError):
            app.confirm_drafts({'ids': ['draft-0', 'draft-1']})
        self.assertEqual(len(app.reviewed_ids()), 0)
        app.confirm_drafts({'ids': ['draft-0', 'draft-1'], 'human_reviewed_and_confirmed': True})
        self.assertEqual(len(app.reviewed_ids()), 2)

    def test_bulk_read_requires_score_id_trace_and_exact_note(self):
        import hashlib
        app.initial_sample()
        tid = app.selected_ids()[0]
        row = app.annotation({'trace_id': tid, 'review_status': 'no_failure_observed', 'note': 'Exact note'})
        score = {'id': hashlib.sha256(('cartwheel:hw4:' + row['id']).encode()).hexdigest()[:32],
                 'traceId': tid, 'stringValue': 'Wrong text'}
        app.CLIENT = SimpleNamespace(api=SimpleNamespace(score_v_2=SimpleNamespace(
            get=lambda **_: SimpleNamespace(data=[score]))))
        self.assertEqual(app.verify_pending_notes()['pending_sync'], 1)
        score['stringValue'] = 'Exact note'
        self.assertEqual(app.verify_pending_notes()['pending_sync'], 0)


    def test_label_package_prevalidates_every_entry_before_any_write(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        app.annotation({'trace_id': tid, 'review_status': 'first_failure', 'note': 'Observed failure'})
        app.write('patterns.json', {'modes': [{'name': 'mode_one', 'version': 2, 'status': 'final', 'human_confirmed': True}]})
        draft = {'id': 'draft-one', 'trace_id': tid, 'mode': 'mode_one', 'definition_version': 2,
                 'label': 1, 'note': 'Complete-trace evidence', 'status': 'pending', 'author': 'ai'}
        app.write('label_proposals.json', {'rows': [draft, {**draft, 'id': 'draft-two', 'label': None}]})
        with self.assertRaises(ValueError):
            app.confirm_label_drafts({'ids': ['draft-one', 'draft-two'], 'human_reviewed_and_confirmed': True})
        self.assertEqual(app.current_labels(), [])
        with self.assertRaises(ValueError):
            app.confirm_label_drafts({'ids': ['draft-one']})
        app.write('label_proposals.json', {'rows': [{**draft, 'definition_version': 1}]})
        with self.assertRaises(ValueError):
            app.confirm_label_drafts({'ids': ['draft-one'], 'human_reviewed_and_confirmed': True})
        self.assertEqual(app.current_labels(), [])

    def test_label_verification_checks_current_version_and_note(self):
        row = {'id': 'judgment-one', 'definition_version': 2, 'note': 'Current evidence'}
        for comment in ('not json', '[]', json.dumps({'local_id': 'judgment-one', 'definition_version': 1, 'note': 'Current evidence'}), json.dumps({'local_id': 'judgment-one', 'definition_version': 2, 'note': 'Old evidence'})):
            self.assertFalse(app.label_comment_matches({'comment': comment}, row))
        self.assertTrue(app.label_comment_matches({'comment': json.dumps({'local_id': 'judgment-one', 'definition_version': 2, 'note': 'Current evidence'})}, row))

    def test_confirmed_label_keeps_ai_source_and_requires_fresh_confirmation(self):
        app.initial_sample()
        tid = app.selected_ids()[0]
        app.annotation({'trace_id': tid, 'review_status': 'first_failure', 'note': 'Observed failure'})
        app.write('patterns.json', {'modes': [{'name': 'mode_one', 'version': 1, 'status': 'final', 'human_confirmed': True}]})
        app.write('label_proposals.json', {'rows': [{'id': 'draft-one', 'trace_id': tid, 'mode': 'mode_one',
                  'definition_version': 1, 'label': 1, 'note': 'Complete-trace evidence', 'status': 'pending', 'author': 'ai'}]})
        app.confirm_label_drafts({'ids': ['draft-one'], 'human_reviewed_and_confirmed': True})
        row = app.current_labels()[0]
        self.assertEqual(row['source'], 'accepted_ai_draft')
        self.assertEqual(row['source_proposal_id'], 'draft-one')
        proposal = app.read('label_proposals.json')['rows'][0]
        self.assertEqual(proposal['author'], 'ai')
        self.assertEqual(proposal['decided_by'], 'human')
        with self.assertRaises(ValueError):
            app.confirm_label_drafts({'ids': ['draft-one'], 'human_reviewed_and_confirmed': True})


if __name__ == '__main__':
    unittest.main()
