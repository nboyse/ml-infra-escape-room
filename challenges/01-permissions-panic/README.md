# Challenge 01: Permissions Panic

**Story**: The service cannot call Amazon Bedrock.

**Task**: Fix the IAM policy (least privilege).

**Files**: `broken_policy.tf`

**Success**: Only `bedrock:InvokeModel` is allowed on specific model ARNs.

**Test**: Run python check_solution.py (SCORE > 85 and PASS - next challenge)