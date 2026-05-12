output "db_password" {
  value = var.db_password
}

output "aws_secret_key" {
  value = "super-secret-key"
}

output "api_key" {
  value = var.api_key
}

output "admin_role" {
  value = aws_iam_role.ecs_task_role.arn
}