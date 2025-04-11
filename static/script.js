document.addEventListener('DOMContentLoaded', () => {
    const graphImg = document.getElementById('graph');
    const resultDiv = document.getElementById('shortest-path-result');

    function refreshGraph() {
        fetch('/get_graph')
            .then(res => res.json())
            .then(data => {
                graphImg.src = data.image_url + '?t=' + new Date().getTime();
            });
    }

    document.getElementById('add-edge-btn').addEventListener('click', async () => {
        const node1 = document.getElementById('node1').value;
        const node2 = document.getElementById('node2').value;
        const weight = document.getElementById('weight').value;

        const res = await fetch('/add_edge', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ node1, node2, weight })
        });

        const data = await res.json();
        alert(data.message || data.error);
        refreshGraph();
    });

    document.getElementById('run-dijkstra-btn').addEventListener('click', async () => {
        const startNode = document.getElementById('start-node').value;
        const endNode = document.getElementById('end-node').value;

        const res = await fetch('/dijkstra', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_node: startNode, end_node: endNode })
        });

        const data = await res.json();
        if (data.shortest_path) {
            resultDiv.innerHTML = `
                Ruta corta: <strong>${data.shortest_path.join(' → ')}</strong><br>
                Total distancia: <strong>${data.shortest_distance}</strong>
            `;
        } else {
            resultDiv.innerHTML = `⚠️ ${data.error || 'No se encontró ruta válida'}`;
        }
        refreshGraph();
    });

    refreshGraph(); // Carga inicial
});
