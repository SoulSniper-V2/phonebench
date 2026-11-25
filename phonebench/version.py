"""Version stamps written into every trial, so a result can always be traced to the exact suite and harness."""
import hashlib
from pathlib import Path
import subprocess

__version__ = '0.7.0'
_HERE = Path(__file__).parent


def _digest(*names):
    h = hashlib.sha256()
    for n in names:
        h.update((_HERE / n).read_bytes())
    return h.hexdigest()[:12]


def stamp():
    """suite = task definitions; harness = everything that shapes what the model sees and can do."""
    try:
        pd = subprocess.run(['npx', '-y', 'phonedriver', '--version'], capture_output=True, text=True, timeout=60).stdout.split()[-1]
    except Exception:
        pd = None
    return {'phonebench': __version__, 'suite': _digest('tasks.py'),
            'harness': _digest('env.py', 'runner.py', 'safety.py', 'device.py', 'providers.py'), 'phonedriver': pd}
