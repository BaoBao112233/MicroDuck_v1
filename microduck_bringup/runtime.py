from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path

from .config import RobotConfig
from .hardware import MockIMU, MockServoBus
from .safety import EmergencyStop, SafetyController


class BringupRuntime:
    def __init__(self, config: RobotConfig, log_dir: str | Path = "logs") -> None:
        self.config = config
        self.bus = MockServoBus(config)
        self.imu = MockIMU()
        self.estop = EmergencyStop()
        self.safety = SafetyController(config, self.estop)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        self.log_path = self.log_dir / f"microduck-{stamp}.jsonl"

    def snapshot(self) -> dict[str, object]:
        return {
            "timestamp": time.time(),
            "mode": "dry-run",
            "robot": self.config.robot,
            "control_hz": self.config.control_hz,
            "estop": {"engaged": self.estop.engaged, "reason": self.estop.reason},
            "servos": [asdict(state) for state in self.bus.read_all()],
            "imu": self.imu.read(),
        }

    def log(self, event: str, payload: dict[str, object]) -> None:
        record = {"timestamp": time.time(), "event": event, **payload}
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def doctor(self) -> dict[str, object]:
        expected = sorted(joint.servo_id for joint in self.config.joints)
        found = self.bus.scan()
        report = {
            "ok": expected == found and bool(self.imu.read()["healthy"]),
            "mode": "dry-run",
            "expected_servo_ids": expected,
            "found_servo_ids": found,
            "missing_servo_ids": sorted(set(expected) - set(found)),
            "imu_healthy": self.imu.read()["healthy"],
            "config_valid": True,
        }
        self.log("doctor", report)
        return report

    def neutral(self) -> dict[str, float]:
        if self.estop.engaged:
            raise RuntimeError("cannot enter neutral pose while emergency stop is engaged")
        self.bus.enable_torque()
        commanded: dict[str, float] = {}
        for joint in self.config.joints:
            target = self.safety.validate_target(joint.name, joint.neutral_deg)
            self.bus.command(joint.servo_id, target)
            commanded[joint.name] = target
        self.log("neutral", {"targets_deg": commanded})
        return commanded

    def emergency_stop(self, reason: str = "operator request") -> None:
        self.estop.trigger(reason)
        self.bus.disable_torque()
        self.log("estop", {"reason": reason, "torque_disabled": True})

