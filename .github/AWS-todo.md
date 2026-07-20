# AWS Setup Checklist — xInvest Deploy (EC2 + ECR + docker-compose)

อ้างอิงจาก `docker-compose.yml`, `.github/workflows/deploy.yml`, `.env.production` ที่มีอยู่แล้วในโปรเจกต์

---

## Phase 1: IAM

### 1.1 IAM User สำหรับ GitHub Actions (push image ขึ้น ECR)
```bash
aws iam create-user --user-name xinvest-ci

aws iam attach-user-policy --user-name xinvest-ci \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPowerUser

aws iam create-access-key --user-name xinvest-ci
# เก็บ AccessKeyId + SecretAccessKey ไว้ — ใช้เป็น GitHub Secrets
```

### 1.2 IAM Role สำหรับ EC2 (pull image จาก ECR)
```bash
aws iam create-role --role-name xinvest-ec2-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"}, "Action": "sts:AssumeRole"}]
  }'

aws iam attach-role-policy --role-name xinvest-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly

aws iam create-instance-profile --instance-profile-name xinvest-ec2-profile
aws iam add-role-to-instance-profile \
  --instance-profile-name xinvest-ec2-profile --role-name xinvest-ec2-role
```

- [ ] IAM user `xinvest-ci` สร้างแล้ว
- [ ] IAM role `xinvest-ec2-role` + instance profile สร้างแล้ว

---

## Phase 2: ECR (Container Registry)

```bash
aws ecr create-repository --repository-name xinvest-backend --region ap-southeast-1
aws ecr create-repository --repository-name xinvest-frontend --region ap-southeast-1
```

### Lifecycle Policy (กัน storage cost บานปลาย)
```bash
cat > /tmp/lifecycle-policy.json <<'EOF'
{
  "rules": [{
    "rulePriority": 1,
    "description": "Keep only last 10 tagged images",
    "selection": {"tagStatus": "tagged", "tagPrefixList": ["latest"], "countType": "imageCountMoreThan", "countNumber": 10},
    "action": {"type": "expire"}
  }]
}
EOF
aws ecr put-lifecycle-policy --repository-name xinvest-backend --lifecycle-policy-text file:///tmp/lifecycle-policy.json
aws ecr put-lifecycle-policy --repository-name xinvest-frontend --lifecycle-policy-text file:///tmp/lifecycle-policy.json
```

จด Account ID (ใช้ประกอบ ECR_REGISTRY):
```bash
aws sts get-caller-identity --query Account --output text
```
`ECR_REGISTRY = <account-id>.dkr.ecr.ap-southeast-1.amazonaws.com`

- [ ] Repo `xinvest-backend` สร้างแล้ว
- [ ] Repo `xinvest-frontend` สร้างแล้ว
- [ ] Lifecycle policy ตั้งแล้วทั้งสอง repo
- [ ] จด Account ID / ECR_REGISTRY ไว้แล้ว

---

## Phase 3: Networking (VPC / Security Group)

```bash
aws ec2 create-security-group --group-name xinvest-sg \
  --description "xInvest production" --vpc-id <YOUR_VPC_ID>

SG_ID=<security-group-id>

# HTTP/HTTPS สู่สาธารณะ
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 443 --cidr 0.0.0.0/0

# SSH เฉพาะ IP ของเรา
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr <YOUR_IP>/32
```

**ห้ามเปิด 5432 (postgres), 6379 (redis), 8000/3000 (backend/frontend) สู่สาธารณะ** — nginx proxy ทุกอย่างผ่าน 80/443 อยู่แล้ว, Postgres เข้าผ่าน SSH tunnel (`docker-compose.yml` bind `127.0.0.1:5432:5432` ไว้แล้ว)

- [ ] Security group สร้างแล้ว
- [ ] เปิด 80/443 public
- [ ] เปิด 22 เฉพาะ IP ของเรา
- [ ] ยืนยันไม่ได้เปิด 5432/6379/8000/3000 สู่สาธารณะ

---

## Phase 4: EC2 Instance

```bash
aws ec2 create-key-pair --key-name xinvest-key --query 'KeyMaterial' --output text > xinvest-key.pem
chmod 400 xinvest-key.pem

aws ec2 run-instances \
  --image-id ami-0xxxxxxx \  # Ubuntu 22.04 LTS AMI (เช็ค AMI ID ล่าสุดของ region ที่ใช้)
  --instance-type t3.medium \
  --key-name xinvest-key \
  --security-group-ids $SG_ID \
  --iam-instance-profile Name=xinvest-ec2-profile \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":50,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=xinvest-prod}]'
```

**ขนาด instance:** เริ่มที่ `t3.medium` (2 vCPU / 4GB RAM) พอสำหรับ workload ปัจจุบัน (หลังตัด sentence-transformers/torch ออกจาก backend image แล้ว)

### 4.1 Elastic IP
```bash
aws ec2 allocate-address --domain vpc
aws ec2 associate-address --instance-id <instance-id> --allocation-id <allocation-id>
```

- [ ] EC2 instance สร้างแล้ว (region/AMI/instance type ตามต้องการ)
- [ ] EBS volume อย่างน้อย 50GB
- [ ] Elastic IP allocate + associate แล้ว
- [ ] จด Elastic IP ไว้แล้ว

---

## Phase 5: ตั้งค่าบนเครื่อง EC2

```bash
ssh -i xinvest-key.pem ubuntu@<Elastic-IP>

curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
sudo apt-get install -y docker-compose-plugin
# logout แล้ว ssh เข้าใหม่ให้ group docker มีผล

git clone https://github.com/yuttana76/xInvest.git /opt/xinvest
cd /opt/xinvest
git checkout master
```

### 5.1 `.env` (compose variable substitution)
```bash
cat > /opt/xinvest/.env <<EOF
ECR_REGISTRY=<account-id>.dkr.ecr.ap-southeast-1.amazonaws.com
IMAGE_TAG=latest
EOF
```

### 5.2 `.env.production`
แก้ค่า `CHANGE_ME` ในไฟล์ local ให้ครบก่อน copy ขึ้น server:
- `DJANGO_SUPERUSER_USERNAME` / `_EMAIL` / `_PASSWORD`
- `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `FRONTEND_URL`, `NEXT_PUBLIC_API_URL` → domain จริง
- `GEMINI_API_KEY`, `FC_API_USER`, `FC_API_PASSWORD`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`

```bash
scp -i xinvest-key.pem .env.production ubuntu@<Elastic-IP>:/opt/xinvest/.env.production
```

### 5.3 First-run ด้วยมือ
```bash
aws ecr get-login-password --region ap-southeast-1 | docker login --username AWS --password-stdin <ECR_REGISTRY>
docker compose -f docker-compose.yml up -d --build
docker compose -f docker-compose.yml logs -f migrate seed backend
```

- [ ] Docker + Compose plugin ติดตั้งบน EC2 แล้ว
- [ ] Repo clone ไว้ที่ `/opt/xinvest`, checkout `master`
- [ ] `.env` สร้างแล้ว (ECR_REGISTRY ถูกต้อง)
- [ ] `.env.production` แก้ `CHANGE_ME` ครบแล้ว copy ขึ้น server แล้ว
- [ ] `docker compose up -d --build` รันผ่าน, เช็ค log `migrate`/`seed`/`backend` ไม่มี error

---

## Phase 6: GitHub Secrets & Variables

ไปที่ repo → Settings → Secrets and variables → Actions

### Secrets
| Secret | ค่า |
|---|---|
| `AWS_ACCESS_KEY_ID` | จาก IAM user `xinvest-ci` |
| `AWS_SECRET_ACCESS_KEY` | จาก IAM user `xinvest-ci` |
| `AWS_REGION` | `ap-southeast-1` |
| `EC2_HOST` | Elastic IP |
| `EC2_USER` | `ubuntu` |
| `EC2_SSH_KEY` | เนื้อหาไฟล์ `xinvest-key.pem` ทั้งไฟล์ |
| `DEPLOY_PATH` | `/opt/xinvest` |
| `NEXT_PUBLIC_API_URL` | `https://<your-domain>/api` |

### Variables
| Variable | ค่า |
|---|---|
| `NEXT_PUBLIC_APP_NAME` | `xInvest` |
| `NEXT_PUBLIC_APP_TAGLINE` | ข้อความ tagline |

- [ ] Secrets ครบทั้ง 8 ตัว
- [ ] Variables ครบทั้ง 2 ตัว

---

## Phase 7: ทดสอบ Pipeline

1. GitHub → Actions → "Deploy to AWS" → Run workflow (`workflow_dispatch`) ทดสอบก่อน push จริง
2. เช็ค log ทุก step: build/push ECR, SSH deploy
3. เข้า `http://<Elastic-IP>` (หรือ domain) ดูว่าเว็บขึ้นจริง

- [ ] Manual `workflow_dispatch` รันผ่านสำเร็จ
- [ ] เว็บเข้าถึงได้จาก public URL

---

## Phase 8 (แนะนำ ไม่บังคับ): TLS

```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d <your-domain>
```
ต้องมี domain ชี้มาที่ Elastic IP ก่อน (ผ่าน Route 53 หรือ DNS provider อื่น)

- [ ] Domain ชี้มาที่ Elastic IP แล้ว
- [ ] Certbot ออก certificate สำเร็จ
- [ ] เข้าเว็บผ่าน `https://` ได้ปกติ
