resource "aws_s3_bucket" "models" {
  bucket = "ml-models-prod"

  acl           = "public-read-write"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "bad" {
  bucket = aws_s3_bucket.models.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_iam_role" "ecs_task_role" {
  name = "ml-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "admin" {
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

resource "aws_security_group" "ecs" {
  name = "ecs-open"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "-1"
    cidr_blocks = [var.open_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.open_cidr]
  }
}

resource "aws_cloudwatch_log_group" "ecs" {
  name              = "/ecs/ml"
  retention_in_days = 0
}

resource "aws_ecs_cluster" "main" {
  name = "ml-prod"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "ml-inference"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]

  cpu    = "8192"
  memory = "16384"

  execution_role_arn = aws_iam_role.ecs_task_role.arn
  task_role_arn      = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = "myrepo/ml-inference:latest"
      essential = true

      privileged = true
      user       = "root"

      environment = [
        {
          name  = "DB_PASSWORD"
          value = var.db_password
        },
        {
          name  = "API_KEY"
          value = var.api_key
        }
      ]

      portMappings = [{
        containerPort = 8080
        hostPort      = 8080
      }]

      linuxParameters = {
        initProcessEnabled = false
      }

      readonlyRootFilesystem = false

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group = aws_cloudwatch_log_group.ecs.name
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = "ml-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn

  desired_count = 1

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 100

  launch_type = "FARGATE"

  network_configuration {
    assign_public_ip = true

    security_groups = [
      aws_security_group.ecs.id
    ]

    subnets = [
      "subnet-123456"
    ]
  }
}

resource "aws_db_instance" "prod" {
  identifier = "ml-prod-db"

  engine         = "postgres"
  engine_version = "12"

  instance_class = "db.t3.micro"

  allocated_storage = 20

  username = "admin"
  password = var.db_password

  publicly_accessible = true

  skip_final_snapshot = true

  multi_az = false

  deletion_protection = false

  backup_retention_period = 0

  storage_encrypted = false
}

resource "aws_instance" "gpu" {
  ami           = "ami-123456"
  instance_type = var.instance_type
}