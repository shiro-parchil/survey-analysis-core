"""
クロス集計モジュール

カテゴリカル変数間のクロス集計と分析を提供。
"""

from typing import Dict, List, Optional, Tuple, Any, Literal
import warnings

import pandas as pd
import numpy as np

from survey_analysis.base.config import SurveyConfig

warnings.filterwarnings('ignore')


def create_crosstab(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    config: Optional[SurveyConfig] = None,
    normalize: Optional[Literal['index', 'columns', 'all']] = None,
    margins: bool = False
) -> pd.DataFrame:
    """
    クロス集計表を作成

    Args:
        df: データフレーム
        row_var: 行変数（質問IDまたはカラム名）
        col_var: 列変数（質問IDまたはカラム名）
        config: SurveyConfig（質問ID→カラム名変換用）
        normalize: 正規化方法（None, 'index', 'columns', 'all'）
        margins: 合計行/列を追加するか

    Returns:
        pd.DataFrame: クロス集計表
    """
    # カラム名解決
    row_col = config.get_column_name(row_var) if config else row_var
    col_col = config.get_column_name(col_var) if config else col_var

    if row_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {row_col}")
    if col_col not in df.columns:
        raise ValueError(f"カラムが見つかりません: {col_col}")

    # クロス集計
    ct = pd.crosstab(
        df[row_col],
        df[col_col],
        margins=margins,
        margins_name='合計'
    )

    # 正規化
    if normalize:
        ct = ct.div(ct.sum(axis=1 if normalize == 'index' else 0), axis=0 if normalize == 'index' else 1)
        ct = ct * 100

    return ct


def create_crosstab_with_totals(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    config: Optional[SurveyConfig] = None
) -> pd.DataFrame:
    """
    合計行・列付きクロス集計表を作成

    Args:
        df: データフレーム
        row_var: 行変数
        col_var: 列変数
        config: SurveyConfig

    Returns:
        pd.DataFrame: 合計付きクロス集計表
    """
    return create_crosstab(df, row_var, col_var, config, margins=True)


def create_crosstab_percentage(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    config: Optional[SurveyConfig] = None,
    by: str = 'row'
) -> pd.DataFrame:
    """
    パーセンテージ表示のクロス集計表を作成

    Args:
        df: データフレーム
        row_var: 行変数
        col_var: 列変数
        config: SurveyConfig
        by: 'row'（行ごと）または'column'（列ごと）

    Returns:
        pd.DataFrame: パーセンテージクロス集計表
    """
    normalize = 'index' if by == 'row' else 'columns'
    return create_crosstab(df, row_var, col_var, config, normalize=normalize)


def create_multiselect_crosstab(
    df: pd.DataFrame,
    row_var: str,
    col_var: str,
    config: Optional[SurveyConfig] = None,
    delimiter: str = '、'
) -> pd.DataFrame:
    """
    複数選択肢を含むクロス集計表を作成

    Args:
        df: データフレーム
        row_var: 行変数
        col_var: 列変数（複数選択可能な質問）
        config: SurveyConfig
        delimiter: 複数選択の区切り文字

    Returns:
        pd.DataFrame: 展開されたクロス集計表
    """
    # カラム名解決
    row_col = config.get_column_name(row_var) if config else row_var
    col_col = config.get_column_name(col_var) if config else col_var

    if row_col not in df.columns or col_col not in df.columns:
        raise ValueError("カラムが見つかりません")

    # 作業用データフレーム作成（必要なカラムのみ）
    work_df = df[[row_col, col_col]].copy()

    # 欠損値と非文字列を除外
    work_df = work_df.dropna(subset=[col_col])
    work_df = work_df[work_df[col_col].apply(lambda x: isinstance(x, str))]

    if len(work_df) == 0:
        return pd.DataFrame()

    # explode()で複数選択を展開（ベクトル化処理でiterrows()より高速）
    work_df[col_col] = work_df[col_col].str.split(delimiter)
    expanded_df = work_df.explode(col_col)

    # 空白を除去し、空文字を除外
    expanded_df[col_col] = expanded_df[col_col].str.strip()
    expanded_df = expanded_df[expanded_df[col_col] != '']

    if len(expanded_df) == 0:
        return pd.DataFrame()

    return pd.crosstab(expanded_df[row_col], expanded_df[col_col])


def analyze_crosstabs_by_tier(
    df: pd.DataFrame,
    config: SurveyConfig,
    tier: str = 'tier1'
) -> Dict[str, pd.DataFrame]:
    """
    Tier定義に基づいてクロス集計を実行

    Args:
        df: データフレーム
        config: SurveyConfig（crosstab_tiers プロパティ必須）
        tier: Tier名（'tier1', 'tier2', 等）

    Returns:
        dict: クロス集計結果のマッピング
    """
    results = {}

    tier_pairs = config.crosstab_tiers.get(tier, [])

    for row_var, col_var in tier_pairs:
        key = f"{row_var}_x_{col_var}"
        try:
            ct = create_crosstab_with_totals(df, row_var, col_var, config)
            results[key] = ct
        except Exception as e:
            warnings.warn(
                f"{key} のクロス集計に失敗: {e}",
                UserWarning,
                stacklevel=2
            )

    return results


def get_crosstab_summary(
    ct: pd.DataFrame,
    row_var: str,
    col_var: str
) -> Dict[str, Any]:
    """
    クロス集計表のサマリーを取得

    Args:
        ct: クロス集計表
        row_var: 行変数名
        col_var: 列変数名

    Returns:
        dict: サマリー情報
    """
    # 合計行/列を除外
    ct_clean = ct.copy()
    if '合計' in ct_clean.index:
        ct_clean = ct_clean.drop('合計')
    if '合計' in ct_clean.columns:
        ct_clean = ct_clean.drop('合計', axis=1)

    total_n = ct_clean.values.sum()

    # 最頻セル
    max_idx = ct_clean.values.argmax()
    max_row_idx, max_col_idx = divmod(max_idx, ct_clean.shape[1])
    max_row = ct_clean.index[max_row_idx]
    max_col = ct_clean.columns[max_col_idx]
    max_count = ct_clean.iloc[max_row_idx, max_col_idx]

    return {
        'row_var': row_var,
        'col_var': col_var,
        'n_rows': ct_clean.shape[0],
        'n_cols': ct_clean.shape[1],
        'total_n': int(total_n),
        'max_cell': {
            'row': max_row,
            'col': max_col,
            'count': int(max_count),
            'percentage': float(max_count / total_n * 100) if total_n > 0 else 0
        }
    }


def filter_crosstab_by_category(
    ct: pd.DataFrame,
    row_categories: Optional[List[str]] = None,
    col_categories: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    クロス集計表を特定のカテゴリでフィルタ

    Args:
        ct: クロス集計表
        row_categories: 残す行カテゴリ
        col_categories: 残す列カテゴリ

    Returns:
        pd.DataFrame: フィルタ済みクロス集計表
    """
    result = ct.copy()

    if row_categories:
        valid_rows = [r for r in row_categories if r in result.index]
        result = result.loc[valid_rows]

    if col_categories:
        valid_cols = [c for c in col_categories if c in result.columns]
        result = result[valid_cols]

    return result


def calculate_row_percentages(ct: pd.DataFrame) -> pd.DataFrame:
    """
    行ごとのパーセンテージを計算

    Args:
        ct: クロス集計表

    Returns:
        pd.DataFrame: パーセンテージ表
    """
    # 合計列を除外して計算
    ct_clean = ct.copy()
    if '合計' in ct_clean.columns:
        ct_clean = ct_clean.drop('合計', axis=1)

    row_sums = ct_clean.sum(axis=1)
    pct = ct_clean.div(row_sums, axis=0) * 100

    return pct.round(1)


def calculate_column_percentages(ct: pd.DataFrame) -> pd.DataFrame:
    """
    列ごとのパーセンテージを計算

    Args:
        ct: クロス集計表

    Returns:
        pd.DataFrame: パーセンテージ表
    """
    # 合計行を除外して計算
    ct_clean = ct.copy()
    if '合計' in ct_clean.index:
        ct_clean = ct_clean.drop('合計')

    col_sums = ct_clean.sum(axis=0)
    pct = ct_clean.div(col_sums, axis=1) * 100

    return pct.round(1)


def export_crosstabs_to_csv(
    crosstabs: Dict[str, pd.DataFrame],
    output_dir: str,
    prefix: str = 'cross'
) -> List[str]:
    """
    クロス集計結果をCSVファイルに出力

    Args:
        crosstabs: クロス集計結果のdict
        output_dir: 出力ディレクトリ
        prefix: ファイル名プレフィックス

    Returns:
        list: 出力したファイルパスのリスト
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for name, ct in crosstabs.items():
        filename = f"{prefix}_{name}.csv"
        filepath = output_path / filename
        ct.to_csv(filepath, encoding='utf-8-sig')
        saved_files.append(str(filepath))
        warnings.warn(f"保存完了: {filename}", UserWarning, stacklevel=2)

    return saved_files
