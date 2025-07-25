import os
import json
import sys
import matplotlib
from matplotlib import colors as pycolors, pyplot as plt
import numpy as np
import mplcursors
import argparse

label_names_spanish = {
    'FPS': 'Velocidad de inferencia (FPS)',
    'mAP50-95': 'Precisión mAP50-95 (%)',
    'mAP50': 'Precisión mAP50 (%)',
    'mAP75': 'Precisión mAP75 (%)',
    'model_size_kb': 'Tamaño del modelo (kB)',
    'inference speed (ms)': 'Tiempo de inferencia (ms)',
}

label_names_for_title_spanish = {
    'FPS': 'Velocidad de inferencia',
    'mAP50-95': 'Precisión mAP50-95',
    'mAP50': 'Precisión mAP50',
    'mAP75': 'Precisión mAP75',
    'model_size_kb': 'Tamaño del modelo',
    'inference speed (ms)': 'Tiempo de inferencia',
}

label_names_english = {
    'FPS': 'Inference Speed (FPS)',
    'mAP50-95': 'mAP50-95 Accuracy (%)',
    'mAP50': 'mAP50 Accuracy (%)',
    'mAP75': 'mAP75 Accuracy (%)',
    'model_size_kb': 'Model Size (kB)',
    'inference speed (ms)': 'Inference Speed (ms)',
}

label_names_for_title_english = {
    'FPS': 'Inference Speed',
    'mAP50-95': 'mAP50-95 Accuracy',
    'mAP50': 'mAP50 Accuracy',
    'mAP75': 'mAP75 Accuracy',
    'model_size_kb': 'Model Size',
    'inference speed (ms)': 'Inference Speed',
}

# CLI arguments
parser = argparse.ArgumentParser(description="Plot export results with selectable variables.")
parser.add_argument('-x', type=str, default='FPS', help='Variable for x-axis (default: FPS)')
parser.add_argument('-y', type=str, default='mAP50-95', help='Variable for y-axis (default: mAP50-95)')
parser.add_argument('-c', '--cursor', action='store_true', help='Enable cursor for hover tooltips')
parser.add_argument('-b', '--base-dir', type=str, default='my-models/sloppy_results', help='Base directory for results')
parser.add_argument('-s', '--save-fig', action='store_true', help='Save the figure to a file')
parser.add_argument('-i', '--interactive', action='store_true', help='Enable interactive mode') 
parser.add_argument('-a', '--axis_limits', action='store_true', help='Set axis limits for the plot')
parser.add_argument('-t', '--table', action='store_true', help='Print results in a table format')
parser.add_argument('-d', '--decimals', action='store_true', help='Show results in table with one decimal place') 
parser.add_argument('-p', '--percentage', action='store_true', help='Show results in table as percentages')
parser.add_argument('-sp', '--spanish', action='store_true', help='Use Spanish labels and titles')
parser.add_argument('-f', '--format', type=str, default='eps', help='Format for saving the figure (default: eps)')

args = parser.parse_args()

# Set the base directory
base_dir = args.base_dir

# Collect data
results = {}
for class_name in os.listdir(base_dir):
    class_dir = os.path.join(base_dir, class_name)
    if not os.path.isdir(class_dir):
        continue
    results[class_name] = {}
    for fname in os.listdir(class_dir):
        if fname.endswith('.json'):
            prune_rate = fname.replace('.json', '')
            with open(os.path.join(class_dir, fname), 'r') as f:
                data = json.load(f)
            results[class_name][prune_rate] = data

print(f"Collected results for {len(results)} classes from {base_dir}")

# Pretty print first few results
# print(results)

# Prepare colormap
class_names = list(results.keys())
num_classes = len(class_names)
cmap = plt.get_cmap('hsv')
colors = [cmap(i / (num_classes + 1)) for i in range(1, num_classes + 1)]

# Plotting
for idx, (class_name, prunes) in enumerate(results.items()):
    x_vals = []
    y_vals = []
    for prune_rate, data in sorted(prunes.items(), key=lambda x: float(x[0])):
        x_val = data.get(args.x, 0)
        y_val = data.get(args.y, 0)
        if args.percentage:
            if 'mAP' in args.x:
                x_val *= 100
            if 'mAP' in args.y:
                y_val *= 100
        x_vals.append(x_val)
        y_vals.append(y_val)
    plt.plot(x_vals, y_vals, marker='o', label=class_name, color=colors[idx], markersize=4)

label_names = label_names_spanish if args.spanish else label_names_english
label_names_for_title = label_names_for_title_spanish if args.spanish else label_names_for_title_english

plt.xlabel(label_names[args.x])
plt.ylabel(label_names[args.y])
plt.title(f'{label_names_for_title[args.y]} vs. {label_names_for_title[args.x]}', fontweight='bold')

# Reorder legend handles and labels
handles, labels = plt.gca().get_legend_handles_labels()
order = [6,7,4,5,2,3,0,1]  # Custom order for legend
plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])

plt.grid(True)

if args.cursor:
    # mplcursors.cursor(hover=True)

    # Add tooltips showing prune_rate value
    for idx, (class_name, prunes) in enumerate(results.items()):
        x_vals = []
        y_vals = []
        prune_rate_labels = []
        for prune_rate, data in sorted(prunes.items(), key=lambda x: float(x[0])):
            x_val = data.get(args.x, 0)
            y_val = data.get(args.y, 0)
            if args.percentage:
                if 'mAP' in args.x:
                    x_val *= 100
                if 'mAP' in args.y:
                    y_val *= 100
            x_vals.append(x_val)
            y_vals.append(y_val)
            prune_rate_labels.append(prune_rate)
        for x, y, label in zip(x_vals, y_vals, prune_rate_labels):
            plt.annotate(label, (x, y), textcoords="offset points", xytext=(0,5), ha='center', fontsize=6)

if args.axis_limits:
    # Set axis limits if specified
    if args.x == 'FPS':
        plt.xlim(0, 60)
        if args.y == 'mAP50':
            if args.percentage:
                plt.ylim(40, 95)
            else:
                plt.ylim(0.4, 0.95)
    elif args.x == 'model_size_kb':
        plt.xlim(500, 4000)
        if args.y == 'mAP50':
            if args.percentage:
                plt.ylim(0, 95)
            else:
                plt.ylim(0.0, 0.95)

if args.save_fig or args.table:
    # Save the plot as an eps file
    output_path = os.path.join(
        "export-results", 
        f"{args.y}_vs_{args.x}" + 
        ("_cursors" if args.cursor else "") + 
        ("_zoomed" if args.axis_limits else "")
    )
    
if args.save_fig:
    output_path_fig = output_path + f".{args.format}"
    plt.gcf().set_size_inches(11.06, 5.49)  # Set figure dimensions (width, height) in inches
    plt.savefig(output_path_fig, format=args.format, dpi=300, bbox_inches='tight')

if args.interactive:
    plt.show()

if args.table:
    # Print results in a table format
    import pandas as pd

    # Create a DataFrame to hold the results
    data = []
    for class_name, prunes in results.items():
        for prune_rate, metrics in prunes.items():
            row = {
                'class': class_name,
                'prune_rate': prune_rate,
                'FPS': metrics.get('FPS', 0),
                'mAP50-95': metrics.get('mAP50-95', 0),
                'mAP50': metrics.get('mAP50', 0),
                'mAP75': metrics.get('mAP75', 0),
                'model_size_kb': metrics.get('model_size_kb', 0),
                'inference speed (ms)': metrics.get('inference speed (ms)', 0)
            }
            data.append(row)

    df = pd.DataFrame(data)

    df = df.sort_values(by=['class', 'prune_rate'])
    df = df.reset_index(drop=True)

    # Custom order for class rows
    custom_order = [
        'imgsz640', 'imgsz640_q8', 
        'imgsz480', 'imgsz480_q8', 
        'imgsz320', 'imgsz320_q8',
        'imgsz160', 'imgsz160_q8'
    ]
    df['class'] = pd.Categorical(df['class'], categories=custom_order, ordered=True)
    df = df.sort_values(by=['class', 'prune_rate'])

    # Use prune_rate for column names and class for rows. Plot only the specified value of args.x
    df_pivot = df.pivot(index='class', columns='prune_rate', values=args.x).reset_index()
    df_pivot.columns.name = None  # Remove the name of the columns index
    df_pivot = df_pivot.rename(columns={'class': 'Class'})
    # df_pivot = df_pivot.fillna(0)  # Fill NaN values with 0

    # Set the index to 'Class' for better readability
    df_pivot.set_index('Class', inplace=True)

    # Handle decimal or integer formatting
    float_cols = df_pivot.select_dtypes(include=['float', 'float64', 'int', 'int64']).columns
    if args.percentage:
        df_pivot[float_cols] = df_pivot[float_cols].map(lambda x: f"{float(x) * 100:.1f}" if pd.notnull(x) else "")
    elif args.decimals:
        df_pivot[float_cols] = df_pivot[float_cols].map(lambda x: f"{x:.1f}")
    else:
        df_pivot[float_cols] = df_pivot[float_cols].map(lambda x: f"{int(x)}" if pd.notnull(x) else "")

    print("\nResults Table:")
    print(df_pivot.to_string(index=False))

    def background_grad_fun(s: pd.Series, cmap='Blues', low=0, high=0):
        """Background gradient"""
        # a = s.apply(str.split, args="±")
        # a.apply(list.reverse)
        # a = a.apply(list.pop)
        # Only apply to columns that are not 'Class' and can be converted to float
        if s.name == 'Class':
            return ['' for _ in s]
        a = pd.to_numeric(s, errors='coerce')
        range = a.max() - a.min()
        norm = pycolors.Normalize(a.min() - (range * low),
                            a.max() + (range * high))
        normed = norm(a.values)
        c = [pycolors.rgb2hex(x) for x in matplotlib.colormaps.get_cmap(cmap)(normed)]
        # c_text = [pycolors.rgb2hex(x) for x in matplotlib.colormaps.get_cmap('gray')(normed)]
        c_text = ["#FFFFFF" if x > 0.5 else "#000000" for x in normed]
        return [f"background-color: {bg_color}; color: {text_color};" for bg_color, text_color in zip(c, c_text)]

    styled_pivot_table = df_pivot.style.apply(
        background_grad_fun,
        cmap='Blues',
    )

    latex_str = styled_pivot_table.to_latex(
        clines="skip-last;data",
        label="placeholder",
        caption="placeholder",
        convert_css=True,
        position_float="centering",
        multicol_align="|c|",
        hrules=True,
        position="h",
        column_format="cccccccccc",
        # index=False,
        # formatters={"name": str.upper},
        # float_format="{:.1f}".format,
    )

    # Save the table as a LaTeX file
    output_path_latex = output_path + ".tex"
    with open(output_path_latex, "w", encoding="utf-8") as f:
        f.write(latex_str)
    print(f"\nLaTeX table saved to {output_path_latex}")