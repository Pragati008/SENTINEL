import networkx as nx
import pickle
import os
from pyvis.network import Network

# File to persist graph between API calls
GRAPH_FILE = "fraud_graph.pkl"

def load_graph():
    if os.path.exists(GRAPH_FILE):
        with open(GRAPH_FILE, "rb") as f:
            return pickle.load(f)
    return nx.Graph()

def save_graph(G):
    with open(GRAPH_FILE, "wb") as f:
        pickle.dump(G, f)

def add_application_to_graph(G, application_id, entities: dict, is_flagged: bool = False):
    """
    entities is a dict like:
    {
        "phone": "9876543210",
        "email": "abc@gmail.com",
        "device_id": "DEV123",
        "address": "123 Main St Delhi",
        "pan": "ABCDE1234F"
    }
    """
    # Add application node
    G.add_node(
        application_id,
        node_type="application",
        is_flagged=is_flagged
    )

    # Add entity nodes and connect to application
    for entity_type, entity_value in entities.items():
        if entity_value is None or entity_value == "":
            continue

        entity_node_id = f"{entity_type}:{entity_value}"

        if not G.has_node(entity_node_id):
            G.add_node(
                entity_node_id,
                node_type=entity_type,
                value=entity_value
            )

        G.add_edge(application_id, entity_node_id, relation=entity_type)

    return G

def analyze_application(G, application_id):
    """
    Check if this application connects to any flagged applications
    through shared entities
    """
    if not G.has_node(application_id):
        return {
            "status": "not_found",
            "message": "Application not in graph"
        }

    # Get all entity nodes this application connects to
    direct_neighbors = list(G.neighbors(application_id))

    # For each entity, find other applications sharing it
    linked_applications = {}
    flagged_connections = []
    shared_entities = []

    for entity_node in direct_neighbors:
        node_data = G.nodes[entity_node]
        if node_data.get("node_type") == "application":
            continue

        # Find other applications connected to this entity
        entity_neighbors = list(G.neighbors(entity_node))
        other_apps = [
            n for n in entity_neighbors
            if n != application_id and G.nodes[n].get("node_type") == "application"
        ]

        if other_apps:
            shared_entities.append({
                "entity_type": node_data.get("node_type"),
                "entity_value": node_data.get("value"),
                "shared_with": other_apps
            })

            for app in other_apps:
                if app not in linked_applications:
                    linked_applications[app] = []
                linked_applications[app].append(node_data.get("node_type"))

                # Check if that application was flagged
                if G.nodes[app].get("is_flagged"):
                    flagged_connections.append({
                        "application_id": app,
                        "shared_via": node_data.get("node_type"),
                        "shared_value": node_data.get("value")
                    })

    # Fraud ring detection — community of 3+ applications sharing 2+ entities
    fraud_ring_suspected = False
    if len(linked_applications) >= 2:
        for app, shared in linked_applications.items():
            if len(shared) >= 2:
                fraud_ring_suspected = True
                break

    # Risk scoring
    risk_score = 0
    if flagged_connections:
        risk_score += 40 * min(len(flagged_connections), 2)
    if fraud_ring_suspected:
        risk_score += 30
    if len(linked_applications) > 0:
        risk_score += 10 * min(len(linked_applications), 3)

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_tier = "high"
    elif risk_score >= 40:
        risk_tier = "medium"
    elif risk_score > 0:
        risk_tier = "low"
    else:
        risk_tier = "clean"

    return {
        "application_id": application_id,
        "total_linked_applications": len(linked_applications),
        "flagged_connections": flagged_connections,
        "shared_entities": shared_entities,
        "fraud_ring_suspected": fraud_ring_suspected,
        "graph_risk_score": risk_score,
        "risk_tier": risk_tier
    }

def generate_graph_visualization(G, application_id, output_file="fraud_graph.html"):
    """
    Generate an interactive HTML visualization
    centered around the given application
    """
    # Get subgraph — application + 2 hops
    nodes_to_include = set([application_id])

    if G.has_node(application_id):
        # First hop — direct entity neighbors
        first_hop = set(G.neighbors(application_id))
        nodes_to_include.update(first_hop)

        # Second hop — other applications sharing those entities
        for entity in first_hop:
            second_hop = set(G.neighbors(entity))
            nodes_to_include.update(second_hop)

    subgraph = G.subgraph(nodes_to_include)

    # Build pyvis network
    net = Network(height="500px", width="100%", bgcolor="#1a1a2e", font_color="white")

    for node in subgraph.nodes:
        node_data = subgraph.nodes[node]
        node_type = node_data.get("node_type", "unknown")

        if node_type == "application":
            if node == application_id:
                color = "#e94560"  # red — current application
                size = 25
            elif node_data.get("is_flagged"):
                color = "#ff6b35"  # orange — flagged application
                size = 20
            else:
                color = "#0f3460"  # dark blue — other application
                size = 15
        else:
            color = "#16213e"  # entity node
            size = 10

        net.add_node(
            node,
            label=str(node),
            color=color,
            size=size,
            title=f"Type: {node_type}"
        )

    for edge in subgraph.edges:
        net.add_edge(edge[0], edge[1])

    net.save_graph(output_file)
    return output_file


# Quick test
if __name__ == "__main__":
    G = load_graph()

    # Add some existing applications to simulate history
    G = add_application_to_graph(G, "APP001", {
        "phone": "9876543210",
        "email": "fraud1@gmail.com",
        "device_id": "DEV999",
        "address": "12 Ghost Lane Delhi",
        "pan": "AAAAA1111A"
    }, is_flagged=True)

    G = add_application_to_graph(G, "APP002", {
        "phone": "9876543210",  # same phone as APP001
        "email": "legit@gmail.com",
        "device_id": "DEV888",
        "address": "45 Real Street Mumbai",
        "pan": "BBBBB2222B"
    }, is_flagged=True)

    G = add_application_to_graph(G, "APP003", {
        "phone": "1111111111",
        "email": "another@gmail.com",
        "device_id": "DEV999",  # same device as APP001
        "address": "78 Other Road Chennai",
        "pan": "CCCCC3333C"
    }, is_flagged=False)

    # Now analyze a new suspicious application
    G = add_application_to_graph(G, "APP004_NEW", {
        "phone": "9876543210",  # same phone as APP001 and APP002
        "email": "newapplicant@gmail.com",
        "device_id": "DEV999",  # same device as APP001 and APP003
        "address": "99 New Address Pune",
        "pan": "DDDDD4444D"
    }, is_flagged=False)

    save_graph(G)

    result = analyze_application(G, "APP004_NEW")
    print("\nGraph Analysis Result:")
    for key, value in result.items():
        print(f"{key}: {value}")

    # Generate visualization
    generate_graph_visualization(G, "APP004_NEW", "fraud_graph.html")
    print("\nVisualization saved to fraud_graph.html")