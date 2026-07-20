#!/bin/bash

# Database Backup Script for xInvest (Development)
# This script dumps the 'db' container's database to the 'backups' folder.

# 1. Configuration - Set your project root path for CRON compatibility
PROJECT_ROOT="/Users/mpamdev03/projects/python/xInvest"
CONTAINER_NAME="xinvest-db-1"
BACKUP_DIR="$PROJECT_ROOT/backups"
LOG_FILE="$PROJECT_ROOT/backups/backup.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="db_backup_${TIMESTAMP}.sql"

# 2. Change directory to project root
cd "$PROJECT_ROOT" || exit 1

# 3. Load environment variables from .env.dev
if [ -f .env.dev ]; then
    export $(grep -v '^#' .env.dev | xargs)
else
    echo "$(date) - Error: .env.dev file not found." >> "$LOG_FILE"
    exit 1
fi

# 4. Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "$(date) - Starting backup for database: $POSTGRES_DB..." >> "$LOG_FILE"

# 5. Perform pg_dump
# We use PGPASSWORD to avoid prompt
/usr/local/bin/docker exec -e PGPASSWORD="$POSTGRES_PASSWORD" "$CONTAINER_NAME" pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "$BACKUP_DIR/$FILENAME"

if [ $? -eq 0 ]; then
    echo "$(date) - Backup successful: $FILENAME" >> "$LOG_FILE"
    # Optional: Delete backups older than 7 days
    # find "$BACKUP_DIR" -name "db_backup_*.sql" -mtime +7 -delete
else
    echo "$(date) - Error: Backup failed." >> "$LOG_FILE"
    exit 1
fi
