resource "aws_iam_policy" "bedrock_access" {
  name = "bedrock-inference-policy"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["bedrock:*"]
        Resource = "*"
      }
    ]
  })
}