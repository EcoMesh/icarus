import networkx as nx

import geopy.distance

import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import matplotlib

def generate_drone_path(sensor_coordinates):
    g = nx.Graph()

    for sensor in sensor_coordinates:
        g.add_node(sensor)
    
    for sensor1 in sensor_coordinates:
        for sensor2 in sensor_coordinates:
            g.add_edge(sensor2, sensor1, weight=geopy.distance.geodesic(sensor1, sensor2).km)

    return nx.approximation.traveling_salesman_problem(g, weight='weight', cycle=True)

# LAUNCH_SITE = (30.455, -103.149) # original
LAUNCH_SITE = (30.396832281150534, -103.16871717297174) # Courand's

def generate_drone_path_with_homebase(sensors):
    path = generate_drone_path([*sensors, LAUNCH_SITE])
    path.pop()

    max_iter = len(path)
    
    while path[0] != LAUNCH_SITE and max_iter > 0:
        path.append(path.pop(0))
        max_iter -= 1

    if max_iter < 0:
        raise Exception('could not find homebase in path')
    
    path.pop(0)
    path.append(LAUNCH_SITE)

    return path


def debug_coordinates(coordinates, cmap='viridis'):
    norm = Normalize(vmin=0, vmax=len(coordinates))
    cmap = plt.get_cmap(cmap)
    
    for i, c in enumerate(coordinates):
        color_hex = matplotlib.colors.to_hex(cmap(norm(i)))
        print(f"{c[0]},{c[1]},{color_hex},marker,\"{i + 1}\"")


if __name__ == '__main__':
    from app.drone_controller import run_drone

    sensors = [
        # (30.45333514055250, -103.14436912536623),
        # (30.45333514055254, -103.14436912536625),
        # (30.39064573955672, -103.18565368652345),
        # (30.46454393219863, -103.20290565490724),
        # (30.427990381032874, -103.21826934814455),
        # (30.45333514055255, -103.14436912536621),
        # --
        # (30.44142207418663,-103.25466156005861),
        # (30.39064573955672,-103.18565368652345),
        # (30.401602635361105,-103.25878143310547),
        # (30.46454393219863,-103.20290565490724),
        # (30.45333514055255,-103.14436912536621),
        # (30.427990381032874,-103.21826934814455),
        # --
        # (30.45333514055255,-103.14436912536621),
        # (30.39064573955672,-103.18565368652345),
        # (30.455,-103.149),
        # --
        (30.398,-103.171),
        (30.378,-103.1731),
        (30.379,-103.1561),
    ]

    path = generate_drone_path_with_homebase(sensors)

    debug_coordinates(path)

    run_drone(path, LAUNCH_SITE)