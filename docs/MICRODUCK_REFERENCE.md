# MicroDuck — tổng hợp nguồn và baseline kỹ thuật

Tài liệu này tổng hợp các nguồn cộng đồng được rà soát ngày 2026-09-28. Repo này chỉ lưu kết luận, liên kết và cấu hình do nhóm tự duy trì; không sao chép nguyên mã/CAD của dự án khác. Khi cần nhập code hoặc model, phải kiểm tra license và cố định commit/tag nguồn.

## Kết luận nhanh

- Baseline nên dùng cho bản dựng hiện tại: **14 × Dynamixel XL330-M288-T + OpenRB-150 + Raspberry Pi Zero 2 W + BNO08x + nguồn servo 6 V**.
- Robot có 14 khớp điều khiển (10 chân, 4 đầu/cổ). Servo miệng thứ 15 là tùy chọn và không nằm trong action space của policy đi bộ.
- Luồng phần mềm: IMU + lệnh người dùng → observation → ONNX policy → 14 joint targets ở 50 Hz → bus Dynamixel Protocol 2.0, 1 Mbps.
- Trước khi đi thật: scan đúng 14 ID, xác nhận hướng/zero/offset từng khớp, IMU frame, điện áp, E-stop và neutral pose có giá đỡ.
- Không xem Open Duck Mini là cùng một robot. Nó là dự án tiền thân/tham khảo về sim-to-real, cao khoảng 42 cm và có cơ khí/phần cứng khác.

## Vai trò từng nguồn

| Nguồn | Giá trị dùng trong repo này | Lưu ý |
|---|---|---|
| [microduck-replica](https://github.com/fanhao375/microduck-replica) | Cây động học, kích thước/khối lượng, joint range, BOM, CAD và hai hướng XL330/HD-1910 | Phân biệt tuyệt đối bản XL330 và HD-1910; không dùng STL mô phỏng làm chi tiết in |
| [Microduck-build-tutorial](https://github.com/AI-FanGe/Microduck-build-tutorial) | Baseline thực dụng cho Pi Zero 2 W, OpenRB-150, XL330, BNO08x, image và ONNX deployment | Đây là nguồn chính cho Servo ID trong `config/robot.yaml` |
| [Open_Duck_Mini_Viewer](https://github.com/mertcookimg/Open_Duck_Mini_Viewer) | Tham khảo UX: 3D pose, joint sliders, motion, telemetry, E-stop, axes/explode | Dành cho Open Duck Mini; chỉ học pattern UI, không dùng geometry/joint contract làm MicroDuck truth |
| [microduck-diy](https://github.com/ScrapMeta/microduck-diy) | Cách tổ chức knowledge base, upstream lock, test bench, firmware IMU-to-DXL và nguyên tắc giữ tương thích official ecosystem | Các khẳng định phần cứng phải đối chiếu lại theo revision cụ thể |
| [awesome-microduck](https://github.com/joeynyc/awesome-microduck) | Bản đồ ecosystem: official runtime, RL, policies, simulator, tools và community | Danh mục tổng hợp, không phải specification authority |
| [Open_Duck_Mini](https://github.com/apirrone/Open_Duck_Mini) | Bối cảnh lineage, MuJoCo/RL và kinh nghiệm sim-to-real | Không trộn BOM, CAD, policy hoặc calibration với MicroDuck |
| [OpenELAB build guide](https://openelab.io/blogs/robotics/microduck-build-guide-openelab) | Checklist lắp ráp, nguồn, servo setup, first boot, first motion và cảnh báo an toàn | Bài diễn giải tutorial; khi xung đột, ưu tiên repo/code revision đang dùng |

## Hardware contract đề xuất

### Servo ID

| ID | Joint | ID | Joint |
|---:|---|---:|---|
| 1 | `right_ankle` | 8 | `left_hip_pitch` |
| 2 | `right_knee` | 9 | `left_hip_roll` |
| 3 | `right_hip_pitch` | 10 | `left_hip_yaw` |
| 4 | `right_hip_roll` | 11 | `head_pitch` |
| 5 | `right_hip_yaw` | 12 | `neck_pitch` |
| 6 | `left_ankle` | 13 | `head_yaw` |
| 7 | `left_knee` | 14 | `head_roll` |

ID 15 (`mouth`) là tùy chọn. Bus khuyến nghị: Dynamixel Protocol 2.0, 1 Mbps, Return Delay Time 0. Các thay đổi protection/shutdown phải được đánh giá điện áp và rủi ro, không áp dụng tự động.

### Power và bus

```text
6 V battery -> switch -> OpenRB-150 / XL330 bus
             -> regulated 5 V -> Raspberry Pi Zero 2 W
Pi Zero 2 W --USB data--> OpenRB-150
Pi GPIO2/3 --I2C--> BNO08x
```

Ba nhánh servo được tài liệu hóa: phải `5→4→3→2→1`, trái `10→9→8→7→6`, đầu/cổ `12→11→13→14`. Thứ tự dây vật lý có thể thay đổi, nhưng ID-to-joint contract không đổi. Luôn kiểm tra polarity và common ground bằng đồng hồ trước khi cấp nguồn.

## Software contract của repo

- `microduck_bringup`: doctor, scan, monitor, neutral, safety-check và E-stop; mặc định dry-run.
- `config/robot.yaml`: joint map, giới hạn phần mềm và IMU mount placeholder.
- Web viewer: mô phỏng 14 khớp, không tự kết nối phần cứng.
- Hardware backend tương lai phải nằm sau interface hiện có; không cho viewer ghi thẳng ra serial bus.
- Mọi command thật cần state machine: `DISCONNECTED → SAFE → TORQUE_ON → ACTIVE → ESTOP`.

## Gate an toàn trước khi bật robot thật

1. Xác nhận đúng hardware revision (XL330 hay HD-1910); baseline repo này là XL330.
2. Cấu hình và dán nhãn từng servo khi chỉ nối một servo trên bus.
3. Scan đủ ID 1–14, không duplicate/missing; ID 15 chỉ khi có miệng.
4. Đo nguồn Pi 5 V ổn định, nguồn servo đúng giới hạn, polarity/common ground đúng.
5. Đo hướng chuyển động từng khớp ở torque/current thấp; ghi zero, direction và offset thực tế.
6. Xác nhận IMU orientation và dấu roll/pitch/yaw khi nghiêng thân bằng tay.
7. Chạy neutral khi robot được treo/đỡ, giới hạn tốc độ và có E-stop vật lý/phần mềm.
8. Chỉ chạy policy tương thích đúng joint order, offsets, observation/action shape và robot revision.

## Những gì chưa được coi là đã xác minh

- Direction, zero và knee offset của robot cụ thể.
- IMU mount quaternion hiện đang là identity placeholder.
- Khả năng dòng của nguồn/buck converter và sụt áp khi tải động.
- Policy ONNX tương thích với cơ khí thực tế.
- CAD/khối lượng/quán tính khớp đúng bản in cuối cùng.
- Hardware backend, serial timeout, watchdog và E-stop thật.

