from __future__ import annotations

from dataclasses import dataclass

from .config import RobotConfig


class SafetyViolation(ValueError):
    pass


@dataclass
class EmergencyStop:
    engaged: bool = False
    reason: str | None = None

    def trigger(self, reason: str = "operator request") -> None:
        self.engaged = True
        self.reason = reason

    def reset(self) -> None:
        self.engaged = False
        self.reason = None


class SafetyController:
    def __init__(self, config: RobotConfig, estop: EmergencyStop) -> None:
        self._by_name = {joint.name: joint for joint in config.joints}
        self.estop = estop

    def validate_target(self, joint_name: str, target_deg: float) -> float:
        if self.estop.engaged:
            raise SafetyViolation(f"emergency stop engaged: {self.estop.reason}")
        if joint_name not in self._by_name:
            raise SafetyViolation(f"unknown joint: {joint_name}")
        joint = self._by_name[joint_name]
        if not joint.min_deg <= target_deg <= joint.max_deg:
            raise SafetyViolation(
                f"{joint_name}: target {target_deg:.2f} outside "
                f"[{joint.min_deg:.2f}, {joint.max_deg:.2f}]"
            )
        return target_deg

