#!/bin/zsh
# Wait for Cloudflare's daily free allocation to reset (00:00 UTC) and for the phone to be free, then run Clef.
cd "$(dirname "$0")/.."
until [ "$(date -u +%H)" = "00" ] || [ "$(date -u +%H%M)" -lt 2000 -a "$(date -u +%d)" != "$(cat .clef_day 2>/dev/null)" ]; do sleep 60; done
while pgrep -f "phonebench.runner --device-kind phone" >/dev/null; do sleep 30; done
# PHONEBENCH_DEVICE comes from ~/.config/phonebench/env; wait until that phone is actually connected.
source ~/.config/phonebench/env 2>/dev/null; export PHONEBENCH_DEVICE
until npx -y phonedriver devices 2>/dev/null | grep -qi "${PHONEBENCH_DEVICE#ios:}"; do sleep 60; done
for m in clef-omni clef-flash clef; do
  python3 -u -m phonebench.runner --device-kind phone --providers $m --repeats 1 --out runs >> runs/batch-clef.log 2>&1
done
echo CLEF-QUEUE-DONE >> runs/batch-clef.log
