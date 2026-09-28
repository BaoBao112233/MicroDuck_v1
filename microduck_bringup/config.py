from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class JointConfig:
    name: str
    servo_id: int
    neutral_deg: float
    direction: int
    min_deg: float
    max_deg: float

    def validate(self) -> None:
        if self.servo_id <= 0:
            raise ValueError(f"{self.name}: servo_id must be positive")
        if self.direction not in (-1, 1):
            raise ValueError(f"{self.name}: direction must be -1 or 1")
        if not self.min_deg < self.neutral_deg < self.max_deg:
            raise ValueError(f"{self.name}: neutral must be inside joint limits")


@dataclass(frozen=True)
class RobotConfig:
    robot: str
    control_hz: float
    joints: tuple[JointConfig, ...]
    imu_frame: str
    imu_mount_quat_xyzw: tuple[float, float, float, float]

    def validate(self) -> None:
        if self.control_hz <= 0:
            raise ValueError("control_hz must be positive")
        if not self.joints:
            raise ValueError("at least one joint is required")
        names = [joint.name for joint in self.joints]
        ids = [joint.servo_id for joint in self.joints]
        if len(names) != len(set(names)):
            raise ValueError("joint names must be unique")
        if len(ids) != len(set(ids)):
            raise ValueError("servo IDs must be unique")
        if len(self.imu_mount_quat_xyzw) != 4:
            raise ValueError("IMU mount quaternion must contain four values")
        for joint in self.joints:
            joint.validate()


def load_config(path: str | Path) -> RobotConfig:
    """Load JSON-compatible YAML without third-party dependencies."""
    source = Path(path)
    raw = json.loads(source.read_text(encoding="utf-8"))
    config = RobotConfig(
        robot=str(raw["robot"]),
        control_hz=float(raw["control_hz"]),
        joints=tuple(JointConfig(**joint) for joint in raw["joints"]),
        imu_frame=str(raw["imu"]["frame"]),
        imu_mount_quat_xyzw=tuple(float(v) for v in raw["imu"]["mount_quat_xyzw"]),
    )
    config.validate()
    return config

