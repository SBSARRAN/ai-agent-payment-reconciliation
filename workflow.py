
from langgraph.graph import (
    StateGraph,
    START,
    END
)

# Import our shared state.
from backend.graph.state import PaymentState

# Import the nodes we already created.
from backend.graph.nodes import (
    classify_node,
    extract_node,
    load_statement_node,
    match_node
)



def route_after_classification(
    state: PaymentState
):

    # Read the classification result.
    is_payment = state.get(
        "is_payment",
        False
    )

    # If it is a payment image,
    # continue to receipt extraction.
    if is_payment:

        return "extract"

    # If it is not a payment image,
    # stop the workflow.
    return "end"


workflow = StateGraph(
    PaymentState
)
workflow.add_node(
    "classify",
    classify_node
)

workflow.add_node(
    "extract",
    extract_node
)

workflow.add_node(
    "load_statement",
    load_statement_node
)

workflow.add_node(
    "match",
    match_node
)


workflow.add_edge(
    START,
    "classify"
)



workflow.add_conditional_edges(
    "classify",
    route_after_classification,
    {
        "extract": "extract",
        "end": END
    }
)




workflow.add_edge(
    "extract",
    "load_statement"
)



workflow.add_edge(
    "load_statement",
    "match"
)




workflow.add_edge(
    "match",
    END
)


payment_graph = workflow.compile()