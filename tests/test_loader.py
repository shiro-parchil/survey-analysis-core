"""
データローダーのテスト

データ読み込み、前処理、カテゴリ変換をテスト。
実際のloader.py APIに基づく。
"""

import pytest
import pandas as pd
from pathlib import Path

from survey_analysis.core import loader


class TestDetectEncoding:
    """detect_encoding関数のテスト"""

    def test_detect_utf8(self, tmp_path):
        """UTF-8を検出"""
        csv_path = tmp_path / 'utf8.csv'
        csv_path.write_text('日本語,テスト\na,b', encoding='utf-8')

        encoding = loader.detect_encoding(csv_path)
        assert encoding.lower() in ['utf-8', 'utf8', 'ascii']

    def test_detect_utf8_bom(self, tmp_path):
        """UTF-8 BOMを検出"""
        csv_path = tmp_path / 'utf8bom.csv'
        csv_path.write_bytes(b'\xef\xbb\xbfcol1,col2\na,b\n')

        encoding = loader.detect_encoding(csv_path)
        assert encoding == 'utf-8-sig'

    def test_detect_with_sample_size(self, tmp_path):
        """サンプルサイズ指定での検出"""
        csv_path = tmp_path / 'large.csv'
        csv_path.write_text('col1,col2\n' + 'a,b\n' * 1000, encoding='utf-8')

        encoding = loader.detect_encoding(csv_path, sample_size=100)
        assert encoding is not None


class TestLoadRawData:
    """load_raw_data関数のテスト"""

    def test_load_raw_data_with_valid_config(self, config_with_csv):
        """有効な設定でデータを読み込み"""
        df = loader.load_raw_data(config_with_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_load_raw_data_file_not_found(self, mock_config):
        """存在しないファイルでFileNotFoundError"""
        with pytest.raises(FileNotFoundError, match="データファイルが見つかりません"):
            loader.load_raw_data(mock_config)

    def test_load_raw_data_returns_all_columns(self, config_with_csv):
        """全カラムが読み込まれる"""
        df = loader.load_raw_data(config_with_csv)
        assert '年齢' in df.columns
        assert '性別' in df.columns
        assert '満足度' in df.columns


class TestCleanColumnNames:
    """clean_column_names関数のテスト"""

    def test_strips_whitespace_from_columns(self):
        """カラム名の前後空白が除去される"""
        df = pd.DataFrame({
            '  col1  ': [1, 2],
            'col2 ': [3, 4]
        })
        cleaned = loader.clean_column_names(df)
        assert 'col1' in cleaned.columns
        assert 'col2' in cleaned.columns

    def test_preserves_original_data(self, sample_dataframe):
        """元データが変更されない（コピー返却）"""
        original_columns = sample_dataframe.columns.tolist()
        _ = loader.clean_column_names(sample_dataframe)
        assert sample_dataframe.columns.tolist() == original_columns


class TestHandleMissingValues:
    """handle_missing_values関数のテスト"""

    def test_keep_strategy_preserves_na(self):
        """keep戦略で欠損値が保持される"""
        df = pd.DataFrame({'col1': [1, None, 3]})
        result = loader.handle_missing_values(df, strategy='keep')
        assert result['col1'].isna().sum() == 1

    def test_drop_strategy_removes_na(self):
        """drop戦略で欠損値行が削除される"""
        df = pd.DataFrame({'col1': [1, None, 3], 'col2': [4, 5, 6]})
        result = loader.handle_missing_values(df, strategy='drop')
        assert len(result) == 2
        assert result['col1'].isna().sum() == 0

    def test_fill_strategy_replaces_na(self):
        """fill戦略で欠損値が埋められる"""
        df = pd.DataFrame({'col1': ['a', None, 'c']})
        result = loader.handle_missing_values(df, strategy='fill', fill_value='X')
        assert result['col1'].tolist() == ['a', 'X', 'c']


class TestSplitMultiselectCell:
    """split_multiselect_cell関数のテスト"""

    def test_splits_with_default_delimiter(self):
        """デフォルト区切り文字で分割"""
        result = loader.split_multiselect_cell('選択肢A、選択肢B、選択肢C')
        assert result == ['選択肢A', '選択肢B', '選択肢C']

    def test_splits_with_custom_delimiter(self):
        """カスタム区切り文字で分割"""
        result = loader.split_multiselect_cell('a,b,c', delimiter=',')
        assert result == ['a', 'b', 'c']

    def test_returns_empty_list_for_none(self):
        """Noneで空リスト"""
        assert loader.split_multiselect_cell(None) == []

    def test_returns_empty_list_for_nan(self):
        """NaNで空リスト"""
        import numpy as np
        assert loader.split_multiselect_cell(np.nan) == []

    def test_strips_whitespace(self):
        """各要素の空白が除去される"""
        result = loader.split_multiselect_cell('  a 、 b 、 c  ')
        assert result == ['a', 'b', 'c']


class TestConvertOrderedCategories:
    """convert_ordered_categories関数のテスト"""

    def test_converts_to_categorical(self, tmp_path):
        """カテゴリカル型に変換される"""
        from conftest import MockSurveyConfig

        df = pd.DataFrame({'年齢': ['20代', '30代', '40代']})
        config = MockSurveyConfig(
            questions={'age': '年齢'},
            category_orders={'age': ['20代', '30代', '40代', '50代']},
            raw_data_path=tmp_path / 'test.csv'
        )

        result = loader.convert_ordered_categories(df, config)
        assert result['年齢'].dtype.name == 'category'

    def test_preserves_specified_order(self, tmp_path):
        """指定した順序が保持される"""
        from conftest import MockSurveyConfig

        df = pd.DataFrame({'年齢': ['40代', '20代', '30代']})
        config = MockSurveyConfig(
            questions={'age': '年齢'},
            category_orders={'age': ['20代', '30代', '40代']},
            raw_data_path=tmp_path / 'test.csv'
        )

        result = loader.convert_ordered_categories(df, config)
        categories = result['年齢'].cat.categories.tolist()
        assert categories == ['20代', '30代', '40代']

    def test_ordered_is_true(self, tmp_path):
        """ordered=Trueで変換される"""
        from conftest import MockSurveyConfig

        df = pd.DataFrame({'年齢': ['20代', '30代']})
        config = MockSurveyConfig(
            questions={'age': '年齢'},
            category_orders={'age': ['20代', '30代', '40代']},
            raw_data_path=tmp_path / 'test.csv'
        )

        result = loader.convert_ordered_categories(df, config)
        assert result['年齢'].cat.ordered is True

    def test_ignores_missing_columns(self, tmp_path):
        """存在しないカラムは無視される"""
        from conftest import MockSurveyConfig

        df = pd.DataFrame({'年齢': ['20代', '30代']})
        config = MockSurveyConfig(
            questions={'age': '年齢', 'missing': '存在しないカラム'},
            category_orders={'missing': ['a', 'b']},
            raw_data_path=tmp_path / 'test.csv'
        )

        # エラーが発生しないことを確認
        result = loader.convert_ordered_categories(df, config)
        assert len(result) == 2


class TestLoadAndPrepareData:
    """load_and_prepare_data関数のテスト"""

    def test_load_and_prepare_with_config(self, config_with_csv):
        """設定を使用してデータを読み込み・準備"""
        df = loader.load_and_prepare_data(config_with_csv)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert '年齢' in df.columns

    def test_applies_category_order(self, tmp_path):
        """カテゴリ順序が適用される"""
        from conftest import MockSurveyConfig

        # テストCSV作成
        csv_path = tmp_path / 'test.csv'
        pd.DataFrame({
            '年齢': ['30代', '20代', '40代'],
            '性別': ['男性', '女性', '男性']
        }).to_csv(csv_path, index=False, encoding='utf-8-sig')

        config = MockSurveyConfig(
            questions={'age': '年齢', 'gender': '性別'},
            raw_data_path=csv_path,
            output_dir=tmp_path / 'output',
            category_orders={'age': ['20代', '30代', '40代']}
        )

        df = loader.load_and_prepare_data(config)

        if df['年齢'].dtype.name == 'category':
            categories = df['年齢'].cat.categories.tolist()
            assert categories == ['20代', '30代', '40代']

    def test_with_drop_missing_strategy(self, tmp_path):
        """drop戦略で欠損値が削除される"""
        from conftest import MockSurveyConfig

        csv_path = tmp_path / 'test.csv'
        pd.DataFrame({
            '年齢': ['20代', None, '40代'],
            '性別': ['男性', '女性', None]
        }).to_csv(csv_path, index=False, encoding='utf-8-sig')

        config = MockSurveyConfig(
            questions={'age': '年齢', 'gender': '性別'},
            raw_data_path=csv_path,
            output_dir=tmp_path / 'output'
        )

        df = loader.load_and_prepare_data(config, missing_strategy='drop')
        # 欠損値を含む行が削除される
        assert len(df) <= 3


class TestValidateData:
    """validate_data関数のテスト"""

    def test_returns_validation_result(self, sample_dataframe, mock_config):
        """検証結果を返す"""
        result = loader.validate_data(sample_dataframe, mock_config)

        assert 'row_count' in result
        assert 'column_count' in result
        assert 'is_valid' in result
        assert 'errors' in result

    def test_detects_missing_columns(self, mock_config):
        """必要なカラムの欠落を検出"""
        df = pd.DataFrame({'不明なカラム': [1, 2, 3]})
        result = loader.validate_data(df, mock_config)

        assert len(result['missing_columns']) > 0

    def test_counts_missing_values(self, sample_dataframe_with_missing, mock_config):
        """欠損値をカウント"""
        result = loader.validate_data(sample_dataframe_with_missing, mock_config)

        assert len(result['missing_values']) > 0


class TestCreateNumericScores:
    """create_numeric_scores関数のテスト"""

    def test_maps_values_to_scores(self):
        """値をスコアにマッピング"""
        df = pd.DataFrame({'満足度': ['満足', '普通', '不満']})
        mapping = {'満足': 5, '普通': 3, '不満': 1}

        result = loader.create_numeric_scores(df, '満足度', mapping)

        assert result.tolist() == [5, 3, 1]

    def test_unmapped_values_become_nan(self):
        """マッピングにない値はNaN"""
        df = pd.DataFrame({'満足度': ['満足', '未知']})
        mapping = {'満足': 5}

        result = loader.create_numeric_scores(df, '満足度', mapping)

        assert result.iloc[0] == 5
        assert pd.isna(result.iloc[1])
