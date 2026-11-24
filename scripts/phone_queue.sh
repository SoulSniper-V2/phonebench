#!/bin/zsh
# Serialized phone work: wait until the iPhone is connected, then run every pending job. The runner skips trials
# that already finished, so rerunning this is always safe. Clef stops at Cloudflare's daily free allocation;
# the loop retries after the 00:00 UTC reset. PHONEBENCH_DEVICE comes from ~/.config/phonebench/env.
cd "$(dirname "$0")/.."
source ~/.config/phonebench/env 2>/dev/null
export PHONEBENCH_DEVICE STRANDS_URL
log=runs/batch-queue.log
connected() { npx -y phonedriver devices 2>/dev/null | grep -qi "${PHONEBENCH_DEVICE#ios:}"; }
run() { echo "== $(date -u +%FT%TZ) $*" >> $log; python3 -u -m phonebench.runner --device-kind phone --out runs "$@" >> $log 2>&1; }
while [ ! -e STOP ]; do
  until connected; do sleep 60; done
  for m in clef-omni clef-flash clef; do connected && run --providers $m --repeats 1; done
  connected && run --providers jev-1.14 jev-1.13 gemini-decision-1 --first-repeat 1 --repeats 2
  connected && run --providers strands-2b --repeats 3
  connected && run --providers jev-1.14 strands-2b --obs-mode tree --repeats 1
  echo "== $(date -u +%FT%TZ) pass complete" >> $log
  sleep 1800
done
