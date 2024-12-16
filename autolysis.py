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
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Fetch API key from environment variable
api_key = os.getenv("AIPROXY_TOKEN")
if not api_key:
    logging.error("API key not found. Please set the AIPROXY_TOKEN environment variable.")
    sys.exit(1)

# Define LLM interaction with retry logic
base_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

def query_llm(function_call):
    """
    Queries the LLM with the function call for dynamic analysis-based prompts.
    """
    # Queries the LLM for insights and returns the response.
    prompt = f"""
    Use the following information to generate a detailed analysis report:
    - {function_call}
    """
    try:
        url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {AIPROXY_TOKEN}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",  # Supported chat model
            "messages": [
                {"role": "system", "content": "You are a helpful data analysis assistant. Provide insights, suggestions, and implications based on the given analysis and visualizations."},
                {"role": "user", "content": prompt},
            ],
        }
        payload_json = json.dumps(payload)
        curl_command = [
            "curl",
            "-X", "POST", url,
            "-H", f"Authorization: Bearer {AIPROXY_TOKEN}",
            "-H", "Content-Type: application/json",
            "-d", payload_json
        ]
        result = subprocess.run(curl_command, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            raise Exception(f"Failed to execute curl command: {result.stderr}")
    except Exception as e:
        print(f"Error querying AI Proxy: {e}")
        return "Error: Unable to generate narrative."


    # Generate Visualizations
    charts = []
    palette = "coolwarm"  # Define consistent color palette
    if len(df.columns) >= 2:
        # Correlation heatmap
        numeric_df = df.select_dtypes(include="number")
        if numeric_df.shape[1] > 1:
            plt.figure(figsize=(10, 8))
            sns.heatmap(numeric_df.corr(), annot=True, cmap=palette, fmt=".2f")
            plt.title(f"{dataset_name} Correlation Heatmap", fontsize=16)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.tight_layout()
            heatmap_file = os.path.join(output_dir, f"{dataset_name}_correlation_heatmap.png")
            plt.savefig(heatmap_file)
            charts.append(heatmap_file)
            plt.close()

        # Distribution of the first numerical column
        if numeric_df.shape[1] > 0:
            first_numeric = numeric_df.columns[0]
            plt.figure(figsize=(8, 6))
            sns.histplot(numeric_df[first_numeric].dropna(), kde=True, bins=30, color="skyblue")
            plt.title(f"Distribution of {first_numeric}", fontsize=16)
            plt.xlabel(first_numeric, fontsize=12)
            plt.ylabel("Frequency", fontsize=12)
            plt.xticks(fontsize=10)
            plt.yticks(fontsize=10)
            plt.tight_layout()
            dist_file = os.path.join(output_dir, f"{dataset_name}_distribution.png")
            plt.savefig(dist_file)
            charts.append(dist_file)
            plt.close()

        # Box plot for the numerical columns
        if numeric_df.shape[1] > 1:
            plt.figure(figsize=(12, 6))
            sns.boxplot(data=numeric_df, palette=palette)
            plt.title(f"Boxplot of {dataset_name}", fontsize=16)
            plt.xticks(rotation=45, ha='right', fontsize=10)
            plt.yticks(fontsize=10)
            plt.tight_layout()
            boxplot_file = os.path.join(output_dir, f"{dataset_name}_boxplot.png")
            plt.savefig(boxplot_file)
            charts.append(boxplot_file)
            plt.close()

        # Bar plot for missing data
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            plt.figure(figsize=(12, 6))
            missing_data[missing_data > 0].plot(kind='bar', color='salmon')
            plt.title(f"Missing Data in {dataset_name}", fontsize=16)
            plt.xlabel("Columns", fontsize=12)
            plt.ylabel("Number of Missing Values", fontsize=12)
            plt.xticks(rotation=45, fontsize=10)
            plt.yticks(fontsize=10)
            plt.tight_layout()
            missing_data_file = os.path.join(output_dir, f"{dataset_name}_missing_data.png")
            plt.savefig(missing_data_file)
            charts.append(missing_data_file)
            plt.close()

    # Request narrative from LLM
    story_messages = [
        {"role": "system", "content": "You are a data storytelling assistant."},
        {"role": "user", "content": f"Based on this analysis:\n\n{analysis}\n\nGenerate a narrative about the insights and implications of this dataset."}
    ]
    story = query_llm(story_messages)

    # Save README.md
    readme_file = os.path.join(output_dir, "README.md")
    try:
        with open(readme_file, "w") as f:
            f.write("# Analysis Report\n\n")
            f.write(story)
            f.write("\n\n## Visualizations\n\n")
            for chart in charts:
                f.write(f"![{os.path.basename(chart)}]({chart})\n")
        logging.info(f"README generated: {readme_file}")
    except Exception as e:
        logging.error(f"Error saving README file: {e}")

    logging.info(f"Analysis complete for {dataset_name}. Files generated:")
    for chart in charts:
        logging.info(f"- {chart}")

def main():
    """Main function to process datasets."""
    if len(sys.argv) < 2:
        logging.error("Please provide at least one CSV file as an argument.")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        if os.path.exists(file_path) and file_path.endswith(".csv"):
            process_dataset(file_path)
        else:
            logging.error(f"Invalid file path or not a CSV file: {file_path}")

if __name__ == "__main__":
    main()
