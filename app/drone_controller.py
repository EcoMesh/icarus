import subprocess
import tempfile
import json
from filelock import FileLock, Timeout

import subprocess
import threading
import time

import signal

import logging
from djitellopy import Tello

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


def run_dronekit_sitl(lanuch_site, terminate_event, ready_event):
    command = [
        "docker", "run", "--rm", "-t", "-e", "DISPLAY=host.docker.internal:0",
        "wnt3rmute/ardupilot-sitl", "./sim_vehicle.py",
        "--out", "udp:host.docker.internal:14550",
        "--out", "udp:host.docker.internal:14551",
        "-l", f"{lanuch_site[0]},{lanuch_site[1]},-999,0", "--console", "--map", "-v", "ArduCopter", "-N"
    ]

    sitl = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
    for line in sitl.stdout:
        if "APM: GPS 1: detected as u-blox at 230400 baud" in line:
            ready_event.set()
            break
        
    while sitl.poll() is None:  # Check if process B is still running
        time.sleep(1)
        if terminate_event.is_set():
            print('Terminating SITL')
            sitl.send_signal(signal.SIGINT)
        print('SITL running')


def go_to_hight(drone, hight):
    # min move is 20cm
    current_hight = drone.get_height()
    y = hight - current_hight
    
    if abs(y) < 20:
        return
    
    if y > 0:
        drone.move_up(y)
    else:
        drone.move_down(-y)


def dji_hover(drone: Tello, hight: int, land_event: threading.Event):
    drone.takeoff()
    go_to_hight(drone, hight)
    i = 0
    while not land_event.is_set():
        time.sleep(1)
        if i % 5 == 0:
            print('Battery:', drone.get_battery())
            drone.send_command_without_return('keepalive')
        i += 1


def run_drone(drone_path, lanuch_site):
    try:
        with FileLock("drone.lock", timeout=1):
            land_event = threading.Event()
            terminate_event = threading.Event()
            ready_event = threading.Event()

            thread_sitl = threading.Thread(target=run_dronekit_sitl, args=(lanuch_site, terminate_event, ready_event), daemon=True)

            thread_sitl.start()

            ready_event.wait()

            subprocess.run(['open', '-a', 'QGroundControl'])

            with tempfile.NamedTemporaryFile('w') as f:
                d = json.dumps(drone_path)
                f.write(d)
                f.flush()
                
                print(d)

                print ('real copter up')
                drone = Tello(host='192.168.2.2')

                drone.connect()

                # drone.enable_mission_pads()
                # drone.set_mission_pad_detection_direction(0)

                print('Battery:', drone.get_battery())

                drone_sim = subprocess.Popen(["python", "-u", "drone/drone_sitl_flight.py", "--connect", "udp:127.0.0.1:14551", f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)

                print('here')

                for line in drone_sim.stdout:
                    print(line)
                    if "Taking off" in line:
                        break
                
                threading.Thread(target=dji_hover, args=(drone, 100, land_event), daemon=True).start()

                for line in drone_sim.stdout:
                    print(line)
                    if "Returning to launch and landing" in line:
                        break
                
                land_event.set()

                # drone.go_xyz_speed(0, 0, 100, 50)
                drone.land()

                try:
                    while True:
                        time.sleep(1)
                        if drone_sim.poll() is not None:
                            print('Drone down')
                            break
                except KeyboardInterrupt:
                    print('Keyboard interrupt')
                    terminate_event.set()
                    drone_sim.kill()
                    drone_sim.wait()
                print ('real copter down')

            
            terminate_event.set()

            thread_sitl.join()
    except Timeout:
        print("Another instance of the drone simulation is already running")
