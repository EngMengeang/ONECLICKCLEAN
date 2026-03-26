import matplotlib.pyplot as plt
import pandas as pd


def draw_boxplots(data: pd.DataFrame, color: str, title: str):
    """Draw a grid of box plots (2 per row) for each column in data."""
    cols_list = data.columns.tolist()
    if not cols_list:
        return None

    n_c = 2
    n_r = -(-len(cols_list) // n_c)  # ceil division
    fig, axes = plt.subplots(n_r, n_c, figsize=(14, n_r * 4))
    fig.suptitle(title, fontsize=14, fontweight="bold", y=1.01)
    axes = axes.flatten() if n_r * n_c > 1 else [axes]

    for i, c in enumerate(cols_list):
        axes[i].boxplot(
            data[c].dropna(),
            patch_artist=True,
            boxprops=dict(facecolor=color, color="#1a1a2e"),
            medianprops=dict(color="red", linewidth=2),
            flierprops=dict(marker="o", color="orange", markersize=5),
        )
        axes[i].set_title(c, fontsize=11, fontweight="bold")
        axes[i].set_ylabel("Value")

    for j in range(len(cols_list), len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    return fig
