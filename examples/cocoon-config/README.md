# Cocoon アンケート分析設定例

[survey-analysis-core](../../) パッケージを使用した Cocoon プロジェクトの実装例。

## 概要

- **回答数**: 289件
- **収集期間**: 2025-12-05〜2025-12-06
- **設問数**: 67問（7セクション）
- **ターゲット**: 23-34歳、オタク趣味、SNS疲れ層

## ファイル構成

```
cocoon-config/
├── config.py              # CocoonSurveyConfig 実装
├── README.md              # このファイル
└── (他の設定ファイルは本リポジトリに残存)
```

## 使用方法

```python
from examples.cocoon_config.config import CocoonSurveyConfig
from survey_analysis.core import load_and_prepare_data, chi_square_test

# 設定インスタンス作成
config = CocoonSurveyConfig()

# データ読み込み
df = load_and_prepare_data(config)
print(f"読み込み完了: {len(df)} 件")

# Tier 1 クロス集計（PMF判定）
for row_var, col_var in config.crosstab_tiers.get(1, []):
    result = chi_square_test(df, row_var, col_var, config)
    print(f"{row_var} × {col_var}: χ² = {result['chi2']:.2f}, p = {result['p_value']:.4f}")
```

## PMF判定基準

| 指標 | 閾値 | 根拠 |
|-----|------|------|
| 興味度 | 50%以上 | ターゲット層（23-34歳）の「興味あり」回答 |
| 課金意向 | 30%以上 | 「月額500円なら払う」層 |
| 継続希望 | 40%以上 | 「週1回以上使いたい」層 |

## セグメント定義

| セグメント | 定義 |
|-----------|------|
| `is_target_age` | 23-34歳 |
| `is_lonely` | 孤独感「時々ある」以上 |
| `is_very_lonely` | 孤独感「しばしばある」以上 |
| `has_otaku_hobby` | アニメ・ゲーム・Vtuber趣味 |
| `is_sns_dissatisfied` | SNS満足度「不満」以下 |

## Tier定義

| Tier | 目的 | クロス集計例 |
|------|------|------------|
| 1 | PMF判定 | 年齢×興味度、孤独感×興味度 |
| 2 | 設計検証 | 年齢×期間限定評価、AI機能×年齢 |
| 3 | ペルソナ検証 | 趣味×興味度、職業×活動時間 |
| 4 | 運用設計 | DM禁止×性別、投稿頻度×年齢 |

## 本リポジトリとの関係

この設定ファイルは **サンプル** として survey-analysis-core パッケージに含まれています。

実際の Cocoon プロジェクトのアンケート分析は、[group-chat-sns-business](https://github.com/shiro-parchil/group-chat-sns-business) リポジトリの以下のファイルを使用:

- `tools/surveys/analysis/scripts/config.py`
- `tools/surveys/analysis/scripts/run_pipeline.py`
