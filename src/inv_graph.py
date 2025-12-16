from langgraph.graph import StateGraph, END

from agents.agents import AgentState, extract_invoice_node, transform_data_node


# Define the graph
workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("extract_invoice", extract_invoice_node)
workflow.add_node("transform_data", transform_data_node)

# Set the entrypoint
workflow.set_entry_point("extract_invoice")

# Add edges
workflow.add_edge("extract_invoice", "transform_data")
workflow.add_edge("transform_data", END)


# Compile the graph
inv_graph = workflow.compile()