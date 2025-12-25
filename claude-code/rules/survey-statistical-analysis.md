# アンケート統計分析ルール

survey-analysis-coreパッケージを使用した統計分析の標準ルール。

## 統計検定

### カイ二乗検定（χ²）

カテゴリカル変数間の独立性を検定。

```python
from survey_analysis.core import chi_square_test

result = chi_square_test(df, 'age', 'interest', config)
# result: {'chi2': float, 'p_value': float, 'dof': int, 'cramers_v': float}
```

**効果量の解釈（Cramer's V）**:
- 0.1未満: 弱い関連
- 0.1-0.3: 中程度の関連
- 0.3以上: 強い関連

### t検定

2群間の平均値差を検定。

```python
from survey_analysis.core import t_test_independent

result = t_test_independent(df, 'score', 'gender', config)
# result: {'t_stat': float, 'p_value': float, 'cohens_d': float}
```

**効果量の解釈（Cohen's d）**:
- 0.2未満: 小さい効果
- 0.2-0.8: 中程度の効果
- 0.8以上: 大きい効果

### ANOVA

3群以上の平均値差を検定。

```python
from survey_analysis.core import anova_test

result = anova_test(df, 'score', 'age_group', config)
# result: {'f_stat': float, 'p_value': float, 'eta_squared': float}
```

**効果量の解釈（η²）**:
- 0.01未満: 小さい効果
- 0.01-0.06: 中程度の効果
- 0.06以上: 大きい効果

### 相関分析

順序尺度間の相関を検定。

```python
from survey_analysis.core import correlation_test

result = correlation_test(df, 'loneliness', 'interest', config)
# result: {'rho': float, 'p_value': float}
```

**相関係数の解釈（Spearman ρ）**:
- 0.3未満: 弱い相関
- 0.3-0.7: 中程度の相関
- 0.7以上: 強い相関

## 多重検定補正

複数の検定を行う場合、FDR補正（Benjamini-Hochberg法）を適用。

```python
from survey_analysis.core import apply_fdr_correction

corrected = apply_fdr_correction(results, alpha=0.05)
```

## 有意水準

| 記号 | p値 | 解釈 |
|-----|-----|------|
| *** | p < 0.001 | 非常に強い関連 |
| ** | p < 0.01 | 強い関連 |
| * | p < 0.05 | 統計的に有意 |
| ns | p ≥ 0.05 | 有意でない |

## クロス集計のTier優先度

| Tier | 目的 | 例 |
|------|------|-----|
| 1 | PMF判定 | 年齢×興味度、孤独感×興味度 |
| 2 | 設計検証 | 年齢×期間限定評価、AI機能×年齢 |
| 3 | ペルソナ検証 | 職業×活動時間帯 |
| 4 | 運用設計 | 参加頻度×年齢 |

## レポート記載必須項目

1. サンプルサイズ（N）
2. 検定名と検定統計量
3. p値（補正前後）
4. 効果量
5. 解釈（日本語）

```markdown
## 年齢と新サービス興味の関係

カイ二乗検定を実施した結果、年齢と新サービス興味の間に
統計的に有意な関連が認められた（χ²(8) = 25.3, p < .01, V = 0.21）。
20-30代で興味度が高い傾向が確認された。
```

## 注意事項

- サンプルサイズが大きいと些細な差でも有意になる
- 効果量も必ず確認する
- 因果関係ではなく相関関係である点を明記
