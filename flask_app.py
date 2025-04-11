from flask import Flask, request, jsonify, render_template
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

app = Flask(__name__, static_url_path='/static')

graph = nx.DiGraph()
highlighted_path_edges = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_edge', methods=['POST'])
def add_edge():
    data = request.json
    if not all(k in data for k in ['node1', 'node2', 'weight']):
        return jsonify({'error': 'Faltan parámetros necesarios'}), 400

    try:
        node1, node2 = str(data['node1']), str(data['node2'])
        weight = float(data['weight'])
        if weight < 0:
            return jsonify({'error': 'Peso negativo no permitido'}), 400
    except ValueError:
        return jsonify({'error': 'Peso inválido'}), 400

    graph.add_edge(node1, node2, weight=weight)
    update_graph_image()
    return jsonify({'message': 'Añadida correctamente'})

@app.route('/dijkstra', methods=['POST'])
def dijkstra():
    data = request.json
    start_node = data.get('start_node')
    end_node = data.get('end_node')

    if not graph.nodes:
        return jsonify({'error': 'El grafo está vacío'}), 400
    if start_node not in graph.nodes:
        return jsonify({'error': f'El nodo {start_node} no existe'}), 400

    distances = {n: float('inf') for n in graph.nodes}
    distances[start_node] = 0
    parents = {n: None for n in graph.nodes}
    visited = set()

    while len(visited) < len(graph.nodes):
        current = min((n for n in graph.nodes if n not in visited), key=lambda n: distances[n])
        visited.add(current)

        for neighbor in graph.neighbors(current):
            weight = graph[current][neighbor]['weight']
            if distances[current] + weight < distances[neighbor]:
                distances[neighbor] = distances[current] + weight
                parents[neighbor] = current

    # Ruta más corta
    global highlighted_path_edges
    highlighted_path_edges = []
    if end_node and end_node in graph.nodes and distances[end_node] < float('inf'):
        path = []
        current = end_node
        while current is not None:
            path.append(current)
            current = parents[current]
        path.reverse()
        highlighted_path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
        update_graph_image(distances, parents)
        return jsonify({
            'shortest_path': path,
            'shortest_distance': distances[end_node]
        })

    update_graph_image(distances, parents)
    return jsonify({'message': 'Dijkstra ejecutado', 'distances': distances})

@app.route('/get_graph', methods=['GET'])
def get_graph():
    update_graph_image()
    return jsonify({'image_url': '/static/graph.png'})

def update_graph_image(distances=None, parents=None):
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, scale=2)

    # Colorear el nodo "1" como visitado (rojo)
    node_colors = [
        'red' if n == '1' else 'lightgreen'
        for n in graph.nodes
    ]
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=700, font_weight='bold')

    # Crear etiquetas para las aristas
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        label = f"{data['weight']}"  # Solo el peso de la arista
        # Agregar información del predecesor si existe
        if parents and parents[v] is not None:
            label += f", Pre: {parents[v]}"
        edge_labels[(u, v)] = label

    # Dibujar etiquetas de las aristas
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=10, font_color='blue')

    # Resaltar los bordes de la ruta más corta si existe
    if highlighted_path_edges:
        nx.draw_networkx_edges(graph, pos, edgelist=highlighted_path_edges, edge_color='red', width=3)

    # Etiquetas de distancias y predecesores para los nodos
    if distances:
        labels = {
            n: f"{int(distances[n]) if distances[n] != float('inf') else '∞'}\n{parents[n] if parents[n] else '-'}"
            for n in graph.nodes
        }

        # Posicionar las etiquetas un poco arriba de los nodos
        pos_labels = {k: (v[0], v[1] + 0.1) for k, v in pos.items()}
        nx.draw_networkx_labels(graph, pos_labels, labels, font_size=12, font_color='black')
    else:
        # Mostrar etiquetas con el nombre del nodo si no hay distancias calculadas
        labels = {n: f"{n}" for n in graph.nodes}
        pos_labels = {k: (v[0], v[1] + 0.1) for k, v in pos.items()}
        nx.draw_networkx_labels(graph, pos_labels, labels, font_size=12, font_color='black')

    plt.axis('off')
    os.makedirs('static', exist_ok=True)
    plt.savefig('static/graph.png')
    plt.close()

if __name__ == '__main__':
    app.run(debug=True)

