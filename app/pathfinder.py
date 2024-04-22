import networkx as nx

import geopy.distance

def generate_drone_path(sensor_coordinates):
    # g = nx.DiGraph()
    g = nx.Graph()

    for sensor in sensor_coordinates:
        g.add_node(sensor)
    
    for sensor1 in sensor_coordinates:
        for sensor2 in sensor_coordinates:
            # g.add_edge(sensor1, sensor2, weight=geopy.distance.geodesic(sensor1, sensor2).km)
            g.add_edge(sensor2, sensor1, weight=geopy.distance.geodesic(sensor1, sensor2).km)

    # return nx.tournament.hamiltonian_path(g)
    return nx.approximation.traveling_salesman_problem(g, weight='weight', cycle=True)


def generate_drone_path_with_homebase(sensors):
    home = (30.455, -103.149)

    path = generate_drone_path([*sensors, home])
    path.pop()

    max_iter = len(path)
    
    while path[0] != home and max_iter > 0:
        path.append(path.pop(0))
        max_iter -= 1

    if max_iter < 0:
        raise Exception('could not find homebase in path')
    
    path.pop(0)
    path.append(home)

    for p in path:
        print(f"{p[0]},{p[1]},#00FF00,marker,\"S\"")

    return path


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
        (30.44142207418663,-103.25466156005861),
        (30.39064573955672,-103.18565368652345),
        (30.401602635361105,-103.25878143310547),
        (30.46454393219863,-103.20290565490724),
        (30.45333514055255,-103.14436912536621),
        (30.427990381032874,-103.21826934814455),
        # --
        # (30.45333514055255,-103.14436912536621),
        # (30.39064573955672,-103.18565368652345),
        # (30.455,-103.149),
    ]

    path = generate_drone_path_with_homebase(sensors)

    for p in path:
        print(f"{p[0]},{p[1]},#00FF00,marker,\"S\"")

    run_drone(path)