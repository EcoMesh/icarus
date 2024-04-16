# icarus
The response mechanism.

## Setup Steps

Install http://qgroundcontrol.com/downloads/



Terminal 1:
```bash
docker run -it -e DISPLAY=host.docker.internal:0 wnt3rmute/ardupilot-sitl ./sim_vehicle.py --out udp:host.docker.internal:14550 -L Ballarat --console --map -v ArduCopter -N
```

TODO: Maybe modify https://github.com/Akademicki-Klub-Lotniczy/ardupilot-sitl-docker to work with our demo better.

Terminal 2:
```bash
mavproxy.py --master udp:127.0.0.1:14550  --out 127.0.0.1:14560 --out 127.0.0.1:14561
```

Launch QGroundControl and connect to the SITL instance by going to the Application Settings > Comm Links > Add > UDP and entering port number 14561. Make sure to click connect after adding or restarting the application.

Run the dronekit script. For example, clone the dronekit-python repository and run the example script:
```bash
python dronekit-python/examples/simple_goto/simple_goto.py --connect udp:127.0.0.1:14560
```