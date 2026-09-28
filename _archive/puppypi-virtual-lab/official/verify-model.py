"""Verify the generated vendor model and installed mesh resources."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from ament_index_python.packages import get_package_share_directory

root = Path('/mnt/g/Projects/PuppyPi/official')
robot = ET.parse(root / 'puppy.generated.urdf').getroot()
share = Path(get_package_share_directory('puppypi_description'))
joints = [j for j in robot.findall('joint') if j.attrib['type'] == 'revolute']
assert len(joints) == 8, len(joints)
meshes = sorted({m.attrib['filename'] for m in robot.findall('.//mesh')})
for uri in meshes:
    assert uri.startswith('package://puppypi_description/')
    path = share / uri.removeprefix('package://puppypi_description/')
    assert path.is_file() and path.stat().st_size > 84, path
report = {'upstream_commit': 'dfff97c42331f97497050a5558e650bde41bf54d',
          'links': len(robot.findall('link')), 'actuated_joints': len(joints),
          'joint_names': [j.attrib['name'] for j in joints],
          'unique_meshes': len(meshes), 'all_meshes_exist': True,
          'scope': 'Official URDF/resource validation, not vendor gait validation'}
(root / 'model-validation.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
