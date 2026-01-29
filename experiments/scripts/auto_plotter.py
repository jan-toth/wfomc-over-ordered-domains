import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
import sys

# --- Plotting Functions ---

def plot_comparison(csv_path, algorithms=None, log_scale=True, output_file=None):
    """
    Generates a grouped bar plot comparing runtimes across different problems.
    """
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        sys.exit(1)

    # Clean whitespace
    df['problem'] = df['problem'].astype(str).str.strip()
    df['algo'] = df['algo'].astype(str).str.strip()

    # Filter algorithms
    if algorithms:
        df = df[df['algo'].isin(algorithms)]
    
    if df.empty:
        print("Error: No data available after filtering. Check algorithm names.")
        sys.exit(1)

    # Aggregate: Median runtime per problem/algo pair
    df_agg = df.groupby(['problem', 'algo'])['time'].median().reset_index()
    
    # Sort alphanumerically
    df_agg.sort_values(by='problem', inplace=True)

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")

    bar_plot = sns.barplot(
        data=df_agg, 
        x='problem', 
        y='time', 
        hue='algo',
        palette='viridis', 
        edgecolor='black'
    )

    if log_scale:
        bar_plot.set_yscale("log")
        plt.ylabel("Median Runtime (s) [Log Scale]")
    else:
        plt.ylabel("Median Runtime (s)")

    plt.xlabel("Problem ID")
    plt.title("Runtime Comparison by Problem")
    plt.legend(title="Algorithm", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Comparison plot saved to {output_file}")
    else:
        plt.show()


def plot_scaling(csv_path, prefix, algorithms=None, log_scale=True, output_file=None):
    """
    Generates a line plot showing how runtime scales with domain size.
    """
    print(f"Loading data from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"Error: File {csv_path} not found.")
        sys.exit(1)

    df['problem'] = df['problem'].astype(str).str.strip()
    df['algo'] = df['algo'].astype(str).str.strip()

    # Filter by problem prefix
    df = df[df['problem'].str.startswith(prefix)].copy()
    if df.empty:
        print(f"Error: No data found for problem prefix '{prefix}'.")
        sys.exit(1)

    # Extract Domain Size
    def extract_size(row_id):
        # Remove prefix
        remainder = row_id[len(prefix):]
        # Remove leading separators (e.g. '_', '-')
        clean = re.sub(r'^[^0-9]+', '', remainder)
        try:
            return int(clean)
        except ValueError:
            return None

    df['domain_size'] = df['problem'].apply(extract_size)
    df.dropna(subset=['domain_size'], inplace=True)

    # Filter algorithms
    if algorithms:
        df = df[df['algo'].isin(algorithms)]

    if df.empty:
        print("Error: No data available after filtering.")
        sys.exit(1)

    # Aggregate
    df_agg = df.groupby(['domain_size', 'algo'])['time'].median().reset_index()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    sns.lineplot(
        data=df_agg,
        x='domain_size',
        y='time',
        hue='algo',
        style='algo',
        markers=True,
        dashes=False,
        markersize=8,
        linewidth=2
    )

    if log_scale:
        plt.yscale("log")
        plt.ylabel("Median Runtime (s) [Log Scale]")
    else:
        plt.ylabel("Median Runtime (s)")

    plt.xlabel("Domain Size")
    plt.title(f"Scaling Behavior: {prefix}")
    plt.legend(title="Algorithm", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Scaling plot saved to {output_file}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description="WFOMC Benchmark Plotter")
    subparsers = parser.add_subparsers(dest="mode", required=True, help="Plotting mode")

    # Common arguments
    def add_common_args(p):
        p.add_argument("input_csv", help="Path to input CSV file")
        p.add_argument("-o", "--output", help="Path to save output image (e.g., plot.png)")
        p.add_argument("-a", "--algos", nargs="+", help="List of algorithms to include")
        p.add_argument("--linear", action="store_true", help="Use linear scale instead of log scale")

    # Subcommand: comparison (Bar Chart)
    parser_comp = subparsers.add_parser("bar", help="Generate grouped bar chart for multiple problems")
    add_common_args(parser_comp)

    # Subcommand: scaling (Line Chart)
    parser_scale = subparsers.add_parser("scale", help="Generate scaling curve for a specific problem")
    add_common_args(parser_scale)
    parser_scale.add_argument("-p", "--prefix", required=True, help="Problem name prefix (e.g., 'ht')")

    args = parser.parse_args()

    # Determine log scale (Default is True, unless --linear is passed)
    use_log_scale = not args.linear

    if args.mode == "bar":
        plot_comparison(
            csv_path=args.input_csv, 
            algorithms=args.algos, 
            log_scale=use_log_scale, 
            output_file=args.output
        )

    elif args.mode == "scale":
        plot_scaling(
            csv_path=args.input_csv, 
            prefix=args.prefix, 
            algorithms=args.algos, 
            log_scale=use_log_scale, 
            output_file=args.output
        )


if __name__ == "__main__":
    main()