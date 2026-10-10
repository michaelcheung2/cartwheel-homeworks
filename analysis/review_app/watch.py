"""Poll human annotations every two seconds; retain a resumable event log.

Run separately: uv run python -m analysis.review_app.watch
This watcher observes saved state. It never generates notes or labels.
"""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from analysis.helpers import _state


def main():
    log = Path(__file__).resolve().parent / '.cache' / 'review-watch.log'
    log.parent.mkdir(exist_ok=True)
    previous = None
    print(f'Polling annotations every 2 seconds; log: {log}', flush=True)
    while True:
        path = _state.state_path('annotations.json')
        current = path.read_text() if path.exists() else ''
        if current != previous:
            try:
                data = json.loads(current)
                rows = data.get('annotations', []) if isinstance(data, dict) else data
                event = {'timestamp': datetime.now(timezone.utc).isoformat(),
                         'event': 'annotation_content_changed',
                         'reviewed_trace_ids': [r['trace_id'] for r in rows if not r.get('deleted')],
                         'pending_sync': sum(r.get('sync', {}).get('status') != 'synced' for r in rows)}
                with log.open('a') as handle:
                    handle.write(json.dumps(event) + '\n')
                previous = current
            except json.JSONDecodeError:
                pass
        time.sleep(2)


if __name__ == '__main__':
    main()
