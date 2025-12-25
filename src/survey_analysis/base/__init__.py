"""
survey_analysis.base - 抽象基底クラス

プロジェクト固有の設定とレポート生成を定義するための
抽象クラスを提供します。
"""

from .config import SurveyConfig
from .report import ReportGenerator

__all__ = ['SurveyConfig', 'ReportGenerator']
