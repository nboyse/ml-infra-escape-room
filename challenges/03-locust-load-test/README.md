# Challenge 03: Locust Load Test

**Task**: Run a load test and determine how many instances you need.

```bash
locust -f locustfile.py --host=http://localhost:8000 --users 50 --spawn-rate 10 --run-time 60s
```

Observe when latency spikes or errors appear. Record findings in load_test_results.md

**Success**: You understand how locust works - this one isn't marked by a script but simply a demonstration of load testing for those who havent used it before