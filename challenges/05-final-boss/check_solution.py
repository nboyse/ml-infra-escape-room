import json
import subprocess
import sys
from collections import defaultdict

class Result:
    def __init__(self):
        self.score = 100
        self.messages = []

    def fail(self, points, message):
        self.score -= points
        self.messages.append(("FAIL", message))

    def warn(self, points, message):
        self.score -= points
        self.messages.append(("WARN", message))

    def pass_(self, message):
        self.messages.append(("PASS", message))


result = Result()

subprocess.run(
    ["terraform", "init", "-backend=false"],
    check=True,
)

subprocess.run(
    ["terraform", "validate"],
    check=True,
)

subprocess.run(
    [
        "terraform",
        "plan",
        "-refresh=false",
        "-out=tfplan",
    ],
    check=True,
)

plan_output = subprocess.run(
    ["terraform", "show", "-json", "tfplan"],
    capture_output=True,
    text=True,
    check=True,
)

plan = json.loads(plan_output.stdout)


resources = []

for rc in plan.get("resource_changes", []):
    change = rc.get("change", {})
    after = change.get("after", {})

    resources.append(
        {
            "address": rc.get("address"),
            "type": rc.get("type"),
            "name": rc.get("name"),
            "values": after,
        }
    )

def get_resources(resource_type):
    return [r for r in resources if r["type"] == resource_type]

for sg in get_resources("aws_security_group"):
    ingress = sg["values"].get("ingress", [])

    for rule in ingress:
        cidrs = rule.get("cidr_blocks", [])
        from_port = rule.get("from_port")
        to_port = rule.get("to_port")

        if "0.0.0.0/0" in cidrs:
            if from_port == 22:
                result.fail(
                    20,
                    f"{sg['address']} exposes SSH to the internet",
                )
            else:
                result.warn(
                    10,
                    f"{sg['address']} allows public ingress on port {from_port}",
                )

def has_encryption(bucket_address):
    for b in get_resources("aws_s3_bucket"):
        if b["address"] == bucket_address:
            if b["values"].get("server_side_encryption_configuration"):
                return True
            break

    for enc in get_resources("aws_s3_bucket_server_side_encryption_configuration"):
        if enc["address"].startswith(f"aws_s3_bucket_server_side_encryption_configuration.{bucket_address.split('.')[-1]}") or \
           enc["values"].get("bucket") == bucket_address:
            return True
    return False


for bucket in get_resources("aws_s3_bucket"):
    if not has_encryption(bucket["address"]):
        result.fail(
            15,
            f"{bucket['address']} missing S3 encryption",
        )
    else:
        result.pass_(f"{bucket['address']} has encryption enabled")


for bucket in get_resources("aws_s3_bucket"):
    name = bucket["values"].get("bucket", "")
    if "model" in name.lower() or "models" in name.lower():
        if not has_encryption(bucket["address"]):
            result.fail(
                20,
                f"Model bucket {bucket['address']} lacks encryption"
            )

for bucket in get_resources("aws_s3_bucket"):
    acl = bucket["values"].get("acl")

    if acl in ["public-read", "public-read-write"]:
        result.fail(
            25,
            f"{bucket['address']} is public",
        )


for policy in get_resources("aws_iam_policy"):
    doc = policy["values"].get("policy", "")

    if "*" in doc:
        result.fail(
            20,
            f"{policy['address']} contains wildcard permissions",
        )
        
for db in get_resources("aws_db_instance"):
    if db["values"].get("publicly_accessible"):
        result.fail(
            20,
            f"{db['address']} is publicly accessible",
        )

for resource in resources:
    values_str = json.dumps(resource["values"]).lower()
    address = resource["address"]

    suspicious = ["AKIA", "BEGIN PRIVATE KEY", "-----BEGIN"]

    if resource["type"] == "aws_db_instance":
        if "password" in resource["values"]:
            result.warn(
                5,
                f"{address} has password (this is normal but consider using AWS Secrets Manager)"
            )
        continue

    for s in suspicious:
        if s.lower() in values_str:
            result.warn(
                10,
                f"{address} may contain plaintext secrets"
            )
            
for db in get_resources("aws_db_instance"):
    if not db["values"].get("multi_az"):
        result.warn(
            10,
            f"{db['address']} is not Multi-AZ",
        )

for asg in get_resources("aws_autoscaling_group"):
    desired = asg["values"].get("desired_capacity", 0)

    if desired < 2:
        result.warn(
            10,
            f"{asg['address']} desired capacity < 2",
        )
        
for tg in get_resources("aws_lb_target_group"):
    hc = tg["values"].get("health_check")

    if not hc:
        result.warn(
            10,
            f"{tg['address']} missing health checks",
        )


for db in get_resources("aws_db_instance"):
    if not db["values"].get("deletion_protection"):
        result.warn(
            5,
            f"{db['address']} missing deletion protection",
        )

EXPENSIVE_INSTANCES = [
    "p4d.24xlarge",
    "p5.48xlarge",
    "u-24tb1.metal",
]


for instance in get_resources("aws_instance"):
    instance_type = instance["values"].get("instance_type")

    if instance_type in EXPENSIVE_INSTANCES:
        result.fail(
            15,
            f"{instance['address']} uses expensive instance type {instance_type}",
        )


def has_lifecycle_config(bucket_address):
    for b in get_resources("aws_s3_bucket"):
        if b["address"] == bucket_address and b["values"].get("lifecycle_rule"):
            return True
    
    for lc in get_resources("aws_s3_bucket_lifecycle_configuration"):
        if (lc["values"].get("bucket") == bucket_address or 
            lc["address"].endswith("." + bucket_address.split(".")[-1])):
            return True
    return False


for bucket in get_resources("aws_s3_bucket"):
    if not has_lifecycle_config(bucket["address"]):
        result.warn(
            5,
            f"{bucket['address']} missing lifecycle policy",
        )

if not get_resources("aws_cloudwatch_metric_alarm"):
    result.warn(
        10,
        "No CloudWatch alarms configured",
    )

for lb in get_resources("aws_lb"):
    attrs = lb["values"]

    if not attrs.get("access_logs"):
        result.warn(
            5,
            f"{lb['address']} missing access logs",
        )

config = plan.get("configuration", {})
required_providers = config.get("provider_config", {}) or config.get("required_providers", {})

if not config.get("required_version"):
    result.warn(5, "Terraform version not pinned")

if not required_providers:
    result.warn(5, "Provider versions not pinned")
else:
    result.pass_("Provider versions are configured")
    
for resource in resources:
    tags = resource["values"].get("tags")

    if tags is not None:
        required_tags = ["Environment", "Owner"]

        missing = [
            tag for tag in required_tags if tag not in tags
        ]

        if missing:
            result.warn(
                2,
                f"{resource['address']} missing tags {missing}",
            )


for instance in get_resources("aws_instance"):
    instance_type = instance["values"].get("instance_type", "")

    if instance_type.startswith("p"):
        result.warn(
            5,
            f"{instance['address']} uses GPU instance - validate necessity",
        )


def is_bucket_encrypted(bucket_address):
    for enc in get_resources("aws_s3_bucket_server_side_encryption_configuration"):
        enc_bucket = enc["values"].get("bucket")
        if enc_bucket == bucket_address or enc["address"].endswith("." + bucket_address.split(".")[-1]):
            return True
    return False


for bucket in get_resources("aws_s3_bucket"):
    name = str(bucket["values"].get("bucket", "")).lower()
    if "model" in name or "models" in name:
        if is_bucket_encrypted(bucket["address"]):
            result.pass_(f"Model bucket {bucket['address']} has encryption")
        else:
            result.fail(
                20,
                f"Model bucket {bucket['address']} lacks encryption",
            )
            
print("\nRESULTS\n")

for status, message in result.messages:
    print(f"[{status}] {message}")

print(f"\nFINAL SCORE: {result.score}/100")

if result.score >= 80:
    print("PASS")
    sys.exit(0)
else:
    print("FAIL")
    sys.exit(1)
    
