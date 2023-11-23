# %matplotlib inline
import osmnx as ox
import networkx as nx
import sys
import json


def generate_routes(graph, start, end, num_routes=15):
    routes = []

    for i in range(num_routes):
        route = nx.shortest_path(graph, source=start, target=end, weight='length')
        routes.append(route)

        edges_used = list(zip(route[:-1], route[1:]))
        modify_weights(graph, edges_used)
    return routes


def calculate_overlap(route1, route2):
    shared_edges = set(zip(route1[:-1], route1[1:])) & set(zip(route2[:-1], route2[1:]))
    return len(shared_edges) / min(len(route1) - 1, len(route2) - 1)


def bounding_box(lat1, lon1, lat2, lon2):
    min_lat = min(lat1, lat2)
    max_lat = max(lat1, lat2)
    min_lon = min(lon1, lon2)
    max_lon = max(lon1, lon2)
    return min_lat, min_lon, max_lat, max_lon


def get_routes():
    print('Load OSM...')
    # graph = ox.graph_from_xml("NE-Merge-v1-1-formatted.osm")
    graph = ox.graph_from_bbox("Omaha, Nebraska")
    print('Loaded')

    north, west, south, east = bounding_box(start_lat, start_lon, end_lat, end_lon)
    print(north, west, south, east)
    print('Truncate...')
    graph = ox.truncate.truncate_graph_bbox(graph, north, south, east, west, truncate_by_edge=True)
    print('Truncated')

    start_node = ox.distance.nearest_nodes(graph, X=start_lon, Y=start_lat)
    end_node = ox.distance.nearest_nodes(graph, X=end_lon, Y=end_lat)

    print('Generate Routes...')
    routes = generate_routes(graph, start_node, end_node, num_routes)
    print('Generated')

    print('Check Overlap...')
    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            overlap = calculate_overlap(routes[i], routes[j])
            print(f"Overlap between route {i} and route {j}: {overlap:.2f}")

    print('Finished')
    return routes


def modify_weights(graph, edges_used, penalty=2):
    for edge in edges_used:
        if len(edge) == 3:
            u, v, key = edge
            graph[u][v][key]['length'] *= penalty
        elif len(edge) == 2:
            u, v = edge
            graph[u][v][0]['length'] *= penalty
        else:
            pass


if __name__ == "__main__":
    print('Start')
    start_lat, start_lon, end_lat, end_lon, num_routes = map(float, sys.argv[1:6])
    final_routes = get_routes()
    print(json.dumps(final_routes))
