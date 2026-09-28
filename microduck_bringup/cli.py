from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .config import load_config
from .runtime import BringupRuntime
from .safety import SafetyViolation


DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / "config" / "robot.yaml"


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="MicroDuck safe software bring-up MVP")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--log-dir", default="logs")
    parser.add_argument("--dry-run", action="store_true", help="Explicitly select the mock hardware backend")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor", help="Validate config and report hardware health")
    sub.add_parser("scan", help="List servo IDs visible on the bus")
    monitor = sub.add_parser("monitor", help="Print live robot state")
    monitor.add_argument("--samples", type=int, default=5)
    monitor.add_argument("--interval", type=float, default=0.25)
    sub.add_parser("neutral", help="Command configured neutral pose")
    safety_check = sub.add_parser("safety-check", help="Prove an unsafe joint target is rejected")
    safety_check.add_argument("--joint", default="left_knee")
    safety_check.add_argument("--target", type=float, default=999.0)
    estop = sub.add_parser("estop", help="Disable torque immediately")
    estop.add_argument("--reason", default="operator request")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = load_config(args.config)
    runtime = BringupRuntime(config, args.log_dir)
    if args.command == "doctor":
        _print(runtime.doctor())
    elif args.command == "scan":
        result = {"mode": "dry-run", "servo_ids": runtime.bus.scan()}
        runtime.log("scan", result)
        _print(result)
    elif args.command == "monitor":
        for _ in range(max(1, args.samples)):
            snapshot = runtime.snapshot()
            runtime.log("monitor", snapshot)
            _print(snapshot)
            time.sleep(max(0.0, args.interval))
    elif args.command == "neutral":
        _print({"mode": "dry-run", "targets_deg": runtime.neutral()})
    elif args.command == "safety-check":
        try:
            runtime.safety.validate_target(args.joint, args.target)
        except SafetyViolation as error:
            result = {"safe": True, "rejected": True, "reason": str(error)}
            runtime.log("safety-check", result)
            _print(result)
        else:
            result = {"safe": False, "rejected": False, "reason": "unsafe test command was accepted"}
            runtime.log("safety-check", result)
            _print(result)
            return 2
    elif args.command == "estop":
        runtime.emergency_stop(args.reason)
        _print({"estop": True, "reason": args.reason, "torque_disabled": True})
    return 0


