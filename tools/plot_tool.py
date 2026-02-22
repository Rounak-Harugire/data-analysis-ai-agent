import os
import matplotlib.pyplot as plt


def generate_dynamic_plots(df, visualization_text):
    os.makedirs("plots", exist_ok=True)

    plot_files = []

    text = visualization_text.lower()

    numeric_columns = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    numeric_columns = [col for col in numeric_columns if "id" not in col.lower()]

    categorical_columns = df.select_dtypes(include=["object"]).columns.tolist()

    # ---------------- BAR CHART ----------------
    if any(keyword in text for keyword in ["bar"]):
        if categorical_columns and numeric_columns:
            cat = categorical_columns[0]
            num = numeric_columns[0]

            plt.figure()
            df.groupby(cat)[num].mean().plot(kind="bar")
            plt.title(f"{num} by {cat}")
            plt.tight_layout()
            path = os.path.join("plots", "bar_chart.png")
            plt.savefig(path)
            plt.close()
            plot_files.append(path)

    # ---------------- SCATTER PLOT ----------------
    if any(keyword in text for keyword in ["scatter"]):
        if len(numeric_columns) >= 2:
            x = numeric_columns[0]
            y = numeric_columns[1]

            plt.figure()
            plt.scatter(df[x], df[y])
            plt.xlabel(x)
            plt.ylabel(y)
            plt.title(f"{x} vs {y}")
            plt.tight_layout()
            path = os.path.join("plots", "scatter_plot.png")
            plt.savefig(path)
            plt.close()
            plot_files.append(path)

    # ---------------- HISTOGRAM ----------------
    if any(keyword in text for keyword in ["histogram", "distribution"]):
        for col in numeric_columns:
            plt.figure()
            df[col].hist()
            plt.title(f"{col} Distribution")
            plt.tight_layout()
            path = os.path.join("plots", f"{col}_histogram.png")
            plt.savefig(path)
            plt.close()
            plot_files.append(path)

    # ---------------- BOX PLOT ----------------
    if any(keyword in text for keyword in ["box"]):
        if numeric_columns:
            plt.figure()
            df[numeric_columns].boxplot()
            plt.xticks(rotation=45)
            plt.title("Box Plot of Numeric Features")
            plt.tight_layout()
            path = os.path.join("plots", "box_plot.png")
            plt.savefig(path)
            plt.close()
            plot_files.append(path)

    # ---------------- PIE CHART ----------------
    if any(keyword in text for keyword in ["pie"]):
        if categorical_columns:
            col = categorical_columns[0]

            plt.figure()
            df[col].value_counts().plot(kind="pie", autopct="%1.1f%%")
            plt.ylabel("")
            plt.title(f"{col} Distribution")
            plt.tight_layout()
            path = os.path.join("plots", "pie_chart.png")
            plt.savefig(path)
            plt.close()
            plot_files.append(path)

    return plot_files