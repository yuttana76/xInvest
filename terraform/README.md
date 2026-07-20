# xInvest AWS Infrastructure (Terraform)

Provisions everything listed in `.github/AWS-todo.md` Phases 1-4: IAM (CI user + EC2 role), ECR repos + lifecycle policy, security group, EC2 instance, Elastic IP. Phase 5 onward (server setup, GitHub Secrets, TLS) is still manual — see that file.

## Usage

```bash
cd terraform
terraform init
terraform plan -var="allowed_ssh_cidr=<YOUR_IP>/32"
terraform apply -var="allowed_ssh_cidr=<YOUR_IP>/32"
```

Required variable: `allowed_ssh_cidr` (your IP, e.g. `1.2.3.4/32`) — no default, on purpose, so SSH is never left open to `0.0.0.0/0` by accident.

Optional variables (see `variables.tf` for full list/defaults): `aws_region`, `instance_type`, `root_volume_size`, `public_key_path`.

After `apply`, get the values needed for GitHub Secrets / Phase 5:
```bash
terraform output elastic_ip
terraform output ecr_backend_url
terraform output ecr_frontend_url
terraform output ci_access_key_id
terraform output -raw ci_secret_access_key   # sensitive, shown only on request
```

## Teardown

```bash
terraform destroy -var="allowed_ssh_cidr=<YOUR_IP>/32"
```
Removes every resource this module created (EC2, EIP, security group, ECR repos + images, IAM user/role). ECR repos are created empty by Terraform and destroy will refuse to delete a repo containing images — either push a lifecycle policy that clears it first or delete images manually before destroying if you hit that.

## State

This module has no remote backend configured — state is local (`terraform.tfstate`, already gitignored). For a team setup, migrate to an S3 backend with DynamoDB locking before more than one person runs this.
