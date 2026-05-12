import re
import sys

TF_FILE = "broken_policy.tf"

with open(TF_FILE, "r") as f:
    tf = f.read()


match = re.search(r'policy\s*=\s*jsonencode\((\{.*?\})\)', tf, re.DOTALL)

if not match:
    print("FAIL: Could not find policy block")
    sys.exit(1)


raw_policy = match.group(1)

policy_text = raw_policy

score = 100

if "bedrock:*" in policy_text:
    print("FAIL: wildcard action detected (bedrock:*)")
    score -= 35

if "*\"" in policy_text or "Resource = \"*\"" in policy_text:
    print("FAIL: wildcard resource detected")
    score -= 35

if "InvokeModel" not in policy_text:
    print("FAIL: missing bedrock:InvokeModel")
    score -= 30

print("\nSCORE:", score)

if score >= 85:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL")
    sys.exit(1)