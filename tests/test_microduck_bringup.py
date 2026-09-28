import json
import tempfile
import unittest
from pathlib import Path

from microduck_bringup.config import load_config
from microduck_bringup.runtime import BringupRuntime
from microduck_bringup.safety import SafetyViolation


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "robot.yaml"


class BringupTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(CONFIG)
        self.temp = tempfile.TemporaryDirectory()
        self.runtime = BringupRuntime(self.config, self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_config_has_unique_servo_ids(self):
        ids = [joint.servo_id for joint in self.config.joints]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(14, len(ids))

    def test_doctor_passes_with_mock_hardware(self):
        report = self.runtime.doctor()
        self.assertTrue(report["ok"])
        self.assertEqual([], report["missing_servo_ids"])

    def test_out_of_range_command_is_rejected(self):
        with self.assertRaises(SafetyViolation):
            self.runtime.safety.validate_target("left_knee", 999.0)

    def test_estop_disables_torque_and_blocks_commands(self):
        self.runtime.neutral()
        self.runtime.emergency_stop("test")
        self.assertTrue(self.runtime.estop.engaged)
        self.assertTrue(all(not state.torque_enabled for state in self.runtime.bus.read_all()))
        with self.assertRaises(SafetyViolation):
            self.runtime.safety.validate_target("left_knee", 180.0)

    def test_jsonl_logging(self):
        self.runtime.doctor()
        lines = self.runtime.log_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(1, len(lines))
        self.assertEqual("doctor", json.loads(lines[0])["event"])


if __name__ == "__main__":
    unittest.main()

