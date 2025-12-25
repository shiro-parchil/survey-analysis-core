"""
クロス集計モジュールのテスト

crosstab.pyの各関数をテスト。
"""

import pytest
import pandas as pd

from survey_analysis.core import crosstab


class TestCreateCrosstab:
    """create_crosstab関数のテスト"""

    def test_basic_crosstab(self, sample_dataframe):
        """基本的なクロス集計"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        assert isinstance(ct, pd.DataFrame)
        assert ct.shape[0] > 0
        assert ct.shape[1] > 0

    def test_crosstab_with_config(self, sample_dataframe, mock_config):
        """設定を使用したクロス集計"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            'age',
            'gender',
            config=mock_config
        )
        assert isinstance(ct, pd.DataFrame)

    def test_crosstab_with_margins(self, sample_dataframe):
        """合計行・列付きクロス集計"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別',
            margins=True
        )
        assert '合計' in ct.index
        assert '合計' in ct.columns

    def test_crosstab_normalize_index(self, sample_dataframe):
        """行ごとに正規化したクロス集計"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別',
            normalize='index'
        )
        # 各行の合計が100%になる
        row_sums = ct.sum(axis=1)
        for s in row_sums:
            assert abs(s - 100) < 0.1

    def test_crosstab_missing_column_raises_error(self, sample_dataframe):
        """存在しないカラムでエラー"""
        with pytest.raises(ValueError, match="カラムが見つかりません"):
            crosstab.create_crosstab(
                sample_dataframe,
                '存在しないカラム',
                '性別'
            )


class TestCreateCrosstabWithTotals:
    """create_crosstab_with_totals関数のテスト"""

    def test_includes_totals(self, sample_dataframe):
        """合計が含まれる"""
        ct = crosstab.create_crosstab_with_totals(
            sample_dataframe,
            '年齢',
            '性別'
        )
        assert '合計' in ct.index
        assert '合計' in ct.columns


class TestCreateCrosstabPercentage:
    """create_crosstab_percentage関数のテスト"""

    def test_row_percentage(self, sample_dataframe):
        """行ごとのパーセンテージ"""
        ct = crosstab.create_crosstab_percentage(
            sample_dataframe,
            '年齢',
            '性別',
            by='row'
        )
        # 各行の合計が約100%
        row_sums = ct.sum(axis=1)
        for s in row_sums:
            assert abs(s - 100) < 0.1

    def test_column_percentage(self, sample_dataframe):
        """列ごとのパーセンテージ"""
        ct = crosstab.create_crosstab_percentage(
            sample_dataframe,
            '年齢',
            '性別',
            by='column'
        )
        # 各列の合計が約100%
        col_sums = ct.sum(axis=0)
        for s in col_sums:
            assert abs(s - 100) < 0.1


class TestCreateMultiselectCrosstab:
    """create_multiselect_crosstab関数のテスト"""

    def test_multiselect_expansion(self):
        """複数選択の展開"""
        df = pd.DataFrame({
            '年齢': ['20代', '30代', '20代'],
            '趣味': ['読書、映画', '映画、音楽', '読書']
        })
        ct = crosstab.create_multiselect_crosstab(df, '年齢', '趣味')

        assert '読書' in ct.columns
        assert '映画' in ct.columns
        assert '音楽' in ct.columns

    def test_multiselect_with_custom_delimiter(self):
        """カスタム区切り文字での展開"""
        df = pd.DataFrame({
            '年齢': ['20代', '30代'],
            '趣味': ['読書,映画', '音楽,ゲーム']
        })
        ct = crosstab.create_multiselect_crosstab(
            df, '年齢', '趣味', delimiter=','
        )

        assert '読書' in ct.columns
        assert '映画' in ct.columns

    def test_multiselect_with_empty_data(self):
        """空データで空DataFrameを返す"""
        df = pd.DataFrame({
            '年齢': ['20代'],
            '趣味': [None]
        })
        ct = crosstab.create_multiselect_crosstab(df, '年齢', '趣味')
        assert len(ct) == 0

    def test_multiselect_strips_whitespace(self):
        """空白が除去される"""
        df = pd.DataFrame({
            '年齢': ['20代'],
            '趣味': ['  読書  、  映画  ']
        })
        ct = crosstab.create_multiselect_crosstab(df, '年齢', '趣味')

        assert '読書' in ct.columns
        assert '映画' in ct.columns


class TestGetCrosstabSummary:
    """get_crosstab_summary関数のテスト"""

    def test_summary_structure(self, sample_dataframe):
        """サマリーの構造"""
        ct = crosstab.create_crosstab_with_totals(
            sample_dataframe,
            '年齢',
            '性別'
        )
        summary = crosstab.get_crosstab_summary(ct, '年齢', '性別')

        assert 'row_var' in summary
        assert 'col_var' in summary
        assert 'n_rows' in summary
        assert 'n_cols' in summary
        assert 'total_n' in summary
        assert 'max_cell' in summary

    def test_max_cell_info(self, sample_dataframe):
        """最頻セル情報"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        summary = crosstab.get_crosstab_summary(ct, '年齢', '性別')

        max_cell = summary['max_cell']
        assert 'row' in max_cell
        assert 'col' in max_cell
        assert 'count' in max_cell
        assert 'percentage' in max_cell


class TestFilterCrosstabByCategory:
    """filter_crosstab_by_category関数のテスト"""

    def test_filter_rows(self, sample_dataframe):
        """行のフィルタ"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        filtered = crosstab.filter_crosstab_by_category(
            ct,
            row_categories=['20代', '30代']
        )

        assert '20代' in filtered.index
        assert '30代' in filtered.index
        assert '40代' not in filtered.index

    def test_filter_columns(self, sample_dataframe):
        """列のフィルタ"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        filtered = crosstab.filter_crosstab_by_category(
            ct,
            col_categories=['男性']
        )

        assert '男性' in filtered.columns
        assert '女性' not in filtered.columns


class TestCalculateRowPercentages:
    """calculate_row_percentages関数のテスト"""

    def test_row_percentages(self, sample_dataframe):
        """行パーセンテージ計算"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        pct = crosstab.calculate_row_percentages(ct)

        # 各行の合計が約100%
        row_sums = pct.sum(axis=1)
        for s in row_sums:
            assert abs(s - 100) < 0.1


class TestCalculateColumnPercentages:
    """calculate_column_percentages関数のテスト"""

    def test_column_percentages(self, sample_dataframe):
        """列パーセンテージ計算"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        pct = crosstab.calculate_column_percentages(ct)

        # 各列の合計が約100%
        col_sums = pct.sum(axis=0)
        for s in col_sums:
            assert abs(s - 100) < 0.1


class TestExportCrosstabsToCsv:
    """export_crosstabs_to_csv関数のテスト"""

    def test_export_creates_files(self, sample_dataframe, tmp_path):
        """CSVファイルが作成される"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        crosstabs = {'age_x_gender': ct}

        saved_files = crosstab.export_crosstabs_to_csv(
            crosstabs,
            str(tmp_path),
            prefix='test'
        )

        assert len(saved_files) == 1
        assert 'test_age_x_gender.csv' in saved_files[0]

    def test_export_creates_directory(self, sample_dataframe, tmp_path):
        """ディレクトリが作成される"""
        ct = crosstab.create_crosstab(
            sample_dataframe,
            '年齢',
            '性別'
        )
        new_dir = tmp_path / 'new_output'
        crosstabs = {'age_x_gender': ct}

        crosstab.export_crosstabs_to_csv(
            crosstabs,
            str(new_dir),
            prefix='test'
        )

        assert new_dir.exists()
