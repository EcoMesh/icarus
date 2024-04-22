import networkx as nx

import geopy.distance

def generate_drone_path(sensor_coordinates):
    g = nx.DiGraph()

    for sensor in sensor_coordinates:
        g.add_node(sensor)
    
    for sensor1 in sensor_coordinates:
        for sensor2 in sensor_coordinates:
            g.add_edge(sensor1, sensor2, weight=geopy.distance.geodesic(sensor1, sensor2).km)
            g.add_edge(sensor2, sensor1, weight=geopy.distance.geodesic(sensor1, sensor2).km)

    return nx.tournament.hamiltonian_path(g)


if __name__ == '__main__':
    home = (30.45333514055277, -103.14436912536610)
    path = [
        home,
        (30.45333514055250, -103.14436912536623),
        (30.45333514055254, -103.14436912536625),
        (30.39064573955672, -103.18565368652345),
        (30.46454393219863, -103.20290565490724),
        (30.427990381032874, -103.21826934814455),
        (30.45333514055255, -103.14436912536621),
    ]

    path = generate_drone_path(path)

    while path[0] != home:
        path.append(path.pop(0))
    
    path.append(home)

    for p in path:
        print(p)