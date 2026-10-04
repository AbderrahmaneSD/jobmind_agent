"""
graph.py — the wiring. Registers the nodes and the edges between them.

    searcher -> scraper -> analyzer -> ranker --(shortlist?)--> tailor -> END
                                                  +--(empty)--> END
"""
from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes.searcher import searcher_node
from agent.nodes.scraper import scraper_node
from agent.nodes.analyzer import analyzer_node
from agent.nodes.ranker import ranker_node
from agent.nodes.tailor import tailor_node


def route_after_ranker(state: AgentState) -> str:
    """Conditional edge: only tailor resumes if something is worth applying to."""
    return "tailor" if state["shortlist"] else "end"


def build_graph():
    graph = StateGraph(AgentState)

    # Nodes: name -> function
    graph.add_node("searcher", searcher_node)
    graph.add_node("scraper", scraper_node)
    graph.add_node("analyzer", analyzer_node)
    graph.add_node("ranker", ranker_node)
    graph.add_node("tailor", tailor_node)

    # Fixed edges
    graph.set_entry_point("searcher")
    graph.add_edge("searcher", "scraper")
    graph.add_edge("scraper", "analyzer")
    graph.add_edge("analyzer", "ranker")

    # Conditional edge: decided at runtime by route_after_ranker
    graph.add_conditional_edges(
        "ranker", route_after_ranker, {"tailor": "tailor", "end": END}
    )
    graph.add_edge("tailor", END)

    return graph.compile()


jobmind_graph = build_graph()
