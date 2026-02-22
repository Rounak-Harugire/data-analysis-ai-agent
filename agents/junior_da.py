from crewai import Agent
from core.llm import llm

junior_da = Agent(
    role="Junior Data Analyst",
    goal="Analyze dataset metadata and provide structured insights",
    backstory="You are a detail-oriented junior data analyst.",
    llm=llm,
    verbose=False
)