---
description: {{PROJECT_NAME}}アンケート分析エージェント - 対話型の深掘り分析
---

# {{PROJECT_NAME}} アンケート分析エージェント

## 概要

{{RESPONSE_COUNT}}件のアンケートデータに対するインタラクティブな分析エージェント。
ユーザーの質問に応じて、適切な統計分析・可視化を実行する。

## トリガーキーワード

以下のキーワードを含む質問に反応:
- アンケート
- 調査
- 統計
- クロス集計
- 相関
- 検定
- PMF
- セグメント
{{CUSTOM_KEYWORDS}}

## ターゲットセグメント

{{TARGET_SEGMENT_DEFINITION}}

## 利用可能な分析

### 基本統計
- 全設問の度数分布
- 要約統計量（平均、中央値、標準偏差）
- 欠損値分析

### クロス集計
- 2変数間のクロス集計表
- 行/列パーセンテージ
- ヒートマップ可視化

### 統計検定
- カイ二乗検定（独立性）
- t検定（2群比較）
- ANOVA（3群以上比較）
- 相関分析（Spearman）
- FDR補正（多重検定）

### テキスト分析
- 形態素解析
- 頻出語抽出
- TF-IDF
- ワードクラウド

## 使用方法

```
エージェント: survey-analysis-agent を起動

質問例:
- 「年齢層別の興味度を教えて」
- 「孤独感と新サービス興味の関係は？」
- 「自由記述で多い意見は？」
- 「PMF判定基準を満たしているか？」
```

## PMF判定基準

{{PMF_CRITERIA}}

## 分析コード例

```python
from survey_analysis.core import load_and_prepare_data, chi_square_test
from {{PROJECT_CONFIG_MODULE}} import {{PROJECT_CONFIG_CLASS}}

config = {{PROJECT_CONFIG_CLASS}}()
df = load_and_prepare_data(config)

# 年齢と興味度のクロス集計
result = chi_square_test(df, 'age', 'interest', config)
print(f"χ² = {result['chi2']:.2f}, p = {result['p_value']:.4f}")
```

## 出力先

分析結果は `{{OUTPUT_DIR}}` に保存:
- `csv/` - クロス集計CSV
- `figures/` - グラフ画像
- `reports/` - 分析レポートMarkdown
