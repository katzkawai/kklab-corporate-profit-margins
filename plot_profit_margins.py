"""日本の主要業種別 売上高経常利益率の可視化.

出典: 財務省・財務総合政策研究所「法人企業統計調査」年次別調査（確定決算ベース）
第4表「売上高利益率の推移」（金融業・保険業を除く、全規模合計）
- 令和4年度: https://www.mof.go.jp/pri/reference/ssc/results/r4.pdf
- 令和5年度: https://www.mof.go.jp/pri/reference/ssc/results/r5.pdf
- 令和6年度: https://www.mof.go.jp/pri/reference/ssc/results/r6.pdf
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

try:
    import japanize_matplotlib  # noqa: F401
except ImportError:
    raise SystemExit(
        "japanize-matplotlib が見つかりません。"
        "`pip install -r requirements.txt` を実行してください。"
    )

YEARS = ["2022年度", "2023年度", "2024年度"]
LATEST_YEAR = YEARS[-1]

# 売上高経常利益率（%）。リストの並びは YEARS に対応。
DATA = {
    "不動産業": {"sector": "非製造業", "values": [12.8, 13.0, 13.6]},
    "化学工業": {"sector": "製造業", "values": [11.6, 12.1, 12.3]},
    "電気機械器具製造業": {"sector": "製造業", "values": [10.7, 8.8, 11.4]},
    "輸送用機械器具製造業": {"sector": "製造業", "values": [9.2, 11.3, 10.2]},
    "情報通信業": {"sector": "非製造業", "values": [11.3, 11.2, 9.9]},
    "サービス業": {"sector": "非製造業", "values": [8.1, 7.7, 9.1]},
    "運輸業、郵便業": {"sector": "非製造業", "values": [5.5, 5.9, 6.5]},
    "食料品製造業": {"sector": "製造業", "values": [3.7, 4.7, 5.5]},
    "鉄鋼業": {"sector": "製造業", "values": [6.5, 7.0, 5.0]},
    "卸売業、小売業": {"sector": "非製造業", "values": [3.4, 3.5, 3.7]},
}

SECTOR_COLORS = {"製造業": "#4C78A8", "非製造業": "#F58518"}
IMAGES_DIR = Path("images")


def build_dataframe() -> pd.DataFrame:
    rows = {
        industry: dict(zip(YEARS, meta["values"])) | {"区分": meta["sector"]}
        for industry, meta in DATA.items()
    }
    df = pd.DataFrame(rows).T
    df = df.sort_values(LATEST_YEAR, ascending=False)
    return df


def plot_ranking(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = df["区分"].map(SECTOR_COLORS)
    ax.barh(df.index[::-1], df[LATEST_YEAR][::-1], color=colors[::-1])
    for y, value in enumerate(df[LATEST_YEAR][::-1]):
        ax.text(value + 0.15, y, f"{value:.1f}%", va="center", fontsize=10)
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=SECTOR_COLORS[s])
        for s in ("製造業", "非製造業")
    ]
    ax.legend(handles, ("製造業", "非製造業"), loc="lower right")
    ax.set_title(f"業種別 売上高経常利益率（{LATEST_YEAR}・降順）", fontsize=14)
    ax.set_xlabel("売上高経常利益率（%）")
    ax.set_xlim(0, df[LATEST_YEAR].max() * 1.15)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_heatmap(df: pd.DataFrame, path: Path) -> None:
    values = df[YEARS].to_numpy(dtype=float)
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(values, cmap="YlGnBu", aspect="auto")
    ax.set_xticks(range(len(YEARS)), YEARS)
    ax.set_yticks(range(len(df.index)), df.index)
    for i in range(values.shape[0]):
        for j in range(values.shape[1]):
            ax.text(
                j, i, f"{values[i, j]:.1f}",
                ha="center", va="center", fontsize=10,
            )
    fig.colorbar(im, ax=ax, label="売上高経常利益率（%）")
    ax.set_title("業種別 売上高経常利益率の推移（2022–2024年度）", fontsize=14)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def main() -> None:
    IMAGES_DIR.mkdir(exist_ok=True)
    df = build_dataframe()
    ranking_path = IMAGES_DIR / "profit_margin_ranking.png"
    heatmap_path = IMAGES_DIR / "profit_margin_heatmap.png"
    plot_ranking(df, ranking_path)
    plot_heatmap(df, heatmap_path)
    print(f"saved: {ranking_path}")
    print(f"saved: {heatmap_path}")


if __name__ == "__main__":
    main()
