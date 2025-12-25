"""
データ監査モジュール

データ品質チェック、監査レポート生成を提供。
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import pandas as pd
import numpy as np

from survey_analysis.base.config import SurveyConfig


def check_data_completeness(
    df: pd.DataFrame,
    config: SurveyConfig
) -> Dict[str, Any]:
    """
    データの完全性をチェック

    Args:
        df: データフレーム
        config: SurveyConfig

    Returns:
        dict: 完全性チェック結果
    """
    results = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'expected_columns': len(config.questions),
        'missing_columns': [],
        'extra_columns': [],
        'column_completeness': {}
    }

    # 期待カラムとの比較
    expected = set(config.questions.values())
    actual = set(df.columns)

    results['missing_columns'] = list(expected - actual)
    results['extra_columns'] = list(actual - expected)

    # カラムごとの完全性
    for col in df.columns:
        non_null = df[col].notna().sum()
        results['column_completeness'][col] = {
            'non_null_count': int(non_null),
            'null_count': int(len(df) - non_null),
            'completeness_rate': float(non_null / len(df) * 100)
        }

    return results


def check_data_validity(
    df: pd.DataFrame,
    config: SurveyConfig
) -> Dict[str, Any]:
    """
    データの妥当性をチェック

    Args:
        df: データフレーム
        config: SurveyConfig

    Returns:
        dict: 妥当性チェック結果
    """
    results = {
        'category_validity': {},
        'invalid_values': {}
    }

    # カテゴリ変数の妥当性チェック
    for q_id, order in config.category_orders.items():
        col_name = config.get_column_name(q_id)
        if col_name not in df.columns:
            continue

        valid_values = set(order)
        actual_values = set(df[col_name].dropna().unique())
        invalid = actual_values - valid_values

        results['category_validity'][q_id] = {
            'column': col_name,
            'expected_values': list(valid_values),
            'invalid_values': list(invalid),
            'is_valid': len(invalid) == 0
        }

        if invalid:
            results['invalid_values'][q_id] = list(invalid)

    return results


def check_data_consistency(df: pd.DataFrame) -> Dict[str, Any]:
    """
    データの一貫性をチェック

    Args:
        df: データフレーム

    Returns:
        dict: 一貫性チェック結果
    """
    results = {
        'duplicate_rows': 0,
        'duplicate_indices': [],
        'constant_columns': [],
        'high_cardinality_columns': []
    }

    # 重複行チェック
    duplicates = df.duplicated()
    results['duplicate_rows'] = int(duplicates.sum())
    results['duplicate_indices'] = df[duplicates].index.tolist()

    # 定数カラム（1値のみ）チェック
    for col in df.columns:
        unique_count = df[col].nunique(dropna=True)
        if unique_count <= 1:
            results['constant_columns'].append(col)
        elif unique_count > len(df) * 0.9:  # 90%以上がユニーク
            results['high_cardinality_columns'].append({
                'column': col,
                'unique_count': int(unique_count),
                'percentage': float(unique_count / len(df) * 100)
            })

    return results


def generate_audit_report(
    df: pd.DataFrame,
    config: SurveyConfig,
    output_path: Optional[Path] = None
) -> str:
    """
    データ監査レポートを生成

    Args:
        df: データフレーム
        config: SurveyConfig
        output_path: 出力パス（省略時はテキストのみ返す）

    Returns:
        str: 監査レポート（Markdown形式）
    """
    # 各チェックを実行
    completeness = check_data_completeness(df, config)
    validity = check_data_validity(df, config)
    consistency = check_data_consistency(df)

    # レポート生成
    report = []
    report.append("# データ監査レポート\n")
    report.append(f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # 概要
    report.append("\n## 1. 概要\n")
    report.append(f"- 総行数: {completeness['total_rows']:,}")
    report.append(f"- 総カラム数: {completeness['total_columns']}")
    report.append(f"- 期待カラム数: {completeness['expected_columns']}")

    # 完全性
    report.append("\n## 2. 完全性チェック\n")

    if completeness['missing_columns']:
        report.append("\n### 欠損カラム（期待されるが存在しない）\n")
        for col in completeness['missing_columns']:
            report.append(f"- {col}")
    else:
        report.append("\n✅ 全ての期待カラムが存在します\n")

    # 欠損値サマリー
    report.append("\n### 欠損値サマリー\n")
    report.append("| カラム | 欠損数 | 欠損率 |")
    report.append("|--------|--------|--------|")

    sorted_cols = sorted(
        completeness['column_completeness'].items(),
        key=lambda x: x[1]['null_count'],
        reverse=True
    )

    for col, stats in sorted_cols[:20]:  # 上位20件
        if stats['null_count'] > 0:
            report.append(
                f"| {col[:40]}... | {stats['null_count']} | "
                f"{100 - stats['completeness_rate']:.1f}% |"
            )

    # 妥当性
    report.append("\n## 3. 妥当性チェック\n")

    invalid_count = sum(
        1 for v in validity['category_validity'].values()
        if not v['is_valid']
    )

    if invalid_count == 0:
        report.append("✅ 全てのカテゴリ値が妥当です\n")
    else:
        report.append(f"⚠️ {invalid_count} カラムに不正な値があります\n")
        for q_id, check in validity['category_validity'].items():
            if not check['is_valid']:
                report.append(f"\n### {q_id} ({check['column'][:30]}...)")
                report.append(f"- 不正な値: {check['invalid_values']}")

    # 一貫性
    report.append("\n## 4. 一貫性チェック\n")

    if consistency['duplicate_rows'] > 0:
        report.append(
            f"⚠️ 重複行: {consistency['duplicate_rows']} 件\n"
        )
    else:
        report.append("✅ 重複行はありません\n")

    if consistency['constant_columns']:
        report.append(f"\n⚠️ 定数カラム（1値のみ）: {len(consistency['constant_columns'])} 件")
        for col in consistency['constant_columns'][:10]:
            report.append(f"  - {col}")

    # サマリー
    report.append("\n## 5. サマリー\n")

    issues = []
    if completeness['missing_columns']:
        issues.append(f"欠損カラム: {len(completeness['missing_columns'])} 件")
    if invalid_count > 0:
        issues.append(f"不正値カラム: {invalid_count} 件")
    if consistency['duplicate_rows'] > 0:
        issues.append(f"重複行: {consistency['duplicate_rows']} 件")

    if issues:
        report.append("### 検出された問題\n")
        for issue in issues:
            report.append(f"- {issue}")
    else:
        report.append("✅ 重大な問題は検出されませんでした\n")

    report_text = '\n'.join(report)

    # ファイル出力
    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding='utf-8')
        print(f"監査レポート保存: {output_path}")

    return report_text


def get_data_profile(df: pd.DataFrame) -> pd.DataFrame:
    """
    データプロファイルを取得

    Args:
        df: データフレーム

    Returns:
        pd.DataFrame: プロファイル情報
    """
    profile = []

    for col in df.columns:
        series = df[col]

        row = {
            'column': col,
            'dtype': str(series.dtype),
            'non_null_count': int(series.notna().sum()),
            'null_count': int(series.isna().sum()),
            'null_percentage': float(series.isna().sum() / len(df) * 100),
            'unique_count': int(series.nunique()),
            'unique_percentage': float(series.nunique() / len(df) * 100),
        }

        # 数値型の場合
        if pd.api.types.is_numeric_dtype(series):
            row['mean'] = float(series.mean()) if series.notna().any() else None
            row['std'] = float(series.std()) if series.notna().any() else None
            row['min'] = float(series.min()) if series.notna().any() else None
            row['max'] = float(series.max()) if series.notna().any() else None

        # カテゴリカル型の場合
        else:
            value_counts = series.value_counts()
            row['top_value'] = value_counts.index[0] if len(value_counts) > 0 else None
            row['top_count'] = int(value_counts.iloc[0]) if len(value_counts) > 0 else 0

        profile.append(row)

    return pd.DataFrame(profile)


def export_audit_results(
    df: pd.DataFrame,
    config: SurveyConfig,
    output_dir: Path
) -> Dict[str, Path]:
    """
    監査結果をファイルに出力

    Args:
        df: データフレーム
        config: SurveyConfig
        output_dir: 出力ディレクトリ

    Returns:
        dict: 出力ファイルパスのマッピング
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {}

    # 監査レポート
    report_path = output_dir / 'audit_report.md'
    generate_audit_report(df, config, report_path)
    paths['report'] = report_path

    # データプロファイル
    profile = get_data_profile(df)
    profile_path = output_dir / 'data_profile.csv'
    profile.to_csv(profile_path, index=False, encoding='utf-8-sig')
    paths['profile'] = profile_path
    print(f"データプロファイル保存: {profile_path}")

    return paths
