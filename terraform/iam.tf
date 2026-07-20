# --- CI user: GitHub Actions pushes images to ECR with this identity ---

resource "aws_iam_user" "ci" {
  name = "${var.project}-ci"
}

resource "aws_iam_user_policy_attachment" "ci_ecr_push" {
  user       = aws_iam_user.ci.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser"
}

resource "aws_iam_access_key" "ci" {
  user = aws_iam_user.ci.name
}

# --- EC2 instance role: lets the running instance pull images from ECR ---

resource "aws_iam_role" "ec2" {
  name = "${var.project}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ec2_ecr_read" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project}-ec2-profile"
  role = aws_iam_role.ec2.name
}
