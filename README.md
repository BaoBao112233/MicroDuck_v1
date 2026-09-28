# MicroDuck Software Bring-up

## MicroDuck Software Bring-up MVP v0.1

Workspace này tập trung duy nhất vào MicroDuck. MVP hiện dùng mock hardware/dry-run, không gửi lệnh tới robot thật và không cần cài thư viện ngoài.

Python đi kèm Codex trên máy này có thể chạy các lệnh sau:

```powershell
$py = "C:\Users\kevin\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
& $py -m microduck_bringup --dry-run doctor
& $py -m microduck_bringup --dry-run scan
& $py -m microduck_bringup --dry-run monitor --samples 3
& $py -m microduck_bringup --dry-run neutral
& $py -m microduck_bringup --dry-run safety-check --joint left_knee --target 999
& $py -m microduck_bringup --dry-run estop --reason "demo"
& $py -m unittest discover -s tests -v
```

Chạy toàn bộ demo bằng một lệnh:

```powershell
.\scripts\demo-microduck.ps1
```

Cấu hình ở `config/robot.yaml`. File này dùng cú pháp JSON, đồng thời là YAML hợp lệ, để runtime có thể đọc bằng thư viện chuẩn. Servo ID, giới hạn khớp và IMU orientation hiện là cấu hình khởi tạo để kiểm thử software; phải đối chiếu đúng revision phần cứng trước khi dùng trên robot thật.

## Cấu trúc MicroDuck

- `microduck_bringup/`: runtime, mock hardware, cấu hình và safety layer.
- `config/robot.yaml`: joint map, servo ID, limits và IMU orientation.
- `scripts/demo-microduck.ps1`: demo end-to-end bằng một lệnh.
- `tests/`: regression tests MicroDuck.
- `logs/`: structured runtime logs sinh tự động.

Mã PuppyPi cũ đã được chuyển vào `_archive/puppypi-virtual-lab/` để có thể khôi phục khi cần. Nó không còn thuộc luồng chạy hoặc tài liệu chính của workspace.
