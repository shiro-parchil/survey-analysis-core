"""
survey-analysis-core - 汎用アンケート解析コアライブラリ

プロジェクト固有の設定を `SurveyConfig` 抽象クラスで注入することで、
様々なアンケートプロジェクトで再利用可能な解析機能を提供。

使用例:
    from survey_analysis.base import SurveyConfig
    from survey_analysis.core import load_and_prepare_data, chi_square_test

    class MySurveyConfig(SurveyConfig):
        @property
        def questions(self) -> dict:
            return {'age': 'Q1. 年齢', ...}
        # ... 他の実装

    config = MySurveyConfig()
    df = load_and_prepare_data(config)
    result = chi_square_test(df, 'age', 'satisfaction', config)
"""

__version__ = '1.0.0'
__author__ = 'SHIRO Inc.'

from .base import SurveyConfig, ReportGenerator

__all__ = [
    'SurveyConfig',
    'ReportGenerator',
    '__version__',
]
