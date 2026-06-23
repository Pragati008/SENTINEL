from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from module4_graph import (
    load_graph,
    save_graph,
    add_application_to_graph,
    analyze_application,
    generate_graph_visualization
)

app = FastAPI()

class ApplicationEntities(BaseModel):
    application_id: str
    is_flagged: Optional[bool] = False
    phone: Optional[str] = None
    email: Optional[str] = None
    device_id: Optional[str] = None
    address: Optional[str] = None
    pan: Optional[str] = None

@app.post("/module4/add-application")
def add_application(data: ApplicationEntities):
    """
    Add a new application to the fraud graph.
    Call this every time a new loan application comes in.
    """
    try:
        G = load_graph()

        entities = {
            "phone": data.phone,
            "email": data.email,
            "device_id": data.device_id,
            "address": data.address,
            "pan": data.pan
        }

        G = add_application_to_graph(
            G,
            data.application_id,
            entities,
            is_flagged=data.is_flagged
        )

        save_graph(G)

        return {
            "status": "success",
            "message": f"{data.application_id} added to fraud graph",
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges()
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/module4/analyze/{application_id}")
def analyze(application_id: str):
    """
    Analyze an existing application in the graph.
    Returns risk score, flagged connections, and fraud ring detection.
    """
    try:
        G = load_graph()
        result = analyze_application(G, application_id)
        return {
            "module": "fraud_graph_intelligence",
            **result
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/module4/visualize/{application_id}")
def visualize(application_id: str):
    """
    Generate fraud graph visualization for a given application.
    Returns path to the HTML file.
    """
    try:
        G = load_graph()
        output_file = f"graph_{application_id}.html"
        generate_graph_visualization(G, application_id, output_file)
        return {
            "status": "success",
            "visualization_file": output_file,
            "message": f"Open {output_file} in your browser to view the graph"
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/module4/graph-stats")
def graph_stats():
    """
    Returns overall graph statistics.
    Useful for dashboard summary.
    """
    try:
        G = load_graph()

        total_applications = sum(
            1 for n in G.nodes
            if G.nodes[n].get("node_type") == "application"
        )
        flagged_applications = sum(
            1 for n in G.nodes
            if G.nodes[n].get("node_type") == "application"
            and G.nodes[n].get("is_flagged")
        )

        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "total_applications": total_applications,
            "flagged_applications": flagged_applications
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/")
def health_check():
    return {"status": "Module 4 — Fraud Graph Intelligence is running"}