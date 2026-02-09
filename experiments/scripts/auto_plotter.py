import argparse
import re
import sys

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from natsort import natsorted

RENAME_MAP = {
    'inc': 'Incremental_v1',
    'rec': 'Recursive',
    'inc2': 'Incremental_v2',
    'd4': 'd4',
    'ganak': 'ganak',
    'inc3': 'Incremental_v3'
}

COLOR_MAP = {
    'inc': "#984ea3",   # purple
    'rec': "#ff7f00",   # orange
    'inc2': "#e41a1c",  # red
    'd4': "#4daf4a",    # green
    'ganak': "#377eb8",  # blue
    'inc3': "#ff00d4",   # pink
}
FALLBACK_COLORS = ["#a65628", "#f781bf", "#999999", "#a6cee3", "#b2df8a"]


def _get_palette(algorithms):
    """Constructs a list of colors corresponding exactly to the input list of algorithms."""
    palette = []
    fallback_idx = 0

    for algo in algorithms:
        # Check if we have a fixed color for this algo
        if algo in COLOR_MAP:
            palette.append(COLOR_MAP[algo])
        else:
            # Assign a fallback color if not defined
            palette.append(FALLBACK_COLORS[fallback_idx % len(FALLBACK_COLORS)])
            fallback_idx += 1

    return palette



def _update_legend_labels(ax):
    if not ax.legend_:
        return

    new_labels = []
    for t in ax.legend_.get_texts():
        raw_name = t.get_text()
        new_labels.append(RENAME_MAP.get(raw_name, raw_name))

    for t, label in zip(ax.legend_.get_texts(), new_labels):
        t.set_text(label)


def _extract_size(x, prefix):
    """Helper functions to extract domain size from problem id string"""
    remainder = x[len(prefix):]
    match = re.search(r'(\d+)', remainder)
    
    if match:
        return int(match.group(1))
    return None


def plot_bars(csv_path, algorithms=None, sort_by_algo=None, legend_loc=None, log_scale=True, output_file=None):
    """
    Generates a grouped bar plot comparing runtimes across different problems.
    """
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
        hue_order = algorithms
    else:
        hue_order = natsorted(df['algo'].unique())
    
    if df.empty:
        print("Error: No data available after filtering. Check algorithm names.")
        sys.exit(1)

    df['problem'] = df['problem'].apply(lambda x: _extract_size(x, ""))

    # Aggregate: Median runtime per problem/algo pair
    df_agg = df.groupby(['problem', 'algo'])['time'].median().reset_index()
    
    # Sort alphanumerically
    # df_agg.sort_values(by='problem', inplace=True)

    
    if sort_by_algo:
        # Sot by algorithm
        target_data = df_agg[df_agg['algo'] == sort_by_algo]
        sorted_problems = target_data.sort_values('time')['problem'].tolist()
        all_problems = set(df_agg['problem'].unique())
        missing = list(all_problems - set(sorted_problems))
        problem_order = sorted_problems + natsorted(missing)
    else:
        # Sort naturally
        problem_order = natsorted(df_agg['problem'].unique())
    
    df_agg['problem'] = pd.Categorical(df_agg['problem'], categories=problem_order, ordered=True)
    df_agg.sort_values(by='problem', inplace=True)

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.barplot(
        data=df_agg, 
        x='problem', 
        y='time', 
        hue='algo',
        hue_order=hue_order,
        palette=_get_palette(hue_order), 
        edgecolor='black'
    )

    if log_scale:
        ax.set_yscale("log")
    plt.ylabel("Runtime [s]")

    plt.xlabel("Problem ID")
    # plt.title("Runtime Comparison by Problem")
    # plt.legend(title="Algorithm", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.legend(loc=legend_loc)
    _update_legend_labels(ax)
    plt.xticks(rotation=45, ha='center')
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Comparison plot saved to {output_file}")
    else:
        plt.show()


def plot_scaling(csv_path, prefix, suffix=None, algorithms=None, min_size=None, max_size=None, xticks=None, legend_loc=None, log_scale=True, output_file=None):
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
    df['domain_size'] = df['problem'].apply(lambda row_id: _extract_size(row_id, prefix))
    df.dropna(subset=['domain_size'], inplace=True)

    if min_size:
        df = df[df['domain_size'] >= min_size]
    if max_size:
        df = df[df['domain_size'] <= max_size]

    # Filter algorithms
    if algorithms:
        df = df[df['algo'].isin(algorithms)]
        hue_order = algorithms
    else:
        hue_order = natsorted(df['algo'].unique())

    if df.empty:
        print("Error: No data available after filtering.")
        sys.exit(1)

    # Aggregate
    df_agg = df.groupby(['domain_size', 'algo'])['time'].median().reset_index()

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    ax = sns.lineplot(
        data=df_agg,
        x='domain_size',
        y='time',
        hue='algo',
        hue_order=hue_order,
        style='algo',
        style_order=hue_order,
        palette=_get_palette(hue_order),
        markers=True,
        dashes=False,
        markersize=8,
        linewidth=2
    )

    if log_scale:
        ax.set_yscale("log")
    plt.ylabel("Runtime [s]")

    plt.xlabel("Domain Size")
    if xticks:
        try:
            parts = [int(x) for x in xticks.split(",")]
            assert len(parts) == 3
            custom_ticks = list(range(*parts))
            ax.set_xticks(custom_ticks)
        except ValueError:
            print("Error parsing 'xticks' argument")
    else:
        ax.set_xticks(sorted(df_agg['domain_size'].unique())[1::2])

    plt.legend(loc=legend_loc)
    _update_legend_labels(ax)
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Scaling plot saved to {output_file}")
    else:
        plt.show()


def plot_cactus(csv_path, algorithms=None, timeout=None, legend_loc=None, log_scale=True, output_file=None):
    """
    Generates a Cactus Plot:
    X-axis: Number of solved instances (cumulative)
    Y-axis: Time taken to solve the Nth fastest instance (sorted independently per algo)
    """
    print(f"Loading data from {csv_path}...")
    try: df = pd.read_csv(csv_path)
    except FileNotFoundError: sys.exit(1)
    df['algo'] = df['algo'].astype(str).str.strip()

    # Filter Algorithms
    if algorithms:
        df = df[df['algo'].isin(algorithms)]
        hue_order = algorithms
    else:
        hue_order = natsorted(df['algo'].unique())

    # Aggregate (Median over runs)
    # This gives one time per (problem, algo) pair
    df_agg = df.groupby(['problem', 'algo'])['time'].median().reset_index()

    # Apply Timeout (Treat > timeout as unsolved)
    if timeout:
        df_agg = df_agg[df_agg['time'] <= timeout]

    if df_agg.empty:
        print("Error: No solved instances found (check data or timeout).")
        sys.exit(1)

    # Prepare Cactus Data
    cactus_data = []

    for algo in hue_order:
        # Get all runtimes for this algo, sorted ascending
        times = sorted(df_agg[df_agg['algo'] == algo]['time'].tolist())

        # Create cumulative count (1st solved, 2nd solved, ...)
        for i, time in enumerate(times, start=1):
            cactus_data.append({
                'algo': algo,
                'solved_count': i,
                'time': time
            })

    df_cactus = pd.DataFrame(cactus_data)

    # Plotting
    plt.figure(figsize=(10, 6))
    sns.set_theme(style="whitegrid")

    # Use lineplot without markers usually, but markers help see distinct problems
    ax = sns.lineplot(
        data=df_cactus,
        x='solved_count',
        y='time',
        hue='algo',
        hue_order=hue_order,
        style='algo',
        style_order=hue_order,
        palette=_get_palette(hue_order),
        markers=True,
        dashes=False,
        linewidth=2
    )

    if log_scale:
        ax.set_yscale("log")
    plt.ylabel("Runtime [s]")

    plt.xlabel("Number of Solved Instances")

    # Legend
    plt.legend(loc=legend_loc)
    _update_legend_labels(ax)

    plt.tight_layout()

    if output_file:
        plt.savefig(output_file, dpi=300)
        print(f"Cactus plot saved to {output_file}")
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
        p.add_argument("--legend", default="upper right", help="Position of the legend per matplotlib specification")

    # Subcommand: comparison (Bar Chart)
    parser_comp = subparsers.add_parser("bar", help="Generate grouped bar chart for multiple problems")
    add_common_args(parser_comp)
    parser_comp.add_argument('--sort-by', help="Algorithm to sort by")

    # Subcommand: scaling (Line Chart)
    parser_scale = subparsers.add_parser("scale", help="Generate scaling curve for a specific problem")
    add_common_args(parser_scale)
    parser_scale.add_argument("-p", "--prefix", required=True, help="Problem name prefix (e.g., 'ht')")
    parser_scale.add_argument("-s", "--suffix", help="Problem name suffix to filter by (e.g., '_1' or '_2')")
    parser_scale.add_argument("--min", type=int, help="Minimum domain size to include")
    parser_scale.add_argument("--max", type=int, help="Maximum domain size to include")
    parser_scale.add_argument("--xticks", help="X-axis ticks as Python range <start>,<stop>,<step>")


    # Subcommand: cactus (Cactus Plot)
    parser_cactus = subparsers.add_parser("cactus", help="Cactus plot")
    add_common_args(parser_cactus)
    parser_cactus.add_argument("--timeout", type=float, help="Cutoff in seconds")

    args = parser.parse_args()

    # Determine log scale (Default is True, unless --linear is passed)
    use_log_scale = not args.linear

    if args.mode == "bar":
        plot_bars(
            csv_path=args.input_csv, 
            algorithms=args.algos,
            sort_by_algo=args.sort_by,
            legend_loc=args.legend,
            log_scale=use_log_scale, 
            output_file=args.output
        )

    elif args.mode == "scale":
        plot_scaling(
            csv_path=args.input_csv, 
            prefix=args.prefix, 
            algorithms=args.algos,
            min_size=args.min,
            max_size=args.max,
            xticks=args.xticks,
            legend_loc=args.legend,
            log_scale=use_log_scale, 
            output_file=args.output
        )
    elif args.mode == "cactus":
        plot_cactus(
            csv_path=args.input_csv,
            algorithms=args.algos,
            timeout=args.timeout,
            legend_loc=args.legend,
            log_scale=use_log_scale,
            output_file=args.output
        )


if __name__ == "__main__":
    main()
