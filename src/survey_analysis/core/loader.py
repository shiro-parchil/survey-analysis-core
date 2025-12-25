"""
データローダーモジュール

CSVデータの読み込み、クリーニング、前処理を提供。
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import warnings

import pandas as pd
import numpy as np
import chardet

from survey_analysis.base.config import SurveyConfig

warnings.filterwarnings('ignore')


def detect_encoding(file_path: Path, sample_size: int = 10000) -> str:
    """
    ファイルのエンコーディングを自動検出

    Args:
        file_path: ファイルパス
        sample_size: 検出に使用するバイト数

    Returns:
        str: 検出されたエンコーディング名
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    encoding = result['encoding']

    # BOM付きUTF-8の処理
    if encoding and encoding.lower() in ['utf-8', 'ascii']:
        if raw_data.startswith(b'\xef\xbb\xbf'):
            encoding = 'utf-8-sig'

    return encoding or 'utf-8'


def load_raw_data(config: SurveyConfig) -> pd.DataFrame:
    """
    生CSVデータを読み込み

    Args:
        config: SurveyConfig の具象クラスインスタンス

    Returns:
        pd.DataFrame: 読み込んだデータフレーム
    """
    file_path = config.raw_data_path

    if not file_path.exists():
        raise FileNotFoundError(f"データファイルが見つかりません: {file_path}")

    # エンコーディング検出
    encoding = config.encoding
    if encoding == 'auto':
        encoding = detect_encoding(file_path)

    df = pd.read_csv(file_path, encoding=encoding)
    print(f"データ読み込み完了: {len(df)} 行 × {len(df.columns)} 列")

    return df


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    カラム名をクリーニング

    Args:
        df: データフレーム

    Returns:
        pd.DataFrame: クリーニング済みデータフレーム
    """
    df = df.copy()
    # 前後の空白を削除
    df.columns = df.columns.str.strip()
    return df


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = 'keep',
    fill_value: Any = None
) -> pd.DataFrame:
    """
    欠損値を処理

    Args:
        df: データフレーム
        strategy: 処理戦略（'keep', 'drop', 'fill'）
        fill_value: 'fill'戦略時の埋め値

    Returns:
        pd.DataFrame: 処理済みデータフレーム
    """
    df = df.copy()

    if strategy == 'drop':
        df = df.dropna()
    elif strategy == 'fill':
        df = df.fillna(fill_value if fill_value is not None else '')
    # 'keep' の場合はそのまま

    return df


def split_multiselect_cell(cell_value: str, delimiter: str = '、') -> List[str]:
    """
    複数選択セルを分割

    Args:
        cell_value: セルの値
        delimiter: 区切り文字

    Returns:
        list: 分割された値のリスト
    """
    if pd.isna(cell_value) or not isinstance(cell_value, str):
        return []
    return [v.strip() for v in cell_value.split(delimiter) if v.strip()]


def convert_ordered_categories(
    df: pd.DataFrame,
    config: SurveyConfig
) -> pd.DataFrame:
    """
    順序付きカテゴリカル変数に変換

    Args:
        df: データフレーム
        config: SurveyConfig インスタンス

    Returns:
        pd.DataFrame: 変換済みデータフレーム
    """
    df = df.copy()

    for col_key, order in config.category_orders.items():
        # 質問IDからカラム名を取得
        col_name = config.get_column_name(col_key)
        if col_name not in df.columns:
            continue

        # 既存の値をチェック
        existing_values = df[col_name].dropna().unique()

        # 順序に含まれない値があれば警告
        missing_from_order = set(existing_values) - set(order)
        if missing_from_order:
            print(f"警告: '{col_name}' に順序定義にない値があります: {missing_from_order}")

        # カテゴリカル型に変換
        df[col_name] = pd.Categorical(
            df[col_name],
            categories=order,
            ordered=True
        )

    return df


def create_numeric_scores(
    df: pd.DataFrame,
    column: str,
    score_mapping: Dict[str, int]
) -> pd.Series:
    """
    カテゴリカル値を数値スコアに変換

    Args:
        df: データフレーム
        column: 対象カラム名
        score_mapping: 値→スコアのマッピング

    Returns:
        pd.Series: 数値スコアのシリーズ
    """
    return df[column].map(score_mapping)


def add_derived_columns(
    df: pd.DataFrame,
    config: SurveyConfig,
    derivations: Optional[Dict[str, callable]] = None
) -> pd.DataFrame:
    """
    派生カラムを追加

    Args:
        df: データフレーム
        config: SurveyConfig インスタンス
        derivations: カラム名→生成関数のマッピング

    Returns:
        pd.DataFrame: 派生カラム追加済みデータフレーム
    """
    df = df.copy()

    if derivations:
        for col_name, func in derivations.items():
            try:
                df[col_name] = func(df, config)
            except Exception as e:
                print(f"警告: 派生カラム '{col_name}' の生成に失敗: {e}")

    return df


def load_and_prepare_data(
    config: SurveyConfig,
    missing_strategy: str = 'keep',
    derivations: Optional[Dict[str, callable]] = None
) -> pd.DataFrame:
    """
    データを読み込み、前処理を実行

    Args:
        config: SurveyConfig の具象クラスインスタンス
        missing_strategy: 欠損値処理戦略
        derivations: 派生カラム生成関数のマッピング

    Returns:
        pd.DataFrame: 前処理済みデータフレーム
    """
    print("=" * 60)
    print("データの読み込みと前処理")
    print("=" * 60)

    # 1. 生データ読み込み
    df = load_raw_data(config)

    # 2. カラム名クリーニング
    df = clean_column_names(df)

    # 3. 欠損値処理
    df = handle_missing_values(df, strategy=missing_strategy)

    # 4. 順序付きカテゴリカル変数に変換
    if config.category_orders:
        df = convert_ordered_categories(df, config)

    # 5. 派生カラム追加
    if derivations:
        df = add_derived_columns(df, config, derivations)

    print(f"\n前処理完了: {len(df)} 行 × {len(df.columns)} 列")
    print("=" * 60)

    return df


def validate_data(df: pd.DataFrame, config: SurveyConfig) -> Dict[str, Any]:
    """
    データの妥当性を検証

    Args:
        df: データフレーム
        config: SurveyConfig インスタンス

    Returns:
        dict: 検証結果
    """
    results = {
        'row_count': len(df),
        'column_count': len(df.columns),
        'missing_columns': [],
        'extra_columns': [],
        'missing_values': {},
        'is_valid': True,
        'errors': []
    }

    # 必要なカラムの存在チェック
    expected_columns = set(config.questions.values())
    actual_columns = set(df.columns)

    results['missing_columns'] = list(expected_columns - actual_columns)
    results['extra_columns'] = list(actual_columns - expected_columns)

    if results['missing_columns']:
        results['is_valid'] = False
        results['errors'].append(
            f"必要なカラムがありません: {results['missing_columns']}"
        )

    # 欠損値チェック
    for col in df.columns:
        missing_count = df[col].isna().sum()
        if missing_count > 0:
            results['missing_values'][col] = {
                'count': int(missing_count),
                'percentage': float(missing_count / len(df) * 100)
            }

    return results
