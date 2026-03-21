from langgraph.graph import StateGraph,END
from agent.state import MedicalState
from agent.nodes import guard_node, brain_node, tool_node, summarize_node,web_search_node,patient_lookup_node,route_after_guard,route_after_brain,route_to_summarize_or_end,answer_node


builder = StateGraph(MedicalState)
builder.add_node( "guard",guard_node)
builder.add_node("brain",brain_node)
builder.add_node("helper tools",tool_node)
builder.add_node( 'summarize',summarize_node)
builder.add_node('web search',web_search_node)
builder.add_node('patient lookup',patient_lookup_node)
builder.add_node("should summarize", lambda state: state)
builder.add_node("final answer", answer_node)



builder.add_conditional_edges("guard",route_after_guard,{
    'block': "final answer",
    'safe': 'brain'
})
builder.add_conditional_edges("brain", route_after_brain,{
    'additional web info': 'web search',
    'patients info': 'patient lookup',
    'pass to summarize': 'should summarize',
    "auxiliary info":"helper tools"
})
builder.add_conditional_edges("should summarize",route_to_summarize_or_end,{
    "summerize conversation": "summarize",
    "pass to final answer": "final answer"
})
builder.add_edge("summarize", "final answer")
builder.add_edge("web search", "brain")
builder.add_edge("patient lookup", "brain")
builder.add_edge("helper tools", "brain")
builder.add_edge("final answer", END)

builder.set_entry_point("guard")




