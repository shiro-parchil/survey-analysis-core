"""
可視化モジュール

グラフ、ヒートマップ、チャートの生成を提供。
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import warnings

import pandas as pd
import numpy as np

from survey_analysis.base.config import SurveyConfig

warnings.filterwarnings('ignore')

# Matplotlib設定（インポート前に環境変数設定）
_CACHE_DIR: Optional[Path] = None
_MPLCONFIG_DIR: Optional[Path] = None


def _setup_matplotlib_env(cache_dir: Optional[Path] = None):
    """Matplotlib環境を設定"""
    global _CACHE_DIR, _MPLCONFIG_DIR

    if cache_dir:
        _CACHE_DIR = cache_dir / ".cache"
        _MPLCONFIG_DIR = cache_dir / ".mplconfig"
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _MPLCONFIG_DIR.mkdir(parents=True, exist_ok=True)
        os.environ["XDG_CACHE_HOME"] = str(_CACHE_DIR)
        os.environ["MPLCONFIGDIR"] = str(_MPLCONFIG_DIR)


# デフォルトインポート
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

# 日本語フォント対応
_JAPANESE_FONT_FAMILY: Optional[str] = None
try:
    import japanize_matplotlib
    _JAPANESE_FONT_FAMILY = plt.rcParams.get('font.family')
except ImportError:
    # フォールバック
    _JAPANESE_FONT_FAMILY = 'Hiragino Sans'  # macOS
    plt.rcParams['font.family'] = _JAPANESE_FONT_FAMILY


def setup_plot_style(config: Optional[SurveyConfig] = None):
    """
    プロットスタイルを設定

    Args:
        config: SurveyConfig（figure_settings プロパティ使用）
    """
    settings = config.figure_settings if config else {}

    style = settings.get('style', 'whitegrid')
    sns.set_style(style)

    if _JAPANESE_FONT_FAMILY:
        plt.rcParams['font.family'] = _JAPANESE_FONT_FAMILY

    figsize = settings.get('figsize', (12, 8))
    plt.rcParams['figure.figsize'] = figsize

    font_size = settings.get('font_size', 12)
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.titlesize'] = font_size + 4
    plt.rcParams['axes.labelsize'] = font_size
    plt.rcParams['xtick.labelsize'] = font_size - 2
    plt.rcParams['ytick.labelsize'] = font_size - 2


def plot_crosstab_heatmap(
    crosstab: pd.DataFrame,
    title: str,
    save_path: Optional[Path] = None,
    cmap: str = 'YlOrRd',
    config: Optional[SurveyConfig] = None,
    figsize: tuple = (12, 8)
) -> plt.Figure:
    """
    クロス集計表のヒートマップを作成

    Args:
        crosstab: クロス集計表
        title: タイトル
        save_path: 保存パス
        cmap: カラーマップ
        config: SurveyConfig
        figsize: 図のサイズ

    Returns:
        plt.Figure: 生成された図
    """
    setup_plot_style(config)

    # 合計行/列を除去
    ct_vis = crosstab.copy()
    for label in ['Total', '合計']:
        if label in ct_vis.index:
            ct_vis = ct_vis.drop(label)
        if label in ct_vis.columns:
            ct_vis = ct_vis.drop(label, axis=1)

    # 空の行/列を除去
    ct_vis = ct_vis.loc[ct_vis.sum(axis=1) > 0]
    ct_vis = ct_vis.loc[:, ct_vis.sum(axis=0) > 0]

    fig, ax = plt.subplots(figsize=figsize)

    sns.heatmap(
        ct_vis,
        annot=True,
        fmt='g',
        cmap=cmap,
        cbar_kws={'label': '回答数'},
        ax=ax
    )

    ax.set_title(title, fontsize=14, pad=20)
    plt.tight_layout()

    if save_path:
        dpi = config.figure_settings.get('dpi', 150) if config else 150
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"  ✓ ヒートマップ保存: {save_path.name}")

    return fig


def plot_bar_chart(
    data: pd.Series,
    title: str,
    xlabel: str = None,
    ylabel: str = '回答数',
    save_path: Optional[Path] = None,
    horizontal: bool = False,
    config: Optional[SurveyConfig] = None,
    figsize: tuple = (10, 6),
    color_palette: str = 'Set2'
) -> plt.Figure:
    """
    棒グラフを作成

    Args:
        data: データ（Series）
        title: タイトル
        xlabel: X軸ラベル
        ylabel: Y軸ラベル
        save_path: 保存パス
        horizontal: 横棒グラフにするか
        config: SurveyConfig
        figsize: 図のサイズ
        color_palette: カラーパレット

    Returns:
        plt.Figure: 生成された図
    """
    setup_plot_style(config)

    fig, ax = plt.subplots(figsize=figsize)
    colors = sns.color_palette(color_palette, len(data))

    if horizontal:
        data.plot(kind='barh', ax=ax, color=colors)
        ax.set_xlabel(ylabel)
        if xlabel:
            ax.set_ylabel(xlabel)

        # 値ラベル
        for patch in ax.patches:
            value = patch.get_width()
            if value > 0:
                ax.text(
                    patch.get_x() + value + max(data.max() * 0.01, 0.5),
                    patch.get_y() + patch.get_height() / 2,
                    f"{int(value)}",
                    va='center',
                    ha='left',
                    fontsize=10
                )
    else:
        data.plot(kind='bar', ax=ax, color=colors)
        if xlabel:
            ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')

        # 値ラベル
        for patch in ax.patches:
            value = patch.get_height()
            if value > 0:
                ax.text(
                    patch.get_x() + patch.get_width() / 2,
                    value + max(data.max() * 0.01, 0.5),
                    f"{int(value)}",
                    va='bottom',
                    ha='center',
                    fontsize=10
                )

    ax.set_title(title, fontsize=14, pad=20)
    plt.tight_layout()

    if save_path:
        dpi = config.figure_settings.get('dpi', 150) if config else 150
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"  ✓ 棒グラフ保存: {save_path.name}")

    return fig


def plot_stacked_bar(
    crosstab: pd.DataFrame,
    title: str,
    xlabel: str = None,
    ylabel: str = '割合 (%)',
    save_path: Optional[Path] = None,
    config: Optional[SurveyConfig] = None,
    figsize: tuple = (12, 8),
    colormap: str = 'Set2'
) -> plt.Figure:
    """
    積み上げ棒グラフを作成

    Args:
        crosstab: クロス集計表
        title: タイトル
        xlabel: X軸ラベル
        ylabel: Y軸ラベル
        save_path: 保存パス
        config: SurveyConfig
        figsize: 図のサイズ
        colormap: カラーマップ

    Returns:
        plt.Figure: 生成された図
    """
    setup_plot_style(config)

    # 合計行/列を除去
    ct_vis = crosstab.copy()
    for label in ['Total', '合計']:
        if label in ct_vis.index:
            ct_vis = ct_vis.drop(label)
        if label in ct_vis.columns:
            ct_vis = ct_vis.drop(label, axis=1)

    # 空の行を除去
    ct_vis = ct_vis.loc[ct_vis.sum(axis=1) > 0]

    # パーセンテージ計算
    ct_pct = ct_vis.div(ct_vis.sum(axis=1), axis=0) * 100
    ct_pct = ct_pct.fillna(0)

    fig, ax = plt.subplots(figsize=figsize)

    ct_pct.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        colormap=colormap
    )

    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, pad=20)
    ax.legend(title='', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45, ha='right')

    # セグメント内のパーセンテージ表示
    for container in ax.containers:
        for patch in container:
            height = patch.get_height()
            if height >= 8:  # 8%以上のみ表示
                ax.text(
                    patch.get_x() + patch.get_width() / 2,
                    patch.get_y() + height / 2,
                    f"{height:.0f}%",
                    ha='center',
                    va='center',
                    fontsize=10,
                    color='black'
                )

    # 各棒の回答者数を表示
    totals = ct_vis.sum(axis=1).astype(int)
    ax.set_ylim(0, 110)
    for i, total in enumerate(totals.values):
        ax.text(i, 101, f"N={total}", ha='center', va='bottom', fontsize=10)

    plt.tight_layout()

    if save_path:
        dpi = config.figure_settings.get('dpi', 150) if config else 150
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"  ✓ 積み上げ棒グラフ保存: {save_path.name}")

    return fig


def plot_pie_chart(
    data: pd.Series,
    title: str,
    save_path: Optional[Path] = None,
    config: Optional[SurveyConfig] = None,
    figsize: tuple = (8, 8),
    color_palette: str = 'Set2'
) -> plt.Figure:
    """
    円グラフを作成

    Args:
        data: データ（Series）
        title: タイトル
        save_path: 保存パス
        config: SurveyConfig
        figsize: 図のサイズ
        color_palette: カラーパレット

    Returns:
        plt.Figure: 生成された図
    """
    setup_plot_style(config)

    fig, ax = plt.subplots(figsize=figsize)

    # 小さすぎるスライスをまとめる
    threshold = data.sum() * 0.01
    data_filtered = data[data > threshold]
    other_sum = data[data <= threshold].sum()
    if other_sum > 0:
        data_filtered['その他'] = other_sum

    colors = sns.color_palette(color_palette, len(data_filtered))

    ax.pie(
        data_filtered,
        labels=data_filtered.index,
        autopct='%1.1f%%',
        startangle=90,
        colors=colors
    )

    ax.set_title(title, fontsize=14, pad=20)
    plt.tight_layout()

    if save_path:
        dpi = config.figure_settings.get('dpi', 150) if config else 150
        fig.savefig(save_path, dpi=dpi, bbox_inches='tight')
        print(f"  ✓ 円グラフ保存: {save_path.name}")

    return fig


def plot_distribution(
    df: pd.DataFrame,
    column: str,
    title: str,
    save_path: Optional[Path] = None,
    config: Optional[SurveyConfig] = None,
    order: Optional[List[str]] = None,
    figsize: tuple = (10, 6)
) -> plt.Figure:
    """
    分布グラフを作成

    Args:
        df: データフレーム
        column: 対象カラム
        title: タイトル
        save_path: 保存パス
        config: SurveyConfig
        order: カテゴリの順序
        figsize: 図のサイズ

    Returns:
        plt.Figure: 生成された図
    """
    counts = df[column].value_counts()

    if order:
        counts = counts.reindex(order).fillna(0).astype(int)

    counts = counts[counts > 0]

    return plot_bar_chart(
        counts,
        title=title,
        xlabel=column,
        ylabel='回答数',
        save_path=save_path,
        config=config,
        figsize=figsize
    )


def create_visualization_report(
    df: pd.DataFrame,
    config: SurveyConfig,
    output_dir: Path,
    visualizations: Optional[List[Dict[str, Any]]] = None
) -> List[Path]:
    """
    複数の可視化を一括生成

    Args:
        df: データフレーム
        config: SurveyConfig
        output_dir: 出力ディレクトリ
        visualizations: 可視化定義リスト

    Returns:
        List[Path]: 生成したファイルパスのリスト

    Example:
        visualizations = [
            {'type': 'bar', 'column': 'age', 'title': '年齢分布'},
            {'type': 'pie', 'column': 'gender', 'title': '性別分布'},
        ]
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    if not visualizations:
        print("可視化定義がありません")
        return saved_files

    print("\n" + "=" * 60)
    print("可視化レポート生成")
    print("=" * 60)

    for i, viz in enumerate(visualizations, 1):
        viz_type = viz.get('type', 'bar')
        column = viz.get('column')
        title = viz.get('title', f'図{i}')

        # カラム名解決
        if config and column in config.questions:
            col_name = config.get_column_name(column)
        else:
            col_name = column

        if col_name not in df.columns:
            print(f"  警告: カラム '{col_name}' が見つかりません")
            continue

        filename = f"{i:02d}_{column or 'chart'}.png"
        save_path = output_dir / filename

        try:
            if viz_type == 'bar':
                data = df[col_name].value_counts()
                order = viz.get('order')
                if order:
                    data = data.reindex(order).fillna(0).astype(int)
                plot_bar_chart(data, title, save_path=save_path, config=config)

            elif viz_type == 'pie':
                data = df[col_name].value_counts()
                plot_pie_chart(data, title, save_path=save_path, config=config)

            elif viz_type == 'heatmap':
                col_var = viz.get('col_var')
                if col_var:
                    col_var_name = config.get_column_name(col_var) if config else col_var
                    ct = pd.crosstab(df[col_name], df[col_var_name])
                    plot_crosstab_heatmap(ct, title, save_path=save_path, config=config)

            saved_files.append(save_path)
            plt.close()

        except Exception as e:
            print(f"  エラー: {title} の生成に失敗 - {e}")

    print(f"\n生成完了: {len(saved_files)} ファイル")
    print("=" * 60)

    return saved_files
