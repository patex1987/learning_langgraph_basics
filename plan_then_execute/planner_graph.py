from datetime import datetime
from typing import TypedDict, Optional, Union

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END

from plan_then_execute.domain.contracts import CodeExplainPlan, CritiqueResult

def extract_text_from_content(content: Union[str, list[Union[str, dict]]]) -> str:
    """Extract text from message content, handling both str and list[str | dict] formats."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Extract text from list items (str or dict)
        texts = []
        for item in content:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
            elif isinstance(item, dict) and "content" in item:
                texts.append(item["content"])
        return " ".join(texts)
    return str(content)

class PlannerState(TypedDict):
    code: str
    plan: Optional[CodeExplainPlan]
    explanation: Optional[str]
    critique: Optional[str]
    iteration: int
    approved: bool




class ExecutionPlanner:
    MAX_ITERATIONS = 3

    def __init__(self, planner_llm: BaseChatModel):
        self.planner_llm = planner_llm



    def compile_planner_graph(self):
        """


        TODO: add graph visualization
        :return:
        """
        g = StateGraph(PlannerState)

        g.add_node("plan", self.decide_plan)
        g.add_node("explain", self.explain)
        g.add_node("critique", self.critique)
        g.add_node("revise", self.revise)

        g.set_entry_point("plan")
        g.add_edge("plan", "explain")
        g.add_edge("explain", "critique")

        g.add_conditional_edges(
            "critique",
            self.route,
            {
                "revise": "revise",
                END: END,
            },
        )

        g.add_edge("revise", "explain")

        return g.compile()

    async def decide_plan(self, state: PlannerState, config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] START: decide_plan')
        
        planner = self.planner_llm.with_structured_output(CodeExplainPlan)

        code_to_review = state['code']
        planner_prompt = f"""
        Decide the explanation depth and focus for the following code:\n\n{code_to_review}
        """

        plan = await planner.ainvoke(planner_prompt)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] END: decide_plan')
        
        return {"plan": plan}

    async def explain(self, state: PlannerState, config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] START: explain')

        state_plan: CodeExplainPlan = state["plan"]
        code_to_review = state["code"]

        explain_prompt = f"""
        Explain this code.
        
        Depth: {state_plan.explanation_type}
        Focus: {state_plan.focus_area}
        
        CODE:
        {code_to_review}
        """
        result = await self.planner_llm.ainvoke(explain_prompt)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] END: explain')
        # TODO: or add structured output
        explanation_text = extract_text_from_content(result.content)

        return {
            "explanation": explanation_text,
            "iteration": state["iteration"] + 1,
        }

    async def critique(self, state: PlannerState, config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] START: critique')

        explanation = state["explanation"]

        critique_prompt = f"""
        Critique the following explanation.
        Determine if it is good enough (approved=True) or needs improvement (approved=False).
        If not approved, provide specific feedback on what needs to be improved.
        
        EXPLANATION:
        {explanation}
        """

        critic = self.planner_llm.with_structured_output(CritiqueResult)
        critique_result = await critic.ainvoke(critique_prompt)
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] END: critique')
        
        critique_text = critique_result.feedback or ("Approved" if critique_result.approved else "Needs improvement")
        
        return {"critique": critique_text, "approved": critique_result.approved}

    async def revise(self, state: PlannerState, config):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] START: revise')

        critique = state["critique"]
        explanation = state["explanation"]

        revision_prompt = f"""
        Revise the explanation based on this critique.
    
        CRITIQUE:
        {critique}
        
        CURRENT EXPLANATION:
        {explanation}
        """

        revised = await self.planner_llm.ainvoke(revision_prompt)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] END: revise')

        return {"explanation": revised.content}

    def route(self, state: PlannerState):
        current_critique = state['critique']
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f'[{timestamp}] NEW LLM ITERATION: {current_critique}')

        if state["approved"]:
            return END
        if state["iteration"] >= self.MAX_ITERATIONS:
            return END
        return "revise"

