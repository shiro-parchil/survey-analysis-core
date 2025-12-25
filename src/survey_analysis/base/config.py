"""
抽象設定クラス - プロジェクト固有設定を定義するベースクラス

使用方法:
    from survey_analysis.base.config import SurveyConfig

    class MySurveyConfig(SurveyConfig):
        @property
        def questions(self) -> dict:
            return {
                'age': 'Q1. 年齢',
                'gender': 'Q2. 性別',
            }

        @property
        def raw_data_path(self) -> Path:
            return Path('data/survey.csv')

        @property
        def output_dir(self) -> Path:
            return Path('output/analysis')
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any


class SurveyConfig(ABC):
    """
    プロジェクト固有設定を定義する抽象クラス

    各プロジェクトでこのクラスを継承し、
    質問マッピング、パス、カテゴリ順序等を定義する。
    """

    # ========================================
    # 必須プロパティ（サブクラスで実装必須）
    # ========================================

    @property
    @abstractmethod
    def questions(self) -> Dict[str, str]:
        """
        質問ID -> カラム名のマッピング

        Returns:
            dict: キーが短縮ID、値が実際のカラム名

        Example:
            {
                'age': 'Q1. あなたの年齢を教えてください',
                'gender': 'Q2. 性別を選択してください',
                'satisfaction': 'Q3. 満足度を5段階で評価してください',
            }
        """
        pass

    @property
    @abstractmethod
    def raw_data_path(self) -> Path:
        """
        アンケート生データのパス

        Returns:
            Path: CSVファイルへのパス（絶対パスまたはプロジェクトルートからの相対パス）
        """
        pass

    @property
    @abstractmethod
    def output_dir(self) -> Path:
        """
        分析結果の出力ディレクトリ

        Returns:
            Path: 出力先ディレクトリ（存在しない場合は自動作成される）
        """
        pass

    # ========================================
    # オプションプロパティ（デフォルト値あり）
    # ========================================

    @property
    def category_orders(self) -> Dict[str, List[str]]:
        """
        カテゴリカル変数の順序定義

        順序を指定することで、クロス集計やグラフでの表示順を制御。
        指定がない場合はデータ内の出現順。

        Returns:
            dict: キーがカラム名、値が順序付きリスト

        Example:
            {
                'age': ['10代', '20代', '30代', '40代', '50代以上'],
                'satisfaction': ['非常に不満', '不満', '普通', '満足', '非常に満足'],
            }
        """
        return {}

    @property
    def stopwords(self) -> List[str]:
        """
        テキスト分析用ストップワード

        自由記述の分析時に除外する単語リスト。

        Returns:
            list: 除外する単語のリスト

        Example:
            ['の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'です', 'ます']
        """
        return []

    @property
    def alpha(self) -> float:
        """
        統計的検定の有意水準

        Returns:
            float: 有意水準（デフォルト: 0.05）
        """
        return 0.05

    @property
    def encoding(self) -> str:
        """
        CSVファイルのエンコーディング

        Returns:
            str: エンコーディング名（デフォルト: 'utf-8-sig' for BOM付きUTF-8）
        """
        return 'utf-8-sig'

    @property
    def figure_settings(self) -> Dict[str, Any]:
        """
        グラフ生成の設定

        Returns:
            dict: matplotlib/seabornの設定

        Example:
            {
                'figsize': (12, 8),
                'dpi': 150,
                'style': 'whitegrid',
                'font_family': 'Noto Sans JP',
            }
        """
        return {
            'figsize': (12, 8),
            'dpi': 150,
            'style': 'whitegrid',
        }

    @property
    def crosstab_tiers(self) -> Dict[str, List[tuple]]:
        """
        クロス集計のTier定義

        優先度別にクロス集計のペアを定義。

        Returns:
            dict: Tier名をキー、(row_var, col_var) のタプルリストを値

        Example:
            {
                'tier1': [('age', 'satisfaction'), ('gender', 'purchase_intent')],
                'tier2': [('region', 'satisfaction')],
            }
        """
        return {}

    # ========================================
    # ユーティリティメソッド
    # ========================================

    def get_column_name(self, question_id: str) -> str:
        """
        質問IDから実際のカラム名を取得

        Args:
            question_id: 短縮質問ID

        Returns:
            str: 実際のカラム名（見つからない場合はIDをそのまま返す）
        """
        return self.questions.get(question_id, question_id)

    def get_question_id(self, column_name: str) -> Optional[str]:
        """
        カラム名から質問IDを逆引き

        Args:
            column_name: 実際のカラム名

        Returns:
            str or None: 質問ID（見つからない場合はNone）
        """
        for qid, col in self.questions.items():
            if col == column_name:
                return qid
        return None

    def ensure_output_dir(self) -> Path:
        """
        出力ディレクトリを作成（存在しない場合）

        Returns:
            Path: 作成された出力ディレクトリ
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)
        return self.output_dir

    def validate(self) -> List[str]:
        """
        設定の妥当性を検証

        Returns:
            list: エラーメッセージのリスト（空なら問題なし）
        """
        errors = []

        # raw_data_path の存在チェック
        if not self.raw_data_path.exists():
            errors.append(f"データファイルが見つかりません: {self.raw_data_path}")

        # questions が空でないかチェック
        if not self.questions:
            errors.append("questions が空です。少なくとも1つの質問を定義してください")

        # alpha の範囲チェック
        if not 0 < self.alpha < 1:
            errors.append(f"alpha は0〜1の範囲で指定してください: {self.alpha}")

        return errors
