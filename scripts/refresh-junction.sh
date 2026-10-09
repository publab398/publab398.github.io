#!/usr/bin/env bash
# Capture the current game in a disposable Editor, then import and rebuild the site.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
site_root=$(cd -- "$script_dir/.." && pwd)
game_root=$(realpath "${1:-$site_root/../fps-cdx}")
capture_dir=$(mktemp -d -t publab398-junction-XXXXXX)
printf 'Capture output: %s\n' "$capture_dir"
bash "$game_root/scripts/capture-site-screenshots.sh" "$game_root/scripts/site-shots-junction.json" "$capture_dir"
python3 "$script_dir/import-screenshots.py" "$capture_dir" --shot cover --shot overview --shot gameplay
python3 - "$site_root" <<'PY'
import datetime as dt
from pathlib import Path
import re
import sys

updated = dt.datetime.now(dt.timezone(dt.timedelta(hours=9))).isoformat(timespec='seconds')
for name in ('junction-55', 'rules'):
    path = Path(sys.argv[1]) / 'content/project-cdx/features' / f'{name}.md'
    prefix, metadata, body = path.read_text(encoding='utf-8').split('+++', 2)
    line = f'updated = "{updated}"'
    if re.search(r'^updated = .*$', metadata, flags=re.M):
        metadata = re.sub(r'^updated = .*$', line, metadata, flags=re.M)
    else:
        metadata = re.sub(r'^(date = .*)$', lambda match: match[0] + '\n' + line, metadata, flags=re.M)
    path.write_text(prefix + '+++' + metadata + '+++' + body, encoding='utf-8')
PY
site_python="$site_root/.venv/bin/python"
if [[ ! -x "$site_python" ]]; then site_python=python3; fi
"$site_python" "$script_dir/build.py"
"$site_python" "$script_dir/check.py"
