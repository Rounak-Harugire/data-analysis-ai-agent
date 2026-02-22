from crewai import Agent
from core.llm import llm

question_agent = Agent(
    role="Business Analyst",
    goal="Generate analytical questions from dataset summary",
    backstory="You specialize in turning data summaries into meaningful business questions.",
    llm=llm,
    verbose=False
)