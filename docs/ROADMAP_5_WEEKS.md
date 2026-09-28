# MicroDuck software roadmap — 5 tuần

Mốc bắt đầu: 2026-09-28. Mục tiêu gần nhất: **thứ Ba 2026-10-06** có demo quan sát được và báo cáo pass/fail, không cần robot thật.

## Definition of Done ngày 2026-10-06

- Web 3D hiển thị đủ 14 joint theo đúng ID map MicroDuck.
- Nút Neutral, Motion demo và E-stop hoạt động; E-stop chặn motion cho đến khi reset/reload.
- CLI dry-run chạy được `doctor`, `scan`, `monitor`, `neutral`, `safety-check`, `estop`.
- Một lệnh test chạy xanh; log demo ghi lại state transition và vi phạm joint limit.
- Trang kết quả ghi rõ phần nào simulated, phần nào chưa hardware-validated.

## Tuần 1 — baseline và demo (28/09–06/10)

- [x] Tạo dry-run bring-up và safety layer.
- [x] Tạo viewer 3D local, telemetry mô phỏng và E-stop.
- [x] Tổng hợp nguồn, tách MicroDuck khỏi Open Duck Mini.
- [x] Đồng bộ Servo ID map với tutorial XL330.
- [ ] Hiển thị Servo ID bên cạnh joint trong viewer.
- [ ] Xuất một report JSON sau demo: test status, joint map, events, timestamp.
- [ ] Quay/chụp bằng chứng demo ngày 06/10.

## Tuần 2 — hardware abstraction và replay (07/10–13/10)

- Tạo `RobotIO` interface và backend `MockRobotIO`; không làm serial thật trước khi contract ổn định.
- Định nghĩa telemetry/event schema có version.
- Cho viewer đọc replay log thay vì dữ liệu hard-code.
- Thêm watchdog, stale-data indication và state-machine tests.

## Tuần 3 — bench integration an toàn (14/10–20/10)

- Thêm backend Dynamixel/OpenRB sau feature flag, mặc định tắt torque.
- Implement scan/read-only: model, ID, voltage, temperature và communication errors.
- Tool kiểm tra từng servo một; lưu zero/direction/offset theo robot serial/revision.
- Không chạy policy; chỉ kiểm chứng bus và sensor ở bench.

## Tuần 4 — neutral và low-risk motion (21/10–27/10)

- Kết nối IMU, hiệu chỉnh mount quaternion và xác nhận trục.
- Neutral có rate/position/current limits, support rig và rollback về torque-off.
- Chạy từng khớp biên độ nhỏ, sau đó pose sequence có kiểm soát.
- Viewer hiển thị measured vs commanded angle, voltage và fault state.

## Tuần 5 — policy readiness (28/10–03/11)

- Validator cho ONNX manifest: joint order, shapes, rate và robot compatibility.
- Shadow mode: policy chạy nhưng không phát lệnh; ghi command + observation để review.
- Supported first-step test trên bề mặt trống, có người giữ và E-stop sẵn sàng.
- Tổng kết go/no-go cho walking; chưa đạt gate nào thì giữ mock/shadow mode.

## Ưu tiên

P0: safety state machine, ID contract, logs, E-stop, deterministic tests.  
P1: replay, measured-vs-commanded telemetry, IMU validation.  
P2: UI polish, colors, exploded view và motion library.

