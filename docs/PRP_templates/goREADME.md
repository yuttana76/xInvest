Go Best Practices & Standards (Mandatory)
เพื่อให้ระบบ Trading มีความเสถียรและดูแลรักษาง่าย โปรดปฏิบัติตามมาตรฐานดังนี้:

1. Project Structure (Standard Layout)
   [ ] ปฏิบัติตาม golang-standards/project-layout
   [ ] Standard Project Layout: จัดโครงสร้างตาม Go Project Layout (https://github.com/golang-standards/project-layout)

/cmd: จุดเริ่มต้นของแอปพลิเคชัน (main.go)

/internal: Code ที่เป็น Private (Service อื่นเรียกใช้ไม่ได้)

/pkg: Library ที่อนุญาตให้ Service อื่นเรียกใช้ได้

/api: ไฟล์นิยาม API (Swagger/Proto files)

2. Error Handling (The Go Way)
   [ ] No Panics: ห้ามใช้ panic() ใน Production logic ให้ใช้การส่งกลับ error เสมอ

[ ] Error Wrapping: ใช้ fmt.Errorf("... %w", err) เพื่อรักษา Context ของ Error ต้นทาง

[ ] Check Errors: ทุกฟังก์ชันที่มีการคืนค่า Error ต้องถูกตรวจสอบ (Don't ignore \_)

3. Concurrency Safety
   [ ] Race Condition: ต้องรันเทสต์ด้วย go test -race ก่อน Deploy

[ ] Context Usage: ทุกฟังก์ชันที่เกี่ยวข้องกับ I/O หรือ API ต้องรับ context.Context เพื่อจัดการ Timeout และ Cancellation

4. Code Quality & Linting
   [ ] Gofmt: ต้องรัน go fmt หรือใช้ goimports เพื่อจัดฟอร์แมตโค้ดอัตโนมัติ

[ ] Golangci-lint: ต้องผ่านการตรวจสอบจาก Linter มาตรฐาน (เช่น staticcheck, errcheck)

[ ] Explicit over Implicit: เน้นการเขียนโค้ดที่อ่านง่ายมากกว่าการเขียนโค้ดที่สั้นแต่ซับซ้อน

5. Performance for Trading
   [ ] Avoid Reflect: หลีกเลี่ยงการใช้ reflect ใน Hot path (จุดที่มีการประมวลผลเยอะ)

[ ] Memory Allocation: ใช้ sync.Pool สำหรับ Object ที่ใช้บ่อยเพื่อลดภาระของ Garbage Collector (GC)
