import sys
from pathlib import Path

FILE = "starter_rag.py"


def load_file():
    if not Path(FILE).exists():
        print("FAIL: starter_rag.py not found")
        sys.exit(1)
    return Path(FILE).read_text()


tf = load_file()

score = 100


def fail(msg, penalty):
    global score
    print(f"FAIL: {msg}")
    score -= penalty


if 'Answer this:' in tf:
    fail("weak prompt template (no structured instructions)", 20)

if "You are" not in tf and "system" not in tf.lower():
    fail("missing system-style instruction / role prompting", 15)


if "context" not in tf.lower():
    fail("no context injection detected (RAG missing)", 30)

if "retriev" not in tf.lower():
    fail("no retrieval step found (vector DB / docs missing)", 20)


if "timeout" not in tf:
    fail("missing request timeout handling", 10)

if "try" not in tf or "except" not in tf:
    fail("missing error handling (try/except)", 10)

if "raise_for_status" not in tf:
    fail("missing HTTP error validation (raise_for_status)", 5)


if "retry" not in tf.lower():
    fail("no retry logic for failures", 15)

if "for " not in tf and "while " not in tf:
    fail("no retry loop structure detected", 5)


if "async" not in tf and "thread" not in tf and "concurrent" not in tf:
    fail("no concurrency/async approach (may be slow under load)", 5)

if "batch" not in tf.lower():
    fail("no batching strategy detected", 5)

print("SCORE:", score)

if score >= 85:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL")
    sys.exit(1)