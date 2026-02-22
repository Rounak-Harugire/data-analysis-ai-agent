import os
import sys
from crewai import Crew, Task, Process
from agents.junior_da import junior_da
from agents.question_agent import question_agent
from agents.eda_agent import eda_agent
from tools.data_tool import load_dataset, get_metadata_summary
from tools.plot_tool import generate_dynamic_plots


def run_pipeline(dataset_path=None):

    # ---------------- Default Dataset ----------------
    if dataset_path is None:
        dataset_path = os.path.join("data", "dataset.csv")

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    # ---------------- Load Dataset ----------------
    df = load_dataset(dataset_path)
    columns, summary = get_metadata_summary(df)

    # ---------------- Task 1 ----------------
    task1 = Task(
        description=f"""
Dataset Columns:
{columns}

Descriptive Statistics:
{summary}

Provide:
1. Dataset Overview (3-4 bullet points)
2. Key Numeric Insights
3. Important Patterns
4. Potential Business Implications

Provide output strictly in clean markdown format.
Do not include extra stars, markdown symbols, or incomplete bullet points.
Be concise and professional.
""",
        expected_output="Executive-level dataset summary.",
        agent=junior_da
    )

    # ---------------- Task 2 ----------------
    task2 = Task(
        description="""
Based on the dataset summary generated earlier,
create exactly 5 meaningful business or analytical questions.

Provide output strictly in clean markdown format.
Use numbered format.
Do not include extra stars or symbols.
Keep it concise.
""",
        expected_output="5 structured analytical questions.",
        agent=question_agent
    )

    # ---------------- Task 3 ----------------
    task3 = Task(
        description="""
For each analytical question generated,
recommend the most appropriate visualization type.

Respond in format:
Question 1 → Visualization Type
Question 2 → Visualization Type

Do not add explanation.
Be concise.
""",
        expected_output="Mapping of questions to visualization types.",
        agent=eda_agent
    )

    # ---------------- Crew Execution ----------------
    crew = Crew(
        agents=[junior_da, question_agent, eda_agent],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        memory=False,
        verbose=False
    )

    results = crew.kickoff()

    # ---------------- SAFE EXTRACTION ----------------
    # CrewAI 1.x returns TaskOutput objects
    # We safely extract raw text
    summary_text = str(results.tasks_output[0].raw)
    questions_text = str(results.tasks_output[1].raw)
    visuals_text = str(results.tasks_output[2].raw)

    # ---------------- Dynamic Plot Generation ----------------
    plot_files = generate_dynamic_plots(df, visuals_text)

    return {
        "summary": summary_text,
        "questions": questions_text,
        "visuals": visuals_text,
        "plots": plot_files
    }


# ---------------- CLI Execution ----------------
if __name__ == "__main__":

    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = None

    output = run_pipeline(dataset_path)

    print("\n===== SUMMARY =====\n")
    print(output["summary"])

    print("\n===== QUESTIONS =====\n")
    print(output["questions"])

    print("\n===== VISUALIZATION RECOMMENDATIONS =====\n")
    print(output["visuals"])

    print("\nGenerated Plot Files:")
    for p in output["plots"]:
        print(p)