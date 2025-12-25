# {{PROJECT_NAME}} Survey Analysis Skill

## 概要

{{PROJECT_NAME}}のアンケート分析に特化したスキル。
統計分析、クロス集計、テキストマイニング、PMF判定を実行。

## トリガー

以下のキーワードで自動適用:
- アンケート分析
- ユーザー調査
- 統計検定
- クロス集計
- PMF判定
{{CUSTOM_TRIGGERS}}

## コンテキスト

### データ概要
- 回答数: {{RESPONSE_COUNT}}
- 収集期間: {{COLLECTION_PERIOD}}
- 設問数: {{QUESTION_COUNT}}

### ターゲットセグメント
{{TARGET_SEGMENT_DEFINITION}}

### PMF判定基準
{{PMF_CRITERIA}}

## 分析パイプライン

```python
from survey_analysis.core import (
    load_and_prepare_data,
    chi_square_test,
    create_crosstab_with_totals,
    plot_crosstab_heatmap,
    generate_audit_report,
)
from {{PROJECT_CONFIG_MODULE}} import {{PROJECT_CONFIG_CLASS}}

# 1. 設定とデータ読み込み
config = {{PROJECT_CONFIG_CLASS}}()
df = load_and_prepare_data(config)

# 2. データ品質監査
audit = generate_audit_report(df, config)

# 3. Tier 1 クロス集計（PMF判定）
for row_var, col_var in config.crosstab_tiers.get(1, []):
    ct = create_crosstab_with_totals(df, row_var, col_var, config)
    result = chi_square_test(df, row_var, col_var, config)
    fig = plot_crosstab_heatmap(ct, row_var, col_var, config)
    fig.savefig(config.output_dir / f'heatmap_{row_var}_{col_var}.png')

# 4. PMF判定
target_interest = get_target_segment_interest(df, config)
pmf_passed = target_interest['positive_rate'] >= config.pmf_threshold * 100
```

## 質問マッピング

{{QUESTION_MAPPING_TABLE}}

## 出力形式

### クロス集計CSV
```
row_var,col_var,count,percentage
```

### 統計検定結果
```
test,var1,var2,statistic,p_value,effect_size,significance
```

### PMF判定レポート
```markdown
## PMF判定結果

- ターゲット層興味度: XX.X%
- 閾値: 50%
- 判定: 合格/不合格
```

## 参考ファイル

- 設定: `{{CONFIG_PATH}}`
- 生データ: `{{RAW_DATA_PATH}}`
- 出力: `{{OUTPUT_DIR}}`
