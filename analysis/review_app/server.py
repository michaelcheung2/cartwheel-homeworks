"""HW4 human review: live Langfuse evidence, durable notes and explicit labels.

Run from the repository root: uv run python -m analysis.review_app.server
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
import threading
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from analysis.helpers import _state, langfuse_io, selection
from analysis.helpers.normalization import normalize_trace
from observability.instrument import load_env
from scenarios.export_langfuse import _jsonable, _scenario_id
from analysis.review_app import hw5

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LOCK = threading.RLock()
CORPUS: list[dict] = []
SOURCE: dict = {}
CLIENT = None


def now():
    return datetime.now(timezone.utc).isoformat()


def read(name, default=None):
    return _state.read_json(_state.state_path(name), default)


def write(name, data):
    _state.write_json(_state.state_path(name), data)


def attributes(record):
    metadata = record.get('metadata') or {}
    attrs = metadata.get('attributes') or {}
    if isinstance(attrs, str):
        attrs = json.loads(attrs)
    return {**attrs, **metadata}


def content(value):
    if isinstance(value, list):
        parts = [str(p.get('content', '')) for m in value if isinstance(m, dict)
                 for p in m.get('parts', []) if p.get('type') == 'text']
        if parts:
            return '\n'.join(parts)
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)


def prepare_record(raw):
    """Normalize each trace individually; never merge away its identifier.

    Keep raw observations because the shared compact normalizer omits span
    parents, exception status and some model messages needed by human review.
    """
    record = normalize_trace(raw)
    if not re.fullmatch('[0-9a-f]{32}', record['id']):
        raise ValueError('Expected a real Langfuse trace identifier')
    observations = sorted(raw.get('observations') or [],
                          key=lambda o: (o.get('startTime') or '', o.get('id') or ''))
    steps = [{'id': 'user', 'role': 'user', 'text': content(raw.get('input'))}]
    tools = []
    for obs in observations:
        attrs = attributes(obs)
        if obs.get('type') == 'TOOL' or attrs.get('gen_ai.operation.name') == 'execute_tool':
            name = attrs.get('gen_ai.tool.name') or obs.get('name')
            tools.append(name)
            steps.append({'id': obs['id'], 'role': 'tool', 'name': name,
                          'input': obs.get('input'), 'output': obs.get('output'),
                          'error': obs.get('statusMessage'), 'level': obs.get('level'),
                          'retrieval': name in ('search_help_center', 'get_policy'),
                          'timestamp': obs.get('startTime')})
        elif obs.get('type') == 'GENERATION':
            # Preserve intermediate text; omit a duplicate of the final reply.
            value = obs.get('output')
            if isinstance(value, list):
                for message in value:
                    for part in message.get('parts') or []:
                        if part.get('type') == 'text' and part.get('content', '').strip():
                            text = part['content']
                            if text.strip() != content(raw.get('output')).strip():
                                steps.append({'id': obs['id'], 'role': 'assistant', 'text': text})
    steps.append({'id': 'reply', 'role': 'assistant', 'text': content(raw.get('output'))})
    record['steps'] = steps
    record['raw_observations'] = observations
    record['features'].update(tool_call_count=len(tools), distinct_tools=len(set(tools)),
                              has_retrieval=int(any(t in ('get_policy', 'search_help_center') for t in tools)),
                              tokens=sum(int((o.get('usageDetails') or {}).get('total', 0) or 0)
                                         for o in observations if o.get('type') == 'GENERATION'),
                              turn_count=2)
    record['tool_names'] = tools
    record['text'] = '\n'.join(content(s) for s in steps)
    record['permalink'] = f"http://localhost:3000/project/cartwheel-dev/traces/{record['id']}"
    return record


def initialize_state():
    """Archive instructor fixtures once, without deleting student analysis."""
    state = _state.state_root()
    manifest = read('sample_manifest.json')
    if manifest:
        if manifest.get('assignment') != 'HW4' or manifest.get('dataset') != 'own_hw3_support':
            raise ValueError('Existing review manifest belongs to another dataset; preserve and inspect it first')
        return
    annotations = read('annotations.json', {'annotations': []})
    notes = annotations.get('annotations', []) if isinstance(annotations, dict) else annotations
    patterns = read('patterns.json', {'modes': []})
    if notes or patterns.get('modes') or read('suggestions.json', []):
        raise ValueError('Existing human review work found. Refusing to replace it.')
    backup = state / 'starter_demo_backup'
    backup.mkdir(parents=True, exist_ok=True)
    for name in ('annotations.json', 'patterns.json', 'suggestions.json', 'store_traces.json',
                 'demo_annotations.json', 'splits.json', 'judges', 'labels'):
        src = state / name
        dst = backup / name
        if src.exists():
            if dst.exists():
                raise ValueError(f'Backup already exists: {dst}; inspect before initializing')
            shutil.move(str(src), str(dst))
    write('annotations.json', {'annotations': [], 'history': []})
    write('patterns.json', {'modes': [], 'history': [], 'status': 'open_coding'})
    write('suggestions.json', [])
    write('sample_manifest.json', {
        'assignment': 'HW4', 'dataset': 'own_hw3_support', 'created_at': now(),
        'seed': 20261010, 'product_dimension': 'user_role',
        'dimension_values': ['shopper', 'merchant', 'support'],
        'dimension_chosen_before_review': True, 'optional_workshop': 'skipped',
        'batches': [], 'required_distinct_traces': 100,
    })


def refresh_corpus(offline=False):
    global CORPUS, SOURCE, CLIENT
    load_env()
    scenarios = [json.loads(line) for line in (ROOT / 'scenarios/support_scenarios.jsonl').read_text().splitlines() if line.strip()]
    allowed = {s['scenario_id'] if 'scenario_id' in s else s['id'] for s in scenarios}
    if offline:
        cached = read('corpus_source.json', {})
        reason = cached.get('offline_reason')
        if not reason:
            raise ValueError('Offline mode needs a recorded reason for temporary Langfuse unavailability')
        raw = json.loads((ROOT / 'traces/support_traces.json').read_text())
        if isinstance(raw, dict):
            raw = raw['traces']
        SOURCE = {'store': 'offline_export', 'fetched_at': now(), 'offline_reason': reason}
    else:
        CLIENT = langfuse_io._client()
        summaries = []
        page = 1
        while True:
            batch = CLIENT.api.trace.list(page=page, limit=100).data or []
            summaries.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        def fetch(summary):
            return _jsonable(CLIENT.api.trace.get(summary.id))
        with ThreadPoolExecutor(max_workers=6) as executor:
            raw = list(executor.map(fetch, summaries))
        SOURCE = {'store': 'live_langfuse', 'fetched_at': now(), 'project': 'cartwheel-dev'}
    raw = [r for r in raw if _scenario_id(r) in allowed]
    normalized = [prepare_record(r) for r in raw]
    if len({r['id'] for r in normalized}) != len(normalized):
        raise ValueError('Duplicate trace identifiers')
    if {_scenario_id(r) for r in raw} != allowed:
        raise ValueError('The live dataset is missing some final HW3 scenarios')
    lookup = {s.get('scenario_id', s.get('id')): s for s in scenarios}
    for r in normalized:
        s = lookup[r['meta']['scenario_id']]
        r['scenario_context'] = {'opening_message': s.get('opening_message'),
                                 'extra_metadata': s.get('extra_metadata'),
                                 'requirement_reference': s.get('expected', {}).get('source')}
    normalized.sort(key=lambda r: (r.get('timestamp') or '', r['id']))
    CORPUS = normalized
    write('corpus_source.json', {**SOURCE, 'trace_count': len(CORPUS), 'scenario_count': len(allowed)})
    (HERE / '.cache').mkdir(exist_ok=True)
    _state.write_json(HERE / '.cache/traces.json', CORPUS)
    print(f"Loaded {len(CORPUS)} live traces from {len(allowed)} scenarios", flush=True)


def initial_sample():
    manifest = read('sample_manifest.json')
    if manifest['batches']:
        return
    seed = manifest['seed']
    random_ids = {r['id'] for r in random.Random(seed).sample(CORPUS, 15)}
    pool = [r for r in CORPUS if r['id'] not in random_ids]
    vectors = selection._standardize([selection._feature_vector(r) for r in pool])
    assigned = selection._kmeans(vectors, 8, seed)
    groups = defaultdict(list)
    for i, group in enumerate(assigned):
        groups[group].append(i)
    representatives = []
    for group, indices in sorted(groups.items()):
        center = [sum(vectors[i][d] for i in indices) / len(indices) for d in range(5)]
        groups[group] = sorted(indices, key=lambda i: (sum((a-b)**2 for a,b in zip(vectors[i], center)), pool[i]['id']))
    while len(representatives) < 15:
        for group in sorted(groups):
            if groups[group] and len(representatives) < 15:
                i = groups[group].pop(0)
                representatives.append({'trace_id': pool[i]['id'], 'method': 'cluster_representative',
                                        'cluster': group, 'reason': 'Nearest available member to standardized feature centroid'})
    uniform = [{'trace_id': r['id'], 'method': 'uniform', 'reason': 'Uniform random draw without replacement'}
               for r in CORPUS if r['id'] in random_ids]
    manifest['batches'] = [{'id': 'breadth_1', 'target': 30, 'created_at': now(),
                            'entries': uniform + representatives, 'cluster_features': list(selection._FEATURES),
                            'cluster_count': len(groups)}]
    write('sample_manifest.json', manifest)


def selected_ids():
    return [e['trace_id'] for b in read('sample_manifest.json')['batches'] for e in b['entries']]


def reviewed_ids():
    return {a['trace_id'] for a in read('annotations.json')['annotations']
            if not a.get('deleted') and a.get('review_status') in ('first_failure', 'no_failure_observed')}


def current_labels():
    rows = {}
    for path in _state.state_path('labels').glob('*.jsonl'):
        for row in _state.read_jsonl(path):
            rows[(row['trace_id'], row['mode'])] = row
    return list(rows.values())


def label_comment_matches(score, row):
    try:
        saved = json.loads(score.get('comment') or '{}')
    except (ValueError, TypeError):
        return False
    return isinstance(saved, dict) and saved.get('definition_version') == row.get('definition_version') and saved.get('local_id') == row['id'] and saved.get('note') == row['note']


def sync_score(row, kind, *, defer=False):
    """Stable score ids make retries update the same Langfuse judgment."""
    if CLIENT is None:
        raise ValueError('Langfuse unavailable; judgment saved locally and pending synchronization')
    if kind == 'annotation':
        value = ('[WITHDRAWN] ' if row.get('deleted') else '') + row['note']
        name, datatype = 'hw4_open_code', 'TEXT'
        key = row['id']
    else:
        name, value, datatype = row['mode'], row['label'], 'NUMERIC'
        key = row['trace_id'] + ':' + row['mode']
    score_id = hashlib.sha256(('cartwheel:hw4:' + key).encode()).hexdigest()[:32]
    # Ingestion may complete after the first verification window. On retry,
    # confirm an already matching score before emitting another write event.
    if not defer:
        try:
            scores = CLIENT.api.score_v_2.get(trace_id=row['trace_id'], name=name).data or []
            for score in scores:
                saved = _jsonable(score)
                actual = saved.get('stringValue') if datatype == 'TEXT' else saved.get('value')
                if saved.get('id') == score_id and actual == value and (kind != 'label' or label_comment_matches(saved, row)):
                    return {'status': 'synced', 'score_id': score_id, 'verified_at': now()}
        except Exception:
            # The write/read path below retains and reports any service error.
            pass
    CLIENT.create_score(trace_id=row['trace_id'], observation_id=row.get('observation_id'),
                        name=name, value=value, data_type=datatype, score_id=score_id,
                        comment=json.dumps({'note': row.get('note'), 'quote': row.get('quote'),
                                            'human_confirmed': True, 'withdrawn': bool(row.get('deleted')),
                                            'definition_version': row.get('definition_version'),
                                            'source': row.get('source'),
                                            'source_proposal_id': row.get('source_proposal_id'),
                                            'local_id': row['id']}, ensure_ascii=False))
    if defer:
        return {'status': 'pending', 'score_id': score_id}
    CLIENT.flush()
    # Verify ingestion rather than claiming a flush alone proves persistence.
    import time
    for attempt in range(5):
        scores = CLIENT.api.score_v_2.get(trace_id=row['trace_id'], name=name).data or []
        for score in scores:
            s = _jsonable(score)
            actual = s.get('stringValue') if datatype == 'TEXT' else s.get('value')
            if s.get('id') == score_id and actual == value and (kind != 'label' or label_comment_matches(s, row)):
                return {'status': 'synced', 'score_id': score_id, 'verified_at': now()}
        time.sleep(0.5 * (attempt + 1))
    raise RuntimeError('Langfuse score not yet visible; saved locally, retry synchronization')


def annotation(payload, *, defer_sync=False):
    tid = payload.get('trace_id')
    if tid not in selected_ids():
        raise ValueError('Only a selected trace can be marked reviewed; context turns do not count')
    status = payload.get('review_status')
    if status not in ('first_failure', 'no_failure_observed'):
        raise ValueError('Choose first failure or no failure observed')
    note = str(payload.get('note', '')).strip()
    if not note:
        raise ValueError('Write a free form observation before saving')
    data = read('annotations.json')
    old = next((a for a in data['annotations'] if a['trace_id'] == tid and not a.get('deleted')), None)
    row = {**(old or {}), 'id': old['id'] if old else str(uuid.uuid4()), 'trace_id': tid,
           'review_status': status, 'note': note, 'quote': str(payload.get('quote', '')),
           'step_id': payload.get('step_id'), 'author': 'human', 'updated_at': now(),
           'source': payload.get('source', 'human_written'),
           'source_suggestion_id': payload.get('source_suggestion_id'),
           'sync': {'status': 'pending'}}
    step = next((s for r in CORPUS if r['id'] == tid for s in r['steps'] if s['id'] == row['step_id']), None)
    if step and step['id'] not in ('user', 'reply'):
        row['observation_id'] = step['id']
    if old:
        data['history'].append({**old, 'superseded_at': now()})
        data['annotations'] = [a for a in data['annotations'] if a['id'] != old['id']]
    data['annotations'].append(row)
    write('annotations.json', data)
    try:
        row['sync'] = sync_score(row, 'annotation', defer=defer_sync)
    except Exception as exc:
        row['sync'] = {'status': 'pending', 'error': str(exc)}
    write('annotations.json', data)
    return row


def label(payload, *, defer_sync=False):
    mode = next((m for m in read('patterns.json')['modes'] if m['name'] == payload.get('mode')
                 and m.get('status') == 'final' and m.get('human_confirmed')), None)
    if not mode:
        raise ValueError('Structured labels require a human-confirmed final mode')
    if not re.fullmatch('[a-z][a-z0-9]*(?:_[a-z0-9]+)*', mode['name']):
        raise ValueError('Failure mode names must use snake_case')
    tid = payload.get('trace_id')
    if tid not in reviewed_ids() or tid not in selected_ids():
        raise ValueError('Review this selected trace first')
    value = payload.get('label')
    if type(value) is not int or value not in (0, 1):
        raise ValueError('Choose 0 = absent or 1 = present explicitly')
    if not payload.get('inspected_complete_trace'):
        raise ValueError('Confirm you inspected the complete trace for this mode')
    row = {'id': str(uuid.uuid4()), 'trace_id': tid, 'mode': mode['name'], 'label': value,
           'note': str(payload.get('note', '')).strip(), 'author': 'human', 'created_at': now(),
           'definition_version': mode.get('version', 1), 'sync': {'status': 'pending'},
           'source': 'human_written'}
    if not row['note']:
        raise ValueError('Record evidence or a reason for this judgment')
    proposals = read('label_proposals.json', {'rows': []})
    proposal = None
    if payload.get('source_proposal_id'):
        proposal = next((p for p in proposals['rows'] if p['id'] == payload['source_proposal_id']), None)
        if not proposal or proposal['trace_id'] != tid or proposal['mode'] != mode['name'] or proposal['definition_version'] != mode.get('version', 1):
            raise ValueError('Label proposal does not match the trace and current mode version')
        row.update(source='accepted_ai_draft' if proposal.get('label') == value else 'corrected_ai_draft',
                   source_proposal_id=proposal['id'])
    path = _state.state_path('labels', mode['name'] + '.jsonl')
    _state.append_jsonl(path, row)
    try:
        row['sync'] = sync_score(row, 'label', defer=defer_sync)
    except Exception as exc:
        row['sync'] = {'status': 'pending', 'error': str(exc)}
    _state.append_jsonl(path, row)
    if proposal:
        proposal.update(status='accepted' if proposal.get('label') == value else 'corrected',
                        decided_by='human', decided_at=now(), accepted_label=value,
                        human_reason=row['note'])
        write('label_proposals.json', proposals)
    return row


def verify_labels():
    """Verify exact trace, value and stable ID; never write remote scores."""
    if CLIENT is None:
        raise ValueError('Langfuse unavailable; labels remain pending')
    scores = {}
    for mode in read('patterns.json')['modes']:
        if mode.get('status') != 'final':
            continue
        page = 1
        while True:
            batch = CLIENT.api.score_v_2.get(name=mode['name'], page=page, limit=100).data or []
            scores.update((s['id'], s) for v in batch if (s := _jsonable(v)))
            if len(batch) < 100:
                break
            page += 1
    for row in current_labels():
        sid = hashlib.sha256(('cartwheel:hw4:' + row['trace_id'] + ':' + row['mode']).encode()).hexdigest()[:32]
        score = scores.get(sid)
        if score and score.get('traceId') == row['trace_id'] and score.get('name') == row['mode'] and score.get('value') == row['label'] and label_comment_matches(score, row):
            row['sync'] = {'status': 'synced', 'score_id': sid, 'verified_at': now()}
            _state.append_jsonl(_state.state_path('labels', row['mode'] + '.jsonl'), row)
    return snapshot()['progress']


def confirm_label_drafts(payload):
    """Prevalidate an explicitly reviewed set before saving any judgment."""
    ids = payload.get('ids')
    if not payload.get('human_reviewed_and_confirmed') or not isinstance(ids, list) or not ids or len(ids) != len(set(ids)):
        raise ValueError('Provide distinct draft IDs and explicit human review confirmation')
    rows = {p['id']: p for p in read('label_proposals.json', {'rows': []})['rows']}
    modes = {m['name']: m for m in read('patterns.json')['modes'] if m.get('status') == 'final' and m.get('human_confirmed')}
    selected, reviewed = set(selected_ids()), reviewed_ids()
    for sid in ids:
        r = rows.get(sid)
        if not r or r.get('status') != 'pending' or r['trace_id'] not in selected & reviewed or r['mode'] not in modes or r['definition_version'] != modes[r['mode']].get('version', 1) or type(r.get('label')) is not int or r['label'] not in (0, 1) or not r.get('note', '').strip():
            raise ValueError('Every draft must be pending, binary, evidenced and match a reviewed trace and current final definition')
    for sid in ids:
        r = rows[sid]
        label({'trace_id': r['trace_id'], 'mode': r['mode'], 'label': r['label'],
               'note': r['note'], 'source_proposal_id': sid,
               'inspected_complete_trace': True}, defer_sync=True)
    if CLIENT is not None:
        CLIENT.flush()
        return verify_labels()
    return snapshot()['progress']


def withdraw_annotation(payload):
    data = read('annotations.json')
    row = next((a for a in data['annotations'] if a['trace_id'] == payload.get('trace_id')
                and not a.get('deleted')), None)
    if not row:
        raise ValueError('No active review to withdraw')
    data['history'].append({**row, 'superseded_at': now()})
    row.update(deleted=True, deleted_at=now(), sync={'status': 'pending'})
    write('annotations.json', data)
    try:
        row['sync'] = sync_score(row, 'annotation')
    except Exception as exc:
        row['sync'] = {'status': 'pending', 'error': str(exc)}
    write('annotations.json', data)
    return row


def suggestion_decision(payload, *, defer_sync=False):
    data = read('suggestions.json')
    row = next((s for s in data if s['id'] == payload.get('id')), None)
    if not row or row.get('status', 'pending') != 'pending':
        raise ValueError('No pending suggestion with that id')
    decision = payload.get('decision')
    if decision not in ('accepted', 'rejected') or not str(payload.get('reason', '')).strip():
        raise ValueError('Accept or reject explicitly and explain your reason')
    if not payload.get('inspected_trace'):
        raise ValueError('Inspect the returned trace before deciding')
    if decision == 'accepted' and row.get('kind') == 'open_code_draft':
        annotation({'trace_id': row['trace_id'], 'review_status': row['proposed_review_status'],
                    'note': payload['reason'], 'quote': row.get('quote', ''),
                    'step_id': row.get('step_id', 'reply'), 'source': 'accepted_ai_draft',
                    'source_suggestion_id': row['id']}, defer_sync=defer_sync)
    row.update(status=decision, human_reason=payload['reason'], decided_at=now(), decided_by='human')
    write('suggestions.json', data)
    return row


def verify_pending_notes():
    """Read all open-code scores once per page and verify exact values."""
    if CLIENT is None:
        raise ValueError('Langfuse unavailable; notes remain pending')
    scores = {}
    page = 1
    while True:
        batch = CLIENT.api.score_v_2.get(name='hw4_open_code', page=page, limit=100).data or []
        scores.update((s['id'], s) for value in batch if (s := _jsonable(value)))
        if len(batch) < 100:
            break
        page += 1
    data = read('annotations.json')
    for row in data['annotations']:
        sid = hashlib.sha256(('cartwheel:hw4:' + row['id']).encode()).hexdigest()[:32]
        score = scores.get(sid)
        expected = ('[WITHDRAWN] ' if row.get('deleted') else '') + row['note']
        if score and score.get('traceId') == row['trace_id'] and score.get('stringValue') == expected:
            row['sync'] = {'status': 'synced', 'score_id': sid, 'verified_at': now()}
    write('annotations.json', data)
    return snapshot()['progress']


def confirm_drafts(payload):
    """Save a specifically confirmed package; no implicit default selection."""
    ids = payload.get('ids')
    if not payload.get('human_reviewed_and_confirmed') or not isinstance(ids, list) or not ids:
        raise ValueError('Provide explicit reviewed draft IDs and human confirmation')
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate draft IDs')
    data = {s['id']: s for s in read('suggestions.json')}
    if any(i not in data or data[i].get('kind') != 'open_code_draft'
           or data[i].get('status') != 'pending' or data[i]['trace_id'] not in selected_ids() for i in ids):
        raise ValueError('Every ID must be a pending review draft for a selected trace')
    for sid in ids:
        suggestion_decision({'id': sid, 'decision': 'accepted', 'reason': data[sid]['note'],
                             'inspected_trace': True}, defer_sync=True)
    if CLIENT is not None:
        CLIENT.flush()
        return verify_pending_notes()
    return snapshot()['progress']


def next_batch():
    manifest = read('sample_manifest.json')
    used = set(selected_ids())
    if not used.issubset(reviewed_ids()):
        raise ValueError('Finish open coding the current selected batch first')
    if any(b['id'] == 'role_2' for b in manifest['batches']):
        raise ValueError('Depth searches come next; candidate modes need human review before selection')
    rng = random.Random(manifest['seed'] + 1)
    entries = []
    for role in manifest['dimension_values']:
        pool = [r for r in CORPUS if r['id'] not in used and r['meta'].get('role') == role]
        if len(pool) < 10:
            raise ValueError(f'Insufficient remaining traces for role {role}')
        entries.extend({'trace_id': r['id'], 'method': 'role_stratified', 'role': role,
                        'reason': f'Uniform within {role}; dimension chosen before review'} for r in rng.sample(pool, 10))
    manifest['batches'].append({'id': 'role_2', 'target': 30, 'created_at': now(), 'entries': entries})
    write('sample_manifest.json', manifest)
    return manifest


def snapshot():
    patterns = read('patterns.json')
    labels = current_labels()
    selected = set(selected_ids())
    reviewed = selected & reviewed_ids()
    final = [m for m in patterns['modes'] if m.get('status') == 'final' and m.get('human_confirmed')]
    applicable = [l for l in labels if l['trace_id'] in reviewed and l['mode'] in {m['name'] for m in final}
                  and l.get('definition_version') == next(m.get('version', 1) for m in final if m['name'] == l['mode'])]
    return {'source': SOURCE, 'corpus': CORPUS, 'manifest': read('sample_manifest.json'),
            'annotations': read('annotations.json'), 'patterns': patterns, 'suggestions': read('suggestions.json'),
            'labels': labels, 'label_proposals': read('label_proposals.json', {'rows': []}),
            'spec': (ROOT / 'SPEC.md').read_text(),
            'spec_proposal': (ROOT / 'analysis/report/hw4-spec-clarification.md').read_text()
            if (ROOT / 'analysis/report/hw4-spec-clarification.md').exists() else '',
            'progress': {'selected': len(selected), 'reviewed': len(reviewed), 'required': 100,
                         'final_modes': len(final), 'judgments': len(applicable),
                         'judgments_remaining': len(reviewed) * len(final) - len(applicable),
                         'pending_sync': sum(a.get('sync', {}).get('status') != 'synced' for a in read('annotations.json')['annotations'])
                         + sum(l.get('sync', {}).get('status') != 'synced' for l in applicable)}}


def retry_sync():
    data = read('annotations.json')
    for row in data['annotations']:
        if row.get('sync', {}).get('status') != 'synced':
            try:
                row['sync'] = sync_score(row, 'annotation')
            except Exception as exc:
                row['sync'] = {'status': 'pending', 'error': str(exc)}
    write('annotations.json', data)
    for row in current_labels():
        if row.get('sync', {}).get('status') != 'synced':
            try:
                row['sync'] = sync_score(row, 'label')
            except Exception as exc:
                row['sync'] = {'status': 'pending', 'error': str(exc)}
            _state.append_jsonl(_state.state_path('labels', row['mode'] + '.jsonl'), row)
    return snapshot()['progress']


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, payload, kind='application/json'):
        data = payload if isinstance(payload, bytes) else json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', kind + '; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == '/':
            return self.reply(200, (HERE / 'index.html').read_bytes(), 'text/html')
        if path in ('/api/state', '/api/updates'):
            with LOCK:
                data = snapshot()
                if path == '/api/updates':
                    data.pop('corpus')
                    data.pop('spec')
                return self.reply(200, data)
        if path == '/api/health':
            return self.reply(200, {'ok': True, 'source': SOURCE, 'traces': len(CORPUS)})
        if path == '/api/hw5':
            with LOCK:
                return self.reply(200, hw5.snapshot())
        self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        # Only the local UI may mutate state. No cross-origin form requests.
        origin = self.headers.get('Origin')
        if origin and origin != 'http://' + self.headers.get('Host', ''):
            return self.reply(403, {'error': 'Origin does not match the local review interface'})
        if 'application/json' not in self.headers.get('Content-Type', ''):
            return self.reply(415, {'error': 'Send JSON'})
        try:
            length = int(self.headers.get('Content-Length', 0))
            if not 0 < length < 100000:
                raise ValueError('Invalid request size')
            payload = json.loads(self.rfile.read(length))
            with LOCK:
                actions = {'/api/annotation': annotation, '/api/label': label,
                           '/api/withdraw-review': withdraw_annotation,
                           '/api/suggestion': suggestion_decision,
                           '/api/next-batch': lambda _: next_batch(),
                           '/api/retry-sync': lambda _: retry_sync()}
                actions['/api/confirm-drafts'] = confirm_drafts
                actions['/api/verify-sync'] = lambda _: verify_pending_notes()
                actions['/api/confirm-label-drafts'] = confirm_label_drafts
                actions['/api/verify-label-sync'] = lambda _: verify_labels()
                actions['/api/hw5-review'] = hw5.review
                action = actions.get(urlparse(self.path).path)
                if not action:
                    return self.reply(404, {'error': 'Not found'})
                self.reply(200, action(payload))
        except (ValueError, KeyError, TypeError) as exc:
            self.reply(400, {'error': str(exc)})
        except Exception as exc:
            self.reply(500, {'error': str(exc)})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8020)
    parser.add_argument('--offline-reason', help='Only for temporary live Langfuse unavailability')
    args = parser.parse_args()
    initialize_state()
    if args.offline_reason:
        write('corpus_source.json', {'offline_reason': args.offline_reason})
    refresh_corpus(offline=bool(args.offline_reason))
    initial_sample()
    print(f'Review interface: http://localhost:{args.port}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
