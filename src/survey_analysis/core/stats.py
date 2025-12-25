"""
統計分析モジュール

基本統計量、統計検定（χ²、t検定、ANOVA、相関）を提供。
"""

from typing import Dict, List, Optional, Any, Tuple
import warnings

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import chi2_contingency, ttest_ind, f_oneway, spearmanr
import statsmodels.api as sm
from statsmodels.stats.multitest import multipletests

from survey_analysis.base.config import SurveyConfig

warnings.filterwarnings('ignore')


# =============================================================================
# 基本統計量
# =============================================================================

def calculate_frequency_distribution(
    df: pd.DataFrame,
    column: str,
    normalize: bool = False
) -> pd.DataFrame:
    """
    度数分布を計算

    Args:
        df: データフレーム
        column: 対象カラム名
        normalize: 割合を計算するか

    Returns:
        pd.DataFrame: 度数分布表
    """
    counts = df[column].value_counts(dropna=False)

    result = pd.DataFrame({
        'choice': counts.index,
        'count': counts.values
    })

    if normalize:
        result['percentage'] = (result['count'] / result['count'].sum() * 100).round(2)

    return result


def calculate_summary_statistics(
    df: pd.DataFrame,
    column: str
) -> Dict[str, Any]:
    """
    要約統計量を計算

    Args:
        df: データフレーム
        column: 対象カラム名

    Returns:
        dict: 要約統計量
    """
    series = df[column].dropna()

    # 数値型の場合
    if pd.api.types.is_numeric_dtype(series):
        return {
            'count': int(len(series)),
            'mean': float(series.mean()),
            'std': float(series.std()),
            'min': float(series.min()),
            'max': float(series.max()),
            'median': float(series.median()),
            'q1': float(series.quantile(0.25)),
            'q3': float(series.quantile(0.75)),
            'skewness': float(series.skew()),
            'kurtosis': float(series.kurtosis())
        }

    # カテゴリカル型の場合
    value_counts = series.value_counts()
    return {
        'count': int(len(series)),
        'unique': int(series.nunique()),
        'mode': value_counts.index[0] if len(value_counts) > 0 else None,
        'mode_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
        'mode_percentage': float(value_counts.iloc[0] / len(series) * 100) if len(value_counts) > 0 else 0
    }


def calculate_all_frequencies(
    df: pd.DataFrame,
    config: SurveyConfig,
    include_missing: bool = True
) -> Dict[str, pd.DataFrame]:
    """
    全質問の度数分布を計算

    Args:
        df: データフレーム
        config: SurveyConfig インスタンス
        include_missing: 欠損値を含めるか

    Returns:
        dict: 質問ID → 度数分布DataFrameのマッピング
    """
    results = {}

    for q_id, col_name in config.questions.items():
        if col_name not in df.columns:
            print(f"警告: カラム '{col_name}' が見つかりません (ID: {q_id})")
            continue

        freq = calculate_frequency_distribution(df, col_name, normalize=True)

        if not include_missing:
            freq = freq[freq['choice'].notna()]

        results[q_id] = freq

    return results


def analyze_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    欠損値を分析

    Args:
        df: データフレーム

    Returns:
        pd.DataFrame: 欠損値分析結果
    """
    missing_counts = df.isnull().sum()
    missing_pcts = (missing_counts / len(df) * 100).round(2)

    result = pd.DataFrame({
        'column': missing_counts.index,
        'missing_count': missing_counts.values,
        'missing_percentage': missing_pcts.values
    })

    return result.sort_values('missing_count', ascending=False)


# =============================================================================
# 統計検定
# =============================================================================

def chi_square_test(
    df: pd.DataFrame,
    var1: str,
    var2: str,
    config: Optional[SurveyConfig] = None
) -> Dict[str, Any]:
    """
    カイ二乗検定を実行

    Args:
        df: データフレーム
        var1: 行変数（質問IDまたはカラム名）
        var2: 列変数（質問IDまたはカラム名）
        config: SurveyConfig（質問ID→カラム名変換用）

    Returns:
        dict: 検定結果（chi2, p_value, dof, cramers_v等）
    """
    # カラム名解決
    col1 = config.get_column_name(var1) if config else var1
    col2 = config.get_column_name(var2) if config else var2

    if col1 not in df.columns:
        raise ValueError(f"カラムが見つかりません: {col1}")
    if col2 not in df.columns:
        raise ValueError(f"カラムが見つかりません: {col2}")

    # クロス集計表作成
    contingency_table = pd.crosstab(df[col1], df[col2])

    # 空のセルがある場合の処理
    if contingency_table.shape[0] < 2 or contingency_table.shape[1] < 2:
        raise ValueError(f"クロス集計表が小さすぎます（2x2未満）: {var1} x {var2}")

    # カイ二乗検定
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)

    # Cramer's V（効果量）
    n = contingency_table.sum().sum()
    min_dim = min(contingency_table.shape[0] - 1, contingency_table.shape[1] - 1)
    cramers_v = np.sqrt(chi2 / (n * min_dim)) if min_dim > 0 else 0

    return {
        'test': 'chi_square',
        'var1': var1,
        'var2': var2,
        'chi2': float(chi2),
        'p_value': float(p_value),
        'dof': int(dof),
        'cramers_v': float(cramers_v),
        'expected': expected.tolist(),
        'observed': contingency_table.values.tolist()
    }


def t_test_independent(
    df: pd.DataFrame,
    group_var: str,
    value_var: str,
    group1: Any,
    group2: Any,
    config: Optional[SurveyConfig] = None
) -> Dict[str, Any]:
    """
    独立2標本t検定を実行

    Args:
        df: データフレーム
        group_var: グループ変数
        value_var: 値変数
        group1: グループ1の値
        group2: グループ2の値
        config: SurveyConfig

    Returns:
        dict: 検定結果
    """
    # カラム名解決
    group_col = config.get_column_name(group_var) if config else group_var
    value_col = config.get_column_name(value_var) if config else value_var

    if group_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {group_col}")
    if value_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {value_col}")

    # グループ抽出
    data1 = df[df[group_col] == group1][value_col].dropna()
    data2 = df[df[group_col] == group2][value_col].dropna()

    if len(data1) < 2 or len(data2) < 2:
        raise ValueError(f"サンプルサイズが不足しています: group1={len(data1)}, group2={len(data2)}")

    # t検定
    t_stat, p_value = ttest_ind(data1, data2)

    # Cohen's d（効果量）
    pooled_std = np.sqrt(
        ((len(data1) - 1) * data1.std() ** 2 + (len(data2) - 1) * data2.std() ** 2) /
        (len(data1) + len(data2) - 2)
    )
    cohens_d = (data1.mean() - data2.mean()) / pooled_std if pooled_std > 0 else 0

    return {
        'test': 't_test',
        'group_var': group_var,
        'value_var': value_var,
        'group1': str(group1),
        'group2': str(group2),
        't_statistic': float(t_stat),
        'p_value': float(p_value),
        'cohens_d': float(cohens_d),
        'n1': int(len(data1)),
        'n2': int(len(data2)),
        'mean1': float(data1.mean()),
        'mean2': float(data2.mean()),
        'std1': float(data1.std()),
        'std2': float(data2.std())
    }


def anova_test(
    df: pd.DataFrame,
    group_var: str,
    value_var: str,
    config: Optional[SurveyConfig] = None
) -> Dict[str, Any]:
    """
    一元配置分散分析（ANOVA）を実行

    Args:
        df: データフレーム
        group_var: グループ変数
        value_var: 値変数
        config: SurveyConfig

    Returns:
        dict: 検定結果
    """
    # カラム名解決
    group_col = config.get_column_name(group_var) if config else group_var
    value_col = config.get_column_name(value_var) if config else value_var

    if group_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {group_col}")
    if value_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {value_col}")

    # グループ別データ
    groups = df.groupby(group_col)[value_col].apply(list).to_dict()
    group_data = [np.array(v) for v in groups.values() if len(v) > 0]

    if len(group_data) < 2:
        raise ValueError(f"グループ数が不足しています: {len(group_data)}グループ")

    # ANOVA
    f_stat, p_value = f_oneway(*group_data)

    # η²（効果量）
    all_data = np.concatenate(group_data)
    grand_mean = all_data.mean()
    ss_between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in group_data)
    ss_total = sum((all_data - grand_mean) ** 2)
    eta_squared = ss_between / ss_total if ss_total > 0 else 0

    return {
        'test': 'anova',
        'group_var': group_var,
        'value_var': value_var,
        'f_statistic': float(f_stat),
        'p_value': float(p_value),
        'eta_squared': float(eta_squared),
        'n_groups': len(group_data),
        'group_sizes': {k: len(v) for k, v in groups.items()}
    }


def correlation_test(
    df: pd.DataFrame,
    var1: str,
    var2: str,
    method: str = 'spearman',
    config: Optional[SurveyConfig] = None
) -> Dict[str, Any]:
    """
    相関分析を実行

    Args:
        df: データフレーム
        var1: 変数1
        var2: 変数2
        method: 相関係数の種類（'spearman', 'pearson', 'kendall'）
        config: SurveyConfig

    Returns:
        dict: 検定結果
    """
    # カラム名解決
    col1 = config.get_column_name(var1) if config else var1
    col2 = config.get_column_name(var2) if config else var2

    if col1 not in df.columns:
        raise ValueError(f"カラムが見つかりません: {col1}")
    if col2 not in df.columns:
        raise ValueError(f"カラムが見つかりません: {col2}")

    # 欠損値を除去
    valid_data = df[[col1, col2]].dropna()

    if len(valid_data) < 3:
        raise ValueError(f"サンプルサイズが不足しています: {len(valid_data)}件")

    # 順序カテゴリカルの場合はコード化
    x = valid_data[col1]
    y = valid_data[col2]

    if hasattr(x, 'cat') and x.cat.ordered:
        x = x.cat.codes
    if hasattr(y, 'cat') and y.cat.ordered:
        y = y.cat.codes

    # 相関係数計算
    if method == 'spearman':
        corr, p_value = spearmanr(x, y)
    elif method == 'pearson':
        corr, p_value = stats.pearsonr(x, y)
    elif method == 'kendall':
        corr, p_value = stats.kendalltau(x, y)
    else:
        raise ValueError(f"未対応の相関手法: {method}（'spearman', 'pearson', 'kendall' のいずれかを指定）")

    return {
        'test': 'correlation',
        'method': method,
        'var1': var1,
        'var2': var2,
        'correlation': float(corr),
        'p_value': float(p_value),
        'n': int(len(valid_data))
    }


def apply_fdr_correction(
    p_values: List[float],
    method: str = 'fdr_bh',
    alpha: float = 0.05
) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """
    多重検定補正（FDR）を適用

    Args:
        p_values: p値のリスト
        method: 補正方法（'fdr_bh', 'bonferroni', 'holm'等）
        alpha: 有意水準

    Returns:
        tuple: (reject配列, 補正後p値, corrected_alpha_sidak, corrected_alpha_bonferroni)
    """
    return multipletests(p_values, alpha=alpha, method=method)


def run_all_chi_square_tests(
    df: pd.DataFrame,
    pairs: List[Tuple[str, str]],
    config: SurveyConfig,
    apply_correction: bool = True
) -> pd.DataFrame:
    """
    複数のカイ二乗検定を実行し、FDR補正を適用

    Args:
        df: データフレーム
        pairs: 検定する変数ペアのリスト
        config: SurveyConfig
        apply_correction: FDR補正を適用するか

    Returns:
        pd.DataFrame: 検定結果一覧
    """
    results = []

    for var1, var2 in pairs:
        result = chi_square_test(df, var1, var2, config)
        results.append(result)

    # DataFrameに変換
    df_results = pd.DataFrame(results)

    # エラーがない結果のみでFDR補正
    if apply_correction and 'p_value' in df_results.columns:
        valid_mask = df_results['p_value'].notna()
        valid_p_values = df_results.loc[valid_mask, 'p_value'].values

        if len(valid_p_values) > 0:
            _, corrected_p, _, _ = apply_fdr_correction(valid_p_values, alpha=config.alpha)
            df_results.loc[valid_mask, 'p_value_corrected'] = corrected_p
            df_results.loc[valid_mask, 'significant'] = corrected_p < config.alpha

    return df_results


def interpret_effect_size(
    effect_size: float,
    effect_type: str = 'cramers_v'
) -> str:
    """
    効果量を解釈

    Args:
        effect_size: 効果量
        effect_type: 効果量の種類

    Returns:
        str: 解釈テキスト
    """
    if effect_type == 'cramers_v':
        if effect_size < 0.1:
            return "効果なし"
        elif effect_size < 0.3:
            return "弱い関連"
        elif effect_size < 0.5:
            return "中程度の関連"
        else:
            return "強い関連"

    elif effect_type == 'cohens_d':
        abs_d = abs(effect_size)
        if abs_d < 0.2:
            return "効果なし"
        elif abs_d < 0.5:
            return "小さい効果"
        elif abs_d < 0.8:
            return "中程度の効果"
        else:
            return "大きい効果"

    elif effect_type == 'eta_squared':
        if effect_size < 0.01:
            return "効果なし"
        elif effect_size < 0.06:
            return "小さい効果"
        elif effect_size < 0.14:
            return "中程度の効果"
        else:
            return "大きい効果"

    elif effect_type == 'correlation':
        abs_r = abs(effect_size)
        if abs_r < 0.1:
            return "相関なし"
        elif abs_r < 0.3:
            return "弱い相関"
        elif abs_r < 0.5:
            return "中程度の相関"
        elif abs_r < 0.7:
            return "強い相関"
        else:
            return "非常に強い相関"

    return "不明"
