# survey-analysis-core

汎用アンケート解析コアライブラリ。依存注入パターンにより、複数のアンケートプロジェクトで再利用可能。

## 特徴

- **プロジェクト非依存**: `SurveyConfig` 抽象クラスを実装するだけで任意のアンケートに適用可能
- **ゼロコスト原則**: LLM APIを使用せず、正規表現とscikit-learnで実装
- **日本語対応**: Janome形態素解析、japanize-matplotlib、日本語ストップワード
- **統計分析**: χ²検定、t検定、ANOVA、相関分析、FDR補正
- **可視化**: ヒートマップ、棒グラフ、円グラフ、ワードクラウド

## インストール

```bash
# 基本インストール
pip install git+https://github.com/shiro-parchil/survey-analysis-core.git

# テキスト分析機能を含む
pip install "survey-analysis-core[text] @ git+https://github.com/shiro-parchil/survey-analysis-core.git"

# 全機能
pip install "survey-analysis-core[all] @ git+https://github.com/shiro-parchil/survey-analysis-core.git"
```

## クイックスタート

### 1. プロジェクト固有の設定クラスを作成

```python
from pathlib import Path
from survey_analysis.base import SurveyConfig

class MySurveyConfig(SurveyConfig):
    """プロジェクト固有の設定"""

    @property
    def questions(self) -> dict:
        return {
            'age': 'Q1. 年齢',
            'gender': 'Q2. 性別',
            'satisfaction': 'Q3. 満足度',
            'interest': 'Q4. 新サービスへの興味',
        }

    @property
    def raw_data_path(self) -> Path:
        return Path('data/survey_responses.csv')

    @property
    def output_dir(self) -> Path:
        return Path('output/analysis')

    @property
    def category_orders(self) -> dict:
        return {
            'age': ['10代', '20代', '30代', '40代', '50代以上'],
            'satisfaction': ['非常に不満', '不満', '普通', '満足', '非常に満足'],
        }
```

### 2. 分析を実行

```python
from survey_analysis.core import (
    load_and_prepare_data,
    chi_square_test,
    create_crosstab_with_totals,
    plot_crosstab_heatmap,
)

# 設定インスタンス作成
config = MySurveyConfig()

# データ読み込み
df = load_and_prepare_data(config)
print(f"読み込み完了: {len(df)} 件")

# カイ二乗検定
result = chi_square_test(df, 'age', 'satisfaction', config)
print(f"χ² = {result['chi2']:.2f}, p = {result['p_value']:.4f}")

# クロス集計
ct = create_crosstab_with_totals(df, 'age', 'satisfaction', config)
print(ct)

# ヒートマップ
fig = plot_crosstab_heatmap(ct, 'age', 'satisfaction', config)
fig.savefig(config.output_dir / 'heatmap_age_satisfaction.png')
```

## パッケージ構成

```
survey-analysis-core/
├── src/survey_analysis/
│   ├── __init__.py
│   ├── base/                    # 抽象クラス（拡張ポイント）
│   │   ├── config.py            # SurveyConfig 抽象クラス
│   │   └── report.py            # ReportGenerator 抽象クラス
│   ├── core/                    # コア分析機能
│   │   ├── loader.py            # データ読み込み・前処理
│   │   ├── stats.py             # 統計検定
│   │   ├── crosstab.py          # クロス集計
│   │   ├── viz.py               # 可視化
│   │   ├── text.py              # テキスト分析
│   │   └── audit.py             # データ品質監査
│   └── utils/
│       └── parsers.py           # ユーティリティ関数
├── claude-code/                 # Claude Code設定テンプレート
├── google-forms-generator/      # GASテンプレート
├── examples/                    # 実装サンプル
│   └── cocoon-config/           # Cocoon設定例
├── tests/
├── pyproject.toml
└── README.md
```

## 主要モジュール

### survey_analysis.core.loader

データ読み込みと前処理。

```python
from survey_analysis.core import load_and_prepare_data, validate_data

# データ読み込み（エンコーディング自動検出）
df = load_and_prepare_data(config)

# データ検証
validation = validate_data(df, config)
print(validation['errors'])
```

### survey_analysis.core.stats

統計検定。

```python
from survey_analysis.core import (
    chi_square_test,
    t_test_independent,
    anova_test,
    correlation_test,
    apply_fdr_correction,
)

# カイ二乗検定
result = chi_square_test(df, 'age', 'interest', config)

# t検定
result = t_test_independent(df, 'satisfaction_score', 'gender', config)

# ANOVA
result = anova_test(df, 'satisfaction_score', 'age', config)

# 相関分析
result = correlation_test(df, 'age_numeric', 'satisfaction_score', config)

# FDR補正（多重検定）
corrected = apply_fdr_correction(results_list, alpha=0.05)
```

### survey_analysis.core.crosstab

クロス集計。

```python
from survey_analysis.core import (
    create_crosstab,
    create_crosstab_with_totals,
    create_percentage_crosstab,
    analyze_crosstabs_by_tier,
)

# 基本クロス集計
ct = create_crosstab(df, 'age', 'interest', config)

# 合計行・列付き
ct = create_crosstab_with_totals(df, 'age', 'interest', config)

# パーセンテージ
ct_pct = create_percentage_crosstab(df, 'age', 'interest', config, normalize='index')

# Tier別一括分析
tier_definitions = {
    1: [('age', 'interest'), ('loneliness', 'interest')],
    2: [('age', 'payment_intent')],
}
results = analyze_crosstabs_by_tier(df, tier_definitions, config)
```

### survey_analysis.core.viz

可視化。

```python
from survey_analysis.core import (
    plot_crosstab_heatmap,
    plot_bar_chart,
    plot_stacked_bar,
    plot_pie_chart,
)

# ヒートマップ
fig = plot_crosstab_heatmap(ct, 'age', 'interest', config)

# 棒グラフ
fig = plot_bar_chart(df, 'age', config, title='年齢分布')

# 積み上げ棒グラフ
fig = plot_stacked_bar(ct, 'age', 'interest', config)

# 円グラフ
fig = plot_pie_chart(df, 'gender', config)
```

### survey_analysis.core.text

テキスト分析（要 `[text]` オプション）。

```python
from survey_analysis.core import (
    tokenize_japanese_text,
    extract_word_frequency,
    generate_wordcloud,
)

# 形態素解析
tokens = tokenize_japanese_text("日本語のテキストを解析します", config)

# 頻出語抽出
freq = extract_word_frequency(df['freetext_column'], config, top_n=50)

# ワードクラウド
fig = generate_wordcloud(df['freetext_column'], config)
fig.savefig('wordcloud.png')
```

### survey_analysis.core.audit

データ品質監査。

```python
from survey_analysis.core import generate_audit_report, get_data_profile

# 監査レポート生成
report = generate_audit_report(df, config)
print(report['summary'])

# データプロファイル
profile = get_data_profile(df, config)
```

## SurveyConfig 抽象クラス

必須プロパティ:

| プロパティ | 型 | 説明 |
|-----------|---|------|
| `questions` | `Dict[str, str]` | 質問ID → カラム名のマッピング |
| `raw_data_path` | `Path` | アンケートCSVのパス |
| `output_dir` | `Path` | 出力ディレクトリ |

オプションプロパティ:

| プロパティ | 型 | デフォルト | 説明 |
|-----------|---|-----------|------|
| `category_orders` | `Dict[str, List[str]]` | `{}` | カテゴリカル変数の順序 |
| `stopwords` | `List[str]` | `[]` | テキスト分析用ストップワード |
| `alpha` | `float` | `0.05` | 有意水準 |
| `encoding` | `str` | `'auto'` | ファイルエンコーディング |
| `figure_style` | `Dict` | matplotlib defaults | グラフスタイル設定 |

## テスト

```bash
# テスト実行
pytest

# カバレッジ付き
pytest --cov=survey_analysis --cov-report=html
```

## ライセンス

MIT License

## 変更履歴

### v1.0.0 (2025-12-25)

- 初回リリース
- `SurveyConfig` 抽象クラスによる依存注入パターン
- コアモジュール: loader, stats, crosstab, viz, text, audit
- Claude Code設定テンプレート
- GASテンプレート
- Cocoon実装サンプル
