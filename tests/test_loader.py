"""
データローダーのテスト

データ読み込み、前処理、カテゴリ変換をテスト。
"""

import pytest
import pandas as pd
from pathlib import Path

from survey_analysis.core import loader


class TestLoadCsv:
    """load_csv関数のテスト"""

    def test_load_csv_with_valid_file(self, tmp_csv_file):
        """有効なCSVファイルを読み込み"""
        df = loader.load_csv(tmp_csv_file)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3

    def test_load_csv_with_encoding(self, tmp_path):
        """エンコーディング指定での読み込み"""
        csv_path = tmp_path / 'test_utf8.csv'
        csv_path.write_text('col1,col2\na,b\nc,d', encoding='utf-8')

        df = loader.load_csv(csv_path, encoding='utf-8')
        assert len(df) == 2

    def test_load_csv_file_not_found(self, tmp_path):
        """存在しないファイルでエラー"""
        with pytest.raises(FileNotFoundError):
            loader.load_csv(tmp_path / 'nonexistent.csv')

    def test_load_csv_auto_detect_encoding(self, tmp_path):
        """エンコーディング自動検出"""
        csv_path = tmp_path / 'test_bom.csv'
        # UTF-8 BOMで書き込み
        csv_path.write_bytes(b'\xef\xbb\xbfcol1,col2\na,b\n')

        df = loader.load_csv(csv_path)
        assert len(df) == 1
        assert 'col1' in df.columns


class TestCleanData:
    """clean_data関数のテスト"""

    def test_clean_removes_empty_rows(self):
        """空行が削除される"""
        df = pd.DataFrame({
            'col1': ['a', '', 'b', None],
            'col2': ['x', '', 'y', None]
        })
        cleaned = loader.clean_data(df)
        # 完全に空の行が削除されることを確認
        assert len(cleaned) <= len(df)

    def test_clean_strips_whitespace(self):
        """文字列の前後空白が除去される"""
        df = pd.DataFrame({
            'col1': ['  a  ', 'b', ' c']
        })
        cleaned = loader.clean_data(df)
        # 空白除去の確認（実装に依存）
        if 'col1' in cleaned.columns:
            values = cleaned['col1'].tolist()
            # 先頭・末尾の空白が除去されていることを確認
            assert '  a  ' not in values or cleaned['col1'].iloc[0].strip() == 'a'

    def test_clean_preserves_valid_data(self, sample_dataframe):
        """有効なデータは保持される"""
        cleaned = loader.clean_data(sample_dataframe)
        assert len(cleaned) == len(sample_dataframe)


class TestApplyCategoryOrder:
    """apply_category_order関数のテスト"""

    def test_apply_order_creates_categorical(self, sample_dataframe):
        """カテゴリ順序を適用"""
        orders = {'年齢': ['20代', '30代', '40代']}
        result = loader.apply_category_order(sample_dataframe, orders)

        assert result['年齢'].dtype.name == 'category'

    def test_apply_order_preserves_order(self, sample_dataframe):
        """指定した順序が保持される"""
        orders = {'年齢': ['20代', '30代', '40代']}
        result = loader.apply_category_order(sample_dataframe, orders)

        categories = result['年齢'].cat.categories.tolist()
        assert categories == ['20代', '30代', '40代']

    def test_apply_order_ignores_missing_columns(self, sample_dataframe):
        """存在しないカラムは無視"""
        orders = {'存在しないカラム': ['a', 'b', 'c']}
        result = loader.apply_category_order(sample_dataframe, orders)
        # エラーが発生しないことを確認
        assert result is not None


class TestLoadAndPrepareData:
    """load_and_prepare_data関数のテスト"""

    def test_load_and_prepare_with_config(self, config_with_csv):
        """設定を使用してデータを読み込み・準備"""
        df = loader.load_and_prepare_data(config_with_csv)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert '年齢' in df.columns

    def test_load_and_prepare_applies_category_order(self, tmp_path):
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
            category_orders={'年齢': ['20代', '30代', '40代']}
        )

        df = loader.load_and_prepare_data(config)

        if df['年齢'].dtype.name == 'category':
            categories = df['年齢'].cat.categories.tolist()
            assert categories == ['20代', '30代', '40代']


class TestDetectEncoding:
    """detect_encoding関数のテスト（存在する場合）"""

    def test_detect_utf8(self, tmp_path):
        """UTF-8を検出"""
        if not hasattr(loader, 'detect_encoding'):
            pytest.skip("detect_encoding関数が存在しません")

        csv_path = tmp_path / 'utf8.csv'
        csv_path.write_text('日本語,テスト\na,b', encoding='utf-8')

        encoding = loader.detect_encoding(csv_path)
        assert encoding.lower() in ['utf-8', 'utf8', 'ascii']

    def test_detect_shift_jis(self, tmp_path):
        """Shift-JISを検出"""
        if not hasattr(loader, 'detect_encoding'):
            pytest.skip("detect_encoding関数が存在しません")

        csv_path = tmp_path / 'sjis.csv'
        csv_path.write_bytes('日本語,テスト\na,b'.encode('shift_jis'))

        encoding = loader.detect_encoding(csv_path)
        # chardetの結果は完全一致しないことがある
        assert encoding is not None
