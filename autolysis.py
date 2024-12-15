# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "numpy",
#   "matplotlib",
#   "seaborn",
#   "argparse",
#   "openai",
#   "httpx",
#   "logging",
# ]
# ///

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import httpx
import time
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Fetch API key from environment variable
api_key = os.getenv("AIPROXY_TOKEN")
if not api_key:
    logging.error("API key not found. Please set the AIPROXY_TOKEN environment variable.")
    sys.exit(1)

# API Base URL
base_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"


# Query LLM with Retry Logic
def query_llm(messages, retries=3):
    """Sends data to the LLM API and retrieves the response with retry logic."""
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {"model": "gpt-4o-mini", "messages": messages}
    for attempt in range(retries):
        try:
            response = httpx.post(base_url, json=data, headers=headers, timeout=60.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            if attempt < retries - 1:
                logging.warning(f"Retry {attempt + 1}/{retries} failed due to error: {e}")
                time.sleep(2)
            else:
                logging.error(f"API request failed after {retries} attempts.")
                raise Exception(f"API Error: {e}")


# Process Dataset
def process_dataset(file_path):
    """Processes the dataset: generates analysis, visualizations, and README."""
    dataset_name = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Load dataset
        df = pd.read_csv(file_path, encoding="latin1")
        logging.info(f"Loaded dataset '{dataset_name}' with {df.shape[0]} rows and {df.shape[1]} columns.")
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return

    # Summarize data
    numeric_df = df.select_dtypes(include="number")
    summary = df.describe(include="all").to_string()
    missing_values = df.isnull().sum().to_string()
    sample_data = df.head(5).to_string()

    # Optimized LLM prompt
    messages = [
        {"role": "system", "content": "You are a data analysis assistant."},
        {"role": "user", "content": f"Analyze this dataset with columns {list(df.columns)}:\n\n"
                                    f"First rows:\n{sample_data[:500]}\n\n"
                                    f"Summary:\n{summary[:800]}\n\n"
                                    f"Missing Values:\n{missing_values}"}
    ]
    analysis = query_llm(messages)

    # Simple In-Script Analysis
    top_missing = df.isnull().sum().nlargest(3)
    logging.info("Top 3 columns with missing values:")
    logging.info(top_missing)

    # Generate visualizations
    charts = []
    if not numeric_df.empty:
        # Correlation heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
        plt.title(f"{dataset_name} - Correlation Heatmap")
        heatmap_file = os.path.join(output_dir, f"{dataset_name}_heatmap.png")
        plt.savefig(heatmap_file)
        charts.append(heatmap_file)
        plt.close()

    # Save README with analysis
    readme_file = os.path.join(output_dir, f"{dataset_name}_README.md")
    try:
        with open(readme_file, "w") as f:
            f.write(f"# {dataset_name} Analysis Report\n\n")
            f.write("## Dataset Summary\n")
            f.write(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.\n\n")
            f.write("## Key Insights\n")
            f.write("- **Top Missing Values**:\n")
            f.write(top_missing.to_string() + "\n\n")
            f.write("## Visualizations\n\n")
            for chart in charts:
                f.write(f"![{os.path.basename(chart)}]({chart})\n\n")
            f.write("## LLM Analysis\n")
            f.write(analysis)
        logging.info(f"README generated at {readme_file}.")
    except Exception as e:
        logging.error(f"Failed to save README: {e}")


# Main Function
def main():
    """Main function to process one or more CSV files."""
    if len(sys.argv) < 2:
        logging.error("Please provide at least one CSV file as input.")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        if os.path.exists(file_path) and file_path.endswith(".csv"):
            process_dataset(file_path)
        else:
            logging.error(f"Invalid file: {file_path}")


if __name__ == "__main__":
    main()
