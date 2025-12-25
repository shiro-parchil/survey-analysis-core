---
description: {{PROJECT_NAME}}アンケート分析を実行
---

# /survey-analysis

{{PROJECT_NAME}}のアンケートデータを包括的に分析し、レポートを生成する。

## 実行内容

1. **データ読み込み**
   - `{{RAW_DATA_PATH}}` からCSV読み込み
   - エンコーディング自動検出
   - 欠損値処理

2. **基本統計**
   - 全設問の度数分布
   - 要約統計量

3. **クロス集計（Tier別）**
   {{TIER_DEFINITIONS}}

4. **統計検定**
   - カイ二乗検定
   - FDR補正

5. **テキスト分析**（自由記述がある場合）
   - 形態素解析
   - 頻出語抽出
   - ワードクラウド生成

6. **レポート生成**
   - Markdown形式
   - 主要インサイト
   - 次アクション提案

## 出力先

```
{{OUTPUT_DIR}}/
├── csv/
│   ├── basic_statistics.csv
│   ├── cross_age_x_interest.csv
│   └── ...
├── figures/
│   ├── heatmap_age_interest.png
│   └── ...
└── reports/
    ├── analysis_report.md
    └── business_insights.md
```

## 使用方法

```bash
/survey-analysis
```

## カスタマイズ

### Tier定義を変更

`{{CONFIG_PATH}}` の `crosstab_tiers` を編集:

```python
@property
def crosstab_tiers(self) -> dict:
    return {
        1: [  # PMF判定（最重要）
            ('age', 'interest'),
            ('loneliness', 'interest'),
        ],
        2: [  # 設計検証
            ('age', 'payment_intent'),
        ],
    }
```

### PMF判定基準を変更

```python
@property
def pmf_threshold(self) -> float:
    return 0.50  # 50%以上で合格
```
