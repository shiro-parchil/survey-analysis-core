"""
レポート生成インターフェース

使用方法:
    from survey_analysis.base.report import ReportGenerator

    class MyReportGenerator(ReportGenerator):
        def generate_summary(self, results: dict) -> str:
            # プロジェクト固有のサマリー生成ロジック
            pass
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


class ReportGenerator(ABC):
    """
    レポート生成の抽象基底クラス

    各プロジェクトでこのクラスを継承し、
    プロジェクト固有のレポート形式を実装する。
    """

    def __init__(self, config: 'SurveyConfig'):
        """
        Args:
            config: SurveyConfig の具象クラスインスタンス
        """
        self.config = config

    @abstractmethod
    def generate_summary(self, results: Dict[str, Any]) -> str:
        """
        分析結果のサマリーを生成

        Args:
            results: 分析結果の辞書

        Returns:
            str: サマリーテキスト（Markdown形式推奨）
        """
        pass

    @abstractmethod
    def generate_insights(self, df: pd.DataFrame, tests: Dict[str, Any]) -> str:
        """
        ビジネスインサイトを生成

        Args:
            df: 分析対象のDataFrame
            tests: 統計検定の結果

        Returns:
            str: インサイトテキスト
        """
        pass

    def save_report(self, content: str, filename: str, subdir: str = 'reports') -> Path:
        """
        レポートをファイルに保存

        Args:
            content: レポート内容
            filename: ファイル名
            subdir: 出力サブディレクトリ

        Returns:
            Path: 保存先パス
        """
        output_path = self.config.output_dir / subdir
        output_path.mkdir(parents=True, exist_ok=True)

        file_path = output_path / filename
        file_path.write_text(content, encoding='utf-8')

        return file_path

    def format_statistical_result(
        self,
        test_name: str,
        p_value: float,
        effect_size: Optional[float] = None,
        effect_size_name: str = "effect size"
    ) -> str:
        """
        統計検定結果をフォーマット

        Args:
            test_name: 検定名
            p_value: p値
            effect_size: 効果量（オプション）
            effect_size_name: 効果量の名前

        Returns:
            str: フォーマットされた結果文字列
        """
        significance = self._get_significance_stars(p_value)

        result = f"**{test_name}**: p = {p_value:.4f} {significance}"

        if effect_size is not None:
            result += f", {effect_size_name} = {effect_size:.3f}"

        return result

    def _get_significance_stars(self, p_value: float) -> str:
        """p値から有意水準の星を返す"""
        if p_value < 0.001:
            return "***"
        elif p_value < 0.01:
            return "**"
        elif p_value < self.config.alpha:
            return "*"
        else:
            return "ns"

    def format_crosstab_summary(
        self,
        row_var: str,
        col_var: str,
        chi2: float,
        p_value: float,
        cramers_v: float
    ) -> str:
        """
        クロス集計結果のサマリーをフォーマット

        Args:
            row_var: 行変数名
            col_var: 列変数名
            chi2: カイ二乗統計量
            p_value: p値
            cramers_v: Cramer's V

        Returns:
            str: フォーマットされたサマリー
        """
        significance = self._get_significance_stars(p_value)

        interpretation = self._interpret_cramers_v(cramers_v)

        return (
            f"### {row_var} × {col_var}\n\n"
            f"- χ² = {chi2:.2f}, p = {p_value:.4f} {significance}\n"
            f"- Cramer's V = {cramers_v:.3f} ({interpretation})\n"
        )

    def _interpret_cramers_v(self, v: float) -> str:
        """Cramer's Vの解釈"""
        if v < 0.1:
            return "効果なし"
        elif v < 0.3:
            return "弱い関連"
        elif v < 0.5:
            return "中程度の関連"
        else:
            return "強い関連"
