FROM golang:1.25-alpine

# ติดตั้ง dependencies ที่จำเป็น (git, curl, build-base)
RUN apk add --no-cache git curl build-base

# ติดตั้ง air ผ่าน official install script (หลีกเลี่ยง ghcr 403 และ build error)
RUN curl -sSfL https://raw.githubusercontent.com/air-verse/air/master/install.sh | sh -s -- -b $(go env GOPATH)/bin

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# รันด้วย air (binary อยู่ใน /go/bin/air)
CMD ["air", "-c", ".air.toml"]