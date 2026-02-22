from crewai import Agent
from core.llm import llm

eda_agent = Agent(
    role="EDA Specialist",
    goal="Recommend visualization types for analytical questions",
    backstory="You are an expert in exploratory data analysis and visualization.",
    llm=llm,
    verbose=False
)