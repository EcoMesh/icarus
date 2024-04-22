import subprocess
import tempfile
import json
from filelock import FileLock, Timeout


def run_drone(drone_path):
    try:
        with FileLock("drone.lock", timeout=1):
            with tempfile.NamedTemporaryFile('w') as f:
                d = json.dumps(drone_path)
                f.write(d)
                f.flush()
                print(d)

                print ('real copter up')
                subprocess.run(["python", "drone/drone_sitl_flight.py", "--connect", "udp:127.0.0.1:14560", f.name])
                print ('real copter down')
    except Timeout:
        print("Another instance of the drone simulation is already running")