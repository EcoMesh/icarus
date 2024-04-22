# icarus
The response mechanism.

## Setup Steps

Install http://qgroundcontrol.com/downloads/

Terminal 1:
```bash
docker run --rm -it -e DISPLAY=host.docker.internal:0 wnt3rmute/ardupilot-sitl ./sim_vehicle.py --out udp:host.docker.internal:14550 -l 30.455,-103.149,-999,0 --console --map -v ArduCopter -N
```

TODO: Maybe modify https://github.com/Akademicki-Klub-Lotniczy/ardupilot-sitl-docker to work with our demo better.

Install the poetry dependencies with `poetry install`. Then enter the shell with `poetry shell`.

Terminal 2:
```bash
mavproxy.py --master udp:127.0.0.1:14550  --out 127.0.0.1:14560 --out 127.0.0.1:14561
```

Launch QGroundControl and connect to the SITL instance by going to the Application Settings > Comm Links > Add > UDP and entering port number 14561. Make sure to click connect after adding or restarting the application.

Run the dronekit script. For example, clone the dronekit-python repository and run the example script:
```bash
python dronekit-python/examples/simple_goto/simple_goto.py --connect udp:127.0.0.1:14560

python drone/drone_sitl_flight.py --connect udp:127.0.0.1:14560
```

Finally, start the webhook server:
```bash
uvicorn app:app --reload --port 4444
```

## Debugging

When debugging the drone path, this website is useful to plot the points. Use the `app.pathfinder.debug_coordinates` function
to print out the coordinates to the console and then copy and paste them into this [mapping website](https://mobisoftinfotech.com/tools/plot-multiple-points-on-map/).

Check "Show Point Numbers" and then "Update Map" to see the numerical order of the points on the map.