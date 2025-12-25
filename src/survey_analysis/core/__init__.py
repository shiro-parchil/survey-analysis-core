"""
survey_analysis.core - コア分析モジュール

データ読み込み、統計分析、クロス集計、可視化、テキスト分析、監査機能を提供。
"""

from .loader import (
    detect_encoding,
    load_raw_data,
    clean_column_names,
    handle_missing_values,
    split_multiselect_cell,
    convert_ordered_categories,
    create_numeric_scores,
    add_derived_columns,
    load_and_prepare_data,
    validate_data,
)

from .stats import (
    chi_square_test,
    t_test_independent,
    anova_test,
    correlation_test,
    apply_fdr_correction,
    run_statistical_tests,
    analyze_missing_values,
    get_basic_stats,
    get_value_counts,
)

from .crosstab import (
    create_crosstab,
    create_crosstab_with_totals,
    create_percentage_crosstab,
    analyze_crosstabs_by_tier,
    export_crosstabs_to_csv,
)

from .viz import (
    setup_japanese_font,
    plot_crosstab_heatmap,
    plot_bar_chart,
    plot_stacked_bar,
    plot_pie_chart,
    plot_histogram,
    create_visualization_report,
)

from .text import (
    tokenize_japanese_text,
    extract_word_frequency,
    extract_tfidf_keywords,
    generate_wordcloud,
    analyze_freetext_column,
    analyze_all_freetext,
)

from .audit import (
    check_data_completeness,
    check_data_validity,
    check_data_consistency,
    generate_audit_report,
    get_data_profile,
)

__all__ = [
    # loader
    'detect_encoding',
    'load_raw_data',
    'clean_column_names',
    'handle_missing_values',
    'split_multiselect_cell',
    'convert_ordered_categories',
    'create_numeric_scores',
    'add_derived_columns',
    'load_and_prepare_data',
    'validate_data',
    # stats
    'chi_square_test',
    't_test_independent',
    'anova_test',
    'correlation_test',
    'apply_fdr_correction',
    'run_statistical_tests',
    'analyze_missing_values',
    'get_basic_stats',
    'get_value_counts',
    # crosstab
    'create_crosstab',
    'create_crosstab_with_totals',
    'create_percentage_crosstab',
    'analyze_crosstabs_by_tier',
    'export_crosstabs_to_csv',
    # viz
    'setup_japanese_font',
    'plot_crosstab_heatmap',
    'plot_bar_chart',
    'plot_stacked_bar',
    'plot_pie_chart',
    'plot_histogram',
    'create_visualization_report',
    # text
    'tokenize_japanese_text',
    'extract_word_frequency',
    'extract_tfidf_keywords',
    'generate_wordcloud',
    'analyze_freetext_column',
    'analyze_all_freetext',
    # audit
    'check_data_completeness',
    'check_data_validity',
    'check_data_consistency',
    'generate_audit_report',
    'get_data_profile',
]
