# Challenge 04: Cost explosion

**Story**:  
Someone shipped a "smart" research agent that uses Bedrock. It's working... but it's extremely expensive and keeps making unnecessary calls.

**Your Task**:  
Fix the `costly_agent.py` script so it:
- Uses significantly fewer tokens
- Stops wasteful repeated calls
- Adds cost guardrails
- Still answers the question properly

**Success Criteria**:
- Total tokens used drops dramatically
- It still gives a good final answer
- Bonus: Add visible cost estimation

Run it with: `python costly_agent.py`