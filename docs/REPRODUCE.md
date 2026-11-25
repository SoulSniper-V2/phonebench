# Reproducing PhoneBench

There are three levels, from "check our numbers" to "run it on your own phone".

## 1. Check the published numbers (no device, one minute)

Every number in a release follows from its `trials.jsonl`. CI re-derives `summary.json` from the trials on every push.
Locally:

```sh
python3 -m phonebench.report results/v0.7    # rewrites summary.json + RESULTS.md from trials.jsonl
git diff --stat results/                      # empty: the published numbers reproduce
```

`grader_audit.json` lists every trial a human reviewed, with the verdict and a one-line reason, so you can see
where the automatic grader was checked and where it was corrected.

## 2. Re-run the simulator track (no phone)

The simulator is the most reproducible setting: a fixed device, a fixed OS, the stock sample contacts and no
account state.

| | Used for the published results |
|---|---|
| Device | iPhone 17 Pro simulator |
| OS | iOS 26.5 |
| Driver | phonedriver 0.1.7 |
| Tasks | every task tagged `sim` in `phonebench/tasks.py` (built-in apps + Safari) |

```sh
npx -y phonedriver boot "iPhone 17 Pro"
npx -y phonedriver devices                     # copy the sim:<udid>
PHONEBENCH_DEVICE=sim:<udid> PHONEBENCH_SESSION=phonebench-sim \
  python3 -m phonebench.runner --device-kind sim --out runs-sim --providers jev-1.14 --repeats 3
python3 -m phonebench.regrade runs-sim --release results/mine
python3 -m phonebench.report results/mine
```

Live web content (Google results in Safari) still varies a little, which is why each cell is repeated.

## 3. Run the phone track

You need an iPhone in Developer Mode, connected over USB, with the apps the tasks use. Your phone has its own
apps, accounts, feeds and network, so absolute times and some task difficulty will differ. The comparison between
models on the same phone is what carries over.

```sh
cp config/private.example.json config/private.json   # optional: personal-data tasks (school portal)
python3 -m phonebench.runner --providers jev-1.14 gemini-decision-1 --repeats 3
```

Or use `scripts/phone_queue.sh`. It waits for the phone, runs every pending job, resumes after a disconnect, and
retries Clef after Cloudflare's daily reset.

## Models and access

| Provider id | Model | Access |
|---|---|---|
| `jev-1.14`, `jev-1.13` | TypeSafe Jev | API key (`TYPESAFE_API_KEY`) |
| `gemini-decision-1` | Google Gemini Decision | API key (`GEMINI_API_KEY`), free tier, 50k input tokens/min |
| `clef`, `clef-flash`, `clef-omni` | Cloudflare Clef | Workers AI (`CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`), daily free allocation |
| `strands-2b` | Strands Decider 2B (open weights) | local: `strands-decider serve …` (`STRANDS_URL`) |

Keys go in `.env` or `~/.config/phonebench/env`, which are never committed. Adding a provider means one entry in
`phonebench/providers.py`, mapping our question format to its wire format.

## Version stamps

Every trial records `versions`: the phonebench version, a hash of the task definitions (`suite`), a hash of
everything that shapes what the model sees and can do (`harness`) and the phonedriver version. It also records the
device model and OS, but never the device id. `RESULTS.md` lists the stamps a release contains. Compare scores only
within one suite hash.
