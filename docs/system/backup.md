วิธีใช้งาน: เปิด Terminal ในโปรเจกต์แล้วรันคำสั่ง:

bash
./scripts/backup_db.sh 3. วิธีการกู้คืนข้อมูล

# (Restore)

หากต้องการนำไฟล์ Backup กลับมาใช้งาน (เช่น เมื่อย้ายเครื่องหรือข้อมูลพัง) สามารถใช้คำสั่งนี้ครับ:

bash

# เปลี่ยนชื่อไฟล์ให้ตรงกับที่คุณมีในโฟลเดอร์ backups

cat backups/db_backup_XXXXXXXX_XXXXXX.sql | docker exec -i xinvest-db-1 psql -U invest_user -d invest_db
