# 業種別売上高経常利益率 可視化 — 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 財務省「法人企業統計調査」の実データに基づく業種別売上高経常利益率のグラフ2点（ランキング棒グラフ＋3年ヒートマップ）と分析解説READMEを作成し、GitHub Pagesで公開する。

**Architecture:** 単一Pythonスクリプト（`plot_profit_margins.py`）にデータを埋め込み、matplotlib + japanize-matplotlib でPNGを `images/` に出力。README.md がそのまま GitHub Pages のトップページになる。

**Tech Stack:** Python 3.10+ / pandas / matplotlib / japanize-matplotlib / gh CLI

**Spec:** `docs/superpowers/specs/2026-09-22-industry-profit-margins-design.md`

**データ（財務省 年次別法人企業統計調査 第4表より取得・照合済み、単位: %）:**

| 業種 | 区分 | FY2022 | FY2023 | FY2024 |
|---|---|---|---|---|
| 不動産業 | 非製造業 | 12.8 | 13.0 | 13.6 |
| 化学工業 | 製造業 | 11.6 | 12.1 | 12.3 |
| 電気機械器具製造業 | 製造業 | 10.7 | 8.8 | 11.4 |
| 輸送用機械器具製造業 | 製造業 | 9.2 | 11.3 | 10.2 |
| 情報通信業 | 非製造業 | 11.3 | 11.2 | 9.9 |
| サービス業 | 非製造業 | 8.1 | 7.7 | 9.1 |
| 運輸業、郵便業 | 非製造業 | 5.5 | 5.9 | 6.5 |
| 食料品製造業 | 製造業 | 3.7 | 4.7 | 5.5 |
| 鉄鋼業 | 製造業 | 6.5 | 7.0 | 5.0 |
| 卸売業、小売業 | 非製造業 | 3.4 | 3.5 | 3.7 |

出典PDF: r4.pdf / r5.pdf / r6.pdf（https://www.mof.go.jp/pri/reference/ssc/results/ 配下）

---

### Task 1: 環境セットアップと依存インストール

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: requirements.txt を作成**

```
matplotlib>=3.8
pandas>=2.0
japanize-matplotlib>=1.1
```

- [ ] **Step 2: .gitignore を作成**

```
.venv/
__pycache__/
*.pyc
.DS_Store
```

- [ ] **Step 3: venv を作り依存をインストール**

Run: `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
Expected: `Successfully installed ... japanize-matplotlib ...` で終了

- [ ] **Step 4: import 確認**

Run: `.venv/bin/python -c "import matplotlib, pandas, japanize_matplotlib; print(matplotlib.__version__)"`
Expected: バージョン番号が表示されエラーなし

- [ ] **Step 5: Commit**

```bash
git add requirements.txt .gitignore
git commit -m "chore: add requirements and gitignore"
```

---

### Task 2: 描画スクリプト本体（データ＋棒グラフ＋ヒートマップ）

**Files:**
- Create: `plot_profit_margins.py`

- [ ] **Step 1: plot_profit_margins.py を作成（以下の完全な内容）**

```python
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
```

- [ ] **Step 2: 実行してPNG 2枚を生成**

Run: `.venv/bin/python plot_profit_margins.py`
Expected:
```
saved: images/profit_margin_ranking.png
saved: images/profit_margin_heatmap.png
```

- [ ] **Step 3: PNG を目視確認**

Run: 画像ビューア相当の確認（ReadMediaFile で2枚とも表示）
Expected: 日本語が文字化けしていない／棒グラフはFY2024降順（不動産業13.6が最上位、卸売業小売業3.7が最下位）／ヒートマップの全セルに数値注記がある

- [ ] **Step 4: Commit**

```bash
git add plot_profit_margins.py images/
git commit -m "feat: add profit margin visualization script and charts"
```

---

### Task 3: README.md（GitHub Pages 本文＋分析解説）

**Files:**
- Create: `README.md`

- [ ] **Step 1: README.md を作成（以下の完全な内容）**

````markdown
# 日本の業種別「売上高経常利益率」比較（2022–2024年度）

財務省「法人企業統計調査」の実データをもとに、主要10業種（製造業5・非製造業5）の
**売上高経常利益率**を比較・可視化したプロジェクトです。

## グラフ

### 最新年度（2024年度）ランキング

![業種別 売上高経常利益率 ランキング](images/profit_margin_ranking.png)

### 直近3年度の推移ヒートマップ

![業種別 売上高経常利益率 ヒートマップ](images/profit_margin_heatmap.png)

## データ

| 業種 | 区分 | 2022年度 | 2023年度 | 2024年度 |
|---|---|---:|---:|---:|
| 不動産業 | 非製造業 | 12.8 | 13.0 | 13.6 |
| 化学工業 | 製造業 | 11.6 | 12.1 | 12.3 |
| 電気機械器具製造業 | 製造業 | 10.7 | 8.8 | 11.4 |
| 輸送用機械器具製造業 | 製造業 | 9.2 | 11.3 | 10.2 |
| 情報通信業 | 非製造業 | 11.3 | 11.2 | 9.9 |
| サービス業 | 非製造業 | 8.1 | 7.7 | 9.1 |
| 運輸業、郵便業 | 非製造業 | 5.5 | 5.9 | 6.5 |
| 食料品製造業 | 製造業 | 3.7 | 4.7 | 5.5 |
| 鉄鋼業 | 製造業 | 6.5 | 7.0 | 5.0 |
| 卸売業、小売業 | 非製造業 | 3.4 | 3.5 | 3.7 |

（単位: %。ソートは2024年度降順）

- **指標の定義**: 売上高経常利益率 = 経常利益 ÷ 売上高 × 100
- **出典**: 財務省・財務総合政策研究所「法人企業統計調査」年次別調査（確定決算ベース）
  第4表「売上高利益率の推移」（金融業・保険業を除く、全規模合計）
  - [令和4年度（2023年9月公表）](https://www.mof.go.jp/pri/reference/ssc/results/r4.pdf)
  - [令和5年度（2024年9月公表）](https://www.mof.go.jp/pri/reference/ssc/results/r5.pdf)
  - [令和6年度（2025年9月公表）](https://www.mof.go.jp/pri/reference/ssc/results/r6.pdf)
- **注**: 年次別調査の公表表では卸売業・小売業は集約区分のため、本データも集約値です。

## 分析：なぜ業種によって利益率がこれほど違うのか

### 上位：不動産業・化学・電気機械・輸送用機械・情報通信業

- **不動産業（13.6%）**: 賃貸ビジネスは一度物件を取得すれば継続的な家賃収入が見込め、
  在庫リスクが小さく粗利構造が高い。近年はオフィス・住宅市況の回復や販売用不動産の
  売却益も押し上げ要因。
- **化学工業（12.3%）**: 機能性化学品や電子材料など高付加価値品の比重が高く、
  原料高も価格転嫁で吸収しやすい。差別化された製品ほどプライシングパワーが働く。
- **電気機械器具（11.4%）**: 工場自動化・半導体関連需要の拡大に加え、
  円安による輸出採算の改善が寄与。2023年度の落ち込みは半導体サイクルの調整局面を反映。
- **輸送用機械器具＝自動車中心（10.2%）**: 円安と車両価格の引き上げ（価格転嫁）で
  高水準を維持。ただし販売台数や為替に左右されやすい。
- **情報通信業（9.9%）**: ソフトウェア・プラットフォーム型ビジネスは限界費用が低く、
  売上が伸びるほど利益率が上がる構造。2024年度の低下は人件費・投資負担の増加が背景。

### 中位：サービス業・運輸業

- **サービス業（9.1%）**: 人材サービスや広告など景気回復の恩恵を受け改善傾向。
  労働集約型だが、業態によっては高粗利。
- **運輸業、郵便業（6.5%）**: 燃料費・人件費の上昇に見合う運賃改定（価格転嫁）が
  進み、3年連続で改善。2024年問題を背景とした適正運賃の浸透が寄与。

### 下位：食料品・鉄鋼・卸売業小売業

- **食料品製造業（5.5%）**: 原材料高を値上げで転嫁し改善しているが、
  競争が激しく消費者の価格敏感度高く、利益率は低めに抑えられる。
- **鉄鋼業（5.0%）**: 鉄鉱石・石炭など原料市況とエネルギーコストに大きく左右され、
  高炉の維持など重い設備負担がある一次素材産業。2024年度は中国発の供給過剰と
  国内需要低迷で悪化。
- **卸売業、小売業（3.7%）**: 典型的な「薄利多売」モデル。商流の中間に位置して
  付加価値の付けられる余地が小さく、売上に対する粗利が構造的に薄い。

### 構造的なまとめ

利益率の高低は主に3つの要因で説明できます。

1. **粗利の厚さ（付加価値率）**: 無形資産・差別化製品・専有資産（不動産）を持つ業種ほど高い
2. **プライシングパワー**: 市況や原価上昇を価格に転嫁できるか
3. **資産・コスト構造**: 設備投資・在庫・エネルギー負担が重い業種ほど利益が削られる

## 再現方法

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python plot_profit_margins.py
```

`images/` に2枚のPNGが生成されます。日本語表示には
[japanize-matplotlib](https://github.com/uehara1414/japanize-matplotlib) を使用しています。
````

- [ ] **Step 2: マークダウンと画像リンクの確認**

Run: `ls images/ && grep -c "images/" README.md`
Expected: 2枚のPNGが存在し、grep が 2 を返す

- [ ] **Step 3: Commit**

```bash
git add README.md
git commit -m "docs: add README with analysis for GitHub Pages"
```

---

### Task 4: GitHub 公開と Pages 有効化

**Files:** なし（リモート操作のみ）

- [ ] **Step 1: gh 認証確認**

Run: `gh auth status`
Expected: `Logged in to github.com account ...` と表示。未ログインなら `gh auth login` をユーザーに依頼して中断

- [ ] **Step 2: リポジトリ作成と push**

Run: `gh repo create kklab-corporate-profit-margins --public --source=. --push`
Expected: リモートが作成され main ブランチが push される

- [ ] **Step 3: GitHub Pages 有効化（main / root）**

Run:
```bash
gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pages" \
  -X POST -f "source[branch]=main" -f "source[path]=/"
```
Expected: レスポンス JSON に `"status": "built"` または `"building"` を含む

- [ ] **Step 4: 公開URLの疎通確認**

Run: `sleep 30 && curl -sL -o /dev/null -w "%{http_code}" "$(gh api "repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/pages" -q .html_url)"`
Expected: `200`（ビルド中で 404 の場合は 1〜2 分待って再試行）
画像も確認: `<URL>/images/profit_margin_ranking.png` が 200 を返すこと

- [ ] **Step 5: ユーザーへ公開URLを報告**
