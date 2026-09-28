from __future__ import annotations

import math
import time
from dataclasses import dataclass

from .config import RobotConfig


@dataclass
class ServoState:
    servo_id: int
    position_deg: float
    velocity_dps: float
    voltage_v: float
    temperature_c: float
    torque_enabled: bool
    error: str | None = None


class MockServoBus:
    def __init__(self, config: RobotConfig) -> None:
        self._states = {
            joint.servo_id: ServoState(
                servo_id=joint.servo_id,
                position_deg=joint.neutral_deg,
                velocity_dps=0.0,
                voltage_v=6.0,
                temperature_c=31.0 + (joint.servo_id % 4),
                torque_enabled=False,
            )
            for joint in config.joints
        }

    def scan(self) -> list[int]:
        return sorted(self._states)

    def read_all(self) -> list[ServoState]:
        return [self._states[key] for key in sorted(self._states)]

    def enable_torque(self) -> None:
        for state in self._states.values():
            state.torque_enabled = True

    def disable_torque(self) -> None:
        for state in self._states.values():
            state.torque_enabled = False
            state.velocity_dps = 0.0

    def command(self, servo_id: int, position_deg: float) -> None:
        state = self._states[servo_id]
        if not state.torque_enabled:
            raise RuntimeError(f"servo {servo_id}: torque is disabled")
        previous = state.position_deg
        state.position_deg = position_deg
        state.velocity_dps = position_deg - previous


class MockIMU:
    def read(self) -> dict[str, object]:
        phase = time.monotonic() * 0.2
        yaw = 0.01 * math.sin(phase)
        return {
            "quaternion_xyzw": [0.0, 0.0, round(yaw, 6), round(math.sqrt(1 - yaw * yaw), 6)],
            "gyro_rps": [0.0, 0.0, round(0.002 * math.cos(phase), 6)],
            "accel_mps2": [0.0, 0.0, 9.80665],
            "healthy": True,
        }

