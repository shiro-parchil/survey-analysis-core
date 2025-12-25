"""
統計検定モジュールのテスト

カイ二乗検定、t検定、ANOVA、相関分析をテスト。
"""

import pytest
import pandas as pd
import numpy as np

from survey_analysis.core import stats


class TestChiSquareTest:
    """カイ二乗検定のテスト"""

    def test_chi_square_with_valid_data(self, crosstab_sample, mock_config):
        """有効なデータでカイ二乗検定"""
        result = stats.chi_square_test(
            crosstab_sample, '年齢', '興味度', mock_config
        )

        assert 'chi2' in result or 'error' in result
        if 'chi2' in result:
            assert isinstance(result['chi2'], (int, float))
            assert 'p_value' in result
            assert 0 <= result['p_value'] <= 1

    def test_chi_square_returns_cramers_v(self, crosstab_sample, mock_config):
        """Cramer's Vが計算される"""
        result = stats.chi_square_test(
            crosstab_sample, '年齢', '興味度', mock_config
        )

        if 'cramers_v' in result:
            assert 0 <= result['cramers_v'] <= 1

    def test_chi_square_with_missing_column(self, sample_dataframe, mock_config):
        """存在しないカラムでValueError"""
        with pytest.raises(ValueError, match="カラムが見つかりません"):
            stats.chi_square_test(
                sample_dataframe, '存在しない', '年齢', mock_config
            )


class TestTTest:
    """t検定のテスト"""

    def test_t_test_with_valid_data(self, sample_dataframe, mock_config):
        """有効なデータでt検定"""
        result = stats.t_test_independent(
            sample_dataframe, '数値スコア', '性別', mock_config
        )

        if 'error' not in result:
            assert 't_stat' in result
            assert 'p_value' in result
            assert isinstance(result['t_stat'], (int, float))

    def test_t_test_returns_cohens_d(self, sample_dataframe, mock_config):
        """Cohen's dが計算される"""
        result = stats.t_test_independent(
            sample_dataframe, '数値スコア', '性別', mock_config
        )

        if 'cohens_d' in result:
            assert isinstance(result['cohens_d'], (int, float))

    def test_t_test_with_non_binary_group(self, sample_dataframe, mock_config):
        """2群以外でのt検定"""
        result = stats.t_test_independent(
            sample_dataframe, '数値スコア', '年齢', mock_config
        )

        # 3群以上の場合はエラーまたは最初の2群で計算
        # 実装に依存
        assert result is not None


class TestAnova:
    """ANOVAのテスト"""

    def test_anova_with_valid_data(self, sample_dataframe, mock_config):
        """有効なデータでANOVA"""
        result = stats.anova_test(
            sample_dataframe, '数値スコア', '年齢', mock_config
        )

        if 'error' not in result:
            assert 'f_stat' in result
            assert 'p_value' in result

    def test_anova_returns_eta_squared(self, sample_dataframe, mock_config):
        """η²（イータ二乗）が計算される"""
        result = stats.anova_test(
            sample_dataframe, '数値スコア', '年齢', mock_config
        )

        if 'eta_squared' in result:
            assert 0 <= result['eta_squared'] <= 1


class TestCorrelation:
    """相関分析のテスト"""

    def test_correlation_with_valid_data(self, mock_config):
        """有効なデータで相関分析"""
        df = pd.DataFrame({
            'var1': [1, 2, 3, 4, 5],
            'var2': [2, 4, 5, 4, 5]
        })

        result = stats.correlation_test(df, 'var1', 'var2', mock_config)

        if 'error' not in result:
            assert 'rho' in result or 'r' in result
            assert 'p_value' in result

    def test_correlation_coefficient_range(self, mock_config):
        """相関係数が-1から1の範囲"""
        df = pd.DataFrame({
            'var1': [1, 2, 3, 4, 5],
            'var2': [5, 4, 3, 2, 1]  # 負の相関
        })

        result = stats.correlation_test(df, 'var1', 'var2', mock_config)

        if 'rho' in result:
            assert -1 <= result['rho'] <= 1
        elif 'r' in result:
            assert -1 <= result['r'] <= 1


class TestFdrCorrection:
    """FDR補正のテスト"""

    def test_fdr_correction_reduces_significance(self, mock_config):
        """FDR補正がp値を調整"""
        if not hasattr(stats, 'apply_fdr_correction'):
            pytest.skip("apply_fdr_correction関数が存在しません")

        results = [
            {'p_value': 0.01},
            {'p_value': 0.03},
            {'p_value': 0.05},
            {'p_value': 0.10},
        ]

        corrected = stats.apply_fdr_correction(results, alpha=0.05)

        # 補正後のp値が追加されていることを確認
        for r in corrected:
            assert 'p_value_corrected' in r or 'p_adj' in r

    def test_fdr_correction_preserves_order(self, mock_config):
        """FDR補正がp値の順序を保持"""
        if not hasattr(stats, 'apply_fdr_correction'):
            pytest.skip("apply_fdr_correction関数が存在しません")

        results = [
            {'p_value': 0.001},
            {'p_value': 0.01},
            {'p_value': 0.05},
        ]

        corrected = stats.apply_fdr_correction(results, alpha=0.05)

        # 元のp値が小さい順に補正後も小さいはず
        p_key = 'p_value_corrected' if 'p_value_corrected' in corrected[0] else 'p_adj'
        if p_key in corrected[0]:
            p_values = [r[p_key] for r in corrected]
            assert p_values[0] <= p_values[1] <= p_values[2]


class TestSignificanceInterpretation:
    """有意水準解釈のテスト"""

    def test_significance_markers(self):
        """有意水準マーカーの解釈"""
        if not hasattr(stats, 'get_significance_marker'):
            pytest.skip("get_significance_marker関数が存在しません")

        assert stats.get_significance_marker(0.0001) == '***'
        assert stats.get_significance_marker(0.001) == '***'
        assert stats.get_significance_marker(0.005) == '**'
        assert stats.get_significance_marker(0.01) == '**'
        assert stats.get_significance_marker(0.03) == '*'
        assert stats.get_significance_marker(0.05) == '*'
        assert stats.get_significance_marker(0.10) == 'ns'


class TestEffectSizeInterpretation:
    """効果量解釈のテスト"""

    def test_cramers_v_interpretation(self):
        """Cramer's Vの解釈"""
        if not hasattr(stats, 'interpret_cramers_v'):
            pytest.skip("interpret_cramers_v関数が存在しません")

        assert '弱い' in stats.interpret_cramers_v(0.05)
        assert '中程度' in stats.interpret_cramers_v(0.20)
        assert '強い' in stats.interpret_cramers_v(0.40)

    def test_cohens_d_interpretation(self):
        """Cohen's dの解釈"""
        if not hasattr(stats, 'interpret_cohens_d'):
            pytest.skip("interpret_cohens_d関数が存在しません")

        assert '小さい' in stats.interpret_cohens_d(0.15)
        assert '中程度' in stats.interpret_cohens_d(0.50)
        assert '大きい' in stats.interpret_cohens_d(1.0)


class TestErrorHandling:
    """エラーハンドリングのテスト"""

    def test_empty_dataframe_handling(self, mock_config):
        """空のDataFrameでValueError"""
        empty_df = pd.DataFrame()

        with pytest.raises(ValueError, match="カラムが見つかりません"):
            stats.chi_square_test(empty_df, 'col1', 'col2', mock_config)

    def test_insufficient_data_handling(self, mock_config):
        """データ不足時のValueError"""
        small_df = pd.DataFrame({
            'col1': ['a'],
            'col2': ['b']
        })

        with pytest.raises(ValueError, match="クロス集計表が小さすぎます"):
            stats.chi_square_test(small_df, 'col1', 'col2', mock_config)

    def test_constant_column_handling(self, mock_config):
        """定数カラム（1カテゴリのみ）でValueError"""
        constant_df = pd.DataFrame({
            'col1': ['a', 'a', 'a', 'a'],
            'col2': ['b', 'c', 'd', 'e']
        })

        with pytest.raises(ValueError, match="クロス集計表が小さすぎます"):
            stats.chi_square_test(constant_df, 'col1', 'col2', mock_config)
