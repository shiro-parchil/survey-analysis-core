"""
pytest共通フィクスチャ

survey-analysis-coreパッケージのテスト用フィクスチャ定義。
"""

import pytest
import pandas as pd
from pathlib import Path
from typing import Dict, List


# =============================================================================
# テスト用の具象ConfigクラスをMockとして作成
# =============================================================================

from survey_analysis.base.config import SurveyConfig


class MockSurveyConfig(SurveyConfig):
    """テスト用のモック設定クラス"""

    def __init__(
        self,
        questions: Dict[str, str] = None,
        raw_data_path: Path = None,
        output_dir: Path = None,
        category_orders: Dict[str, List[str]] = None,
        alpha: float = 0.05
    ):
        self._questions = questions or {
            'age': '年齢',
            'gender': '性別',
            'satisfaction': '満足度',
            'interest': '興味度',
        }
        self._raw_data_path = raw_data_path or Path('/tmp/test_survey.csv')
        self._output_dir = output_dir or Path('/tmp/test_output')
        self._category_orders = category_orders or {}
        self._alpha = alpha

    @property
    def questions(self) -> Dict[str, str]:
        return self._questions

    @property
    def raw_data_path(self) -> Path:
        return self._raw_data_path

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    @property
    def category_orders(self) -> Dict[str, List[str]]:
        return self._category_orders

    @property
    def alpha(self) -> float:
        return self._alpha


# =============================================================================
# フィクスチャ定義
# =============================================================================

@pytest.fixture
def mock_config():
    """基本的なモック設定"""
    return MockSurveyConfig()


@pytest.fixture
def sample_dataframe():
    """テスト用サンプルデータフレーム"""
    return pd.DataFrame({
        '年齢': ['20代', '30代', '20代', '40代', '30代', '20代', '30代', '40代', '20代', '30代'],
        '性別': ['男性', '女性', '男性', '女性', '男性', '女性', '男性', '女性', '男性', '女性'],
        '満足度': ['満足', '普通', '不満', '満足', '満足', '普通', '不満', '満足', '普通', '満足'],
        '興味度': ['高', '中', '低', '高', '中', '高', '低', '中', '高', '高'],
        '数値スコア': [5, 3, 1, 5, 4, 3, 2, 5, 3, 4],
    })


@pytest.fixture
def sample_dataframe_with_missing():
    """欠損値を含むサンプルデータフレーム"""
    return pd.DataFrame({
        '年齢': ['20代', '30代', None, '40代', '30代'],
        '性別': ['男性', None, '男性', '女性', '男性'],
        '満足度': ['満足', '普通', '不満', None, '満足'],
    })


@pytest.fixture
def crosstab_sample():
    """クロス集計テスト用データ"""
    return pd.DataFrame({
        '年齢': ['20代'] * 5 + ['30代'] * 5 + ['40代'] * 5,
        '興味度': ['高', '高', '中', '中', '低'] * 3,
    })


@pytest.fixture
def freetext_sample():
    """自由記述テスト用データ"""
    return pd.DataFrame({
        'コメント': [
            'とても良いサービスだと思います。使いやすいです。',
            'もう少し機能が欲しい。価格は適切。',
            '使い方がわからなかった。',
            None,
            'サポートが丁寧で助かりました。',
        ]
    })


@pytest.fixture
def config_with_categories(tmp_path):
    """カテゴリ順序付き設定"""
    return MockSurveyConfig(
        category_orders={
            'age': ['20代', '30代', '40代', '50代以上'],
            'satisfaction': ['非常に不満', '不満', '普通', '満足', '非常に満足'],
        },
        output_dir=tmp_path / 'output'
    )


@pytest.fixture
def tmp_csv_file(tmp_path):
    """一時CSVファイルを作成"""
    csv_path = tmp_path / 'test_data.csv'
    df = pd.DataFrame({
        '年齢': ['20代', '30代', '40代'],
        '性別': ['男性', '女性', '男性'],
        '満足度': ['満足', '普通', '不満'],
    })
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    return csv_path


@pytest.fixture
def config_with_csv(tmp_csv_file, tmp_path):
    """CSVファイル付き設定"""
    return MockSurveyConfig(
        questions={
            'age': '年齢',
            'gender': '性別',
            'satisfaction': '満足度',
        },
        raw_data_path=tmp_csv_file,
        output_dir=tmp_path / 'output'
    )
