import pandas as pd


def load_dataset(file_path: str):
    return pd.read_csv(file_path)


def get_metadata_summary(df):
    summary = df.describe(include="all").to_string()
    columns = df.columns.tolist()
    return columns, summary