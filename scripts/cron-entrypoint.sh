#!/bin/sh
# Internal Docker Cron Entrypoint for Database Backups

# 1. Ensure we have the backup directory
mkdir -p /backups

# 2. Create the crontab entry
# Note: $BACKUP_SCHEDULE should be passed as an environment variable (e.g., "59 23 * * *")
LOG_FILE="/backups/backup.log"

CRON_COMMAND="(echo \"\$(date) - Starting daily backup...\" >> $LOG_FILE && PGPASSWORD=$POSTGRES_PASSWORD pg_dump -h db -U $POSTGRES_USER $POSTGRES_DB > /backups/daily_backup_\$(date +\%Y\%m\%d_\%H\%M\%S).sql 2>> $LOG_FILE && echo \"\$(date) - Daily backup successful.\" >> $LOG_FILE) || echo \"\$(date) - ERROR: Daily backup failed.\" >> $LOG_FILE"

echo "$BACKUP_SCHEDULE $CRON_COMMAND" > /etc/crontabs/root

echo "--------------------------------------------------------"
echo "Backup Scheduler Started"
echo "Schedule: $BACKUP_SCHEDULE"
echo "Database: $POSTGRES_DB"
echo "--------------------------------------------------------"

# 3. Start crond in foreground with log level 2
exec crond -f -l 2
