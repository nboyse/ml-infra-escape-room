import sys
from pathlib import Path

FILE = "costly_agent.py"


def load_file():
    if not Path(FILE).exists():
        print("FAIL: costly_agent.py not found")
        sys.exit(1)
    return Path(FILE).read_text()


code = load_file()

score = 100


def fail(msg, penalty):
    global score
    print(f"FAIL: {msg}")
    score -= penalty


call_count = code.count("call_bedrock(")

if call_count > 2:
    fail(f"too many LLM calls detected ({call_count}) — inefficient multi-step pipeline", 40)

elif call_count == 2:
    fail("still multiple sequential LLM calls — could likely be single-pass", 5)

if "Critique and improve" in code:
    fail("unnecessary critique step detected (step 2 pattern)", 15)

if "Expand this answer" in code:
    fail("unnecessary expansion step detected (token inflation)", 15)

if "Research everything you can" in code:
    fail("over-broad prompting detected (expensive and uncontrolled)", 10)

if "budget" not in code.lower() and "limit" not in code.lower():
    fail("no cost or budget guardrails detected", 5)

if "tokens_used" not in code:
    fail("no token tracking usage detected", 10)

if "compress" not in code.lower() and "summar" not in code.lower():
    fail("no evidence of prompt/result compression strategy", 5)

if code.count("res1") > 0 and code.count("res2") > 0 and code.count("res3") > 0:
    fail("multi-stage refinement chain detected (likely unnecessary)", 15)

if "final answer" in code.lower() and call_count >= 3:
    fail("final answer produced after excessive intermediate steps", 10)

print("SCORE:", score)

if score >= 85:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL")
    sys.exit(1)