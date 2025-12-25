"""
Cocoon プロジェクトのアンケート分析設定

survey-analysis-core パッケージを使用した実装例。
"""

from pathlib import Path
from typing import Dict, List, Optional

from survey_analysis.base import SurveyConfig


class CocoonSurveyConfig(SurveyConfig):
    """
    Cocoon ユーザーニーズ調査の設定

    289件のアンケートデータを分析するための設定。
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Args:
            project_root: プロジェクトルートパス。
                          Noneの場合は現在のディレクトリから解決。
        """
        if project_root is None:
            # デフォルト: group-chat-sns-business リポジトリのルート
            project_root = Path(__file__).resolve().parents[4]
        self._project_root = project_root

    @property
    def questions(self) -> Dict[str, str]:
        """質問ID → カラム名のマッピング"""
        return {
            # Section A: Demographics
            'age': 'A-1. 年齢',
            'gender': 'A-2. 性別',
            'region_pref': 'A-3-1. 居住地域',
            'region_type': 'A-3-2. 居住地域',
            'occupation': 'A-4. 職業・身分',
            'living_situation': 'A-5. 同居状況',
            'activity_time': 'A-6. 主な活動時間帯（複数選択可）',
            'hobbies': 'A-7. 趣味・関心カテゴリ（最大5つまで）',

            # Section B: SNS Usage
            'sns_used': 'B-1. 現在利用しているSNS/コミュニティサービス（複数選択可）',
            'sns_usage_time': 'B-2. 最もよく使うSNSでの1日の平均利用時間',
            'sns_satisfaction': 'B-8. 既存のSNSやコミュニティに対する全体的な満足度',

            # Section C: Relationships & Loneliness
            'loneliness': 'C-4. 最近1ヶ月で「孤独だ」と感じたことはありますか？',
            'offline_friends': 'C-5. オフラインで「趣味の話を深くできる友人」は何人いますか？',
            'new_relationship_desire': 'C-6. 新しい人間関係を作りたいと思いますか？',

            # Section E: Ideal Connection
            'ephemeral_evaluation': 'E-3. 「期間限定の関係」についてどう思いますか？',
            'ai_welcome': 'E-6. 以下のAI機能にどの程度興味がありますか？ [AIによるウェルカムメッセージ（参加時の挨拶代行）]',
            'ai_topic': 'E-6. 以下のAI機能にどの程度興味がありますか？ [AIによる話題提案（沈黙時に話題を提供）]',
            'dm_prohibition': 'E-8. DMなし（グループチャットのみ）のサービスについてどう思いますか？',

            # Section G: New Service
            'g1_service_interest': 'G-1. 以下のようなサービスがあったら、どのくらい興味がありますか？',
            'g5_continuation': 'G-5. 「気の合った人とは、次の週も同じグループで続けられる」仕組みについて',
            'g7a_payment_monthly': 'G-7a. このサービスに月額料金を払うとしたら、いくらまでなら許容できますか？',
            'g11_posting_frequency': 'G-11. 1回の参加（1週間のグループ）で、何日程度アクティブに投稿できそうですか？',

            # Section H: Free Text
            'h1_ideal_sns': 'H-1. 「こんなSNS・コミュニティがあったらいいのに」と思うことがあれば、自由にお書きください',
            'h2_connection_thoughts': 'H-2. 人とのつながりについて、日頃感じていることがあれば自由にお書きください',
        }

    @property
    def raw_data_path(self) -> Path:
        """アンケートCSVのパス"""
        return self._project_root / "tools" / "surveys" / "raw-data" / "user-needs-survey-v2.0.csv"

    @property
    def output_dir(self) -> Path:
        """出力ディレクトリ"""
        return self._project_root / "output" / "survey-analysis"

    @property
    def encoding(self) -> str:
        """ファイルエンコーディング（auto = 自動検出）"""
        return 'auto'

    @property
    def category_orders(self) -> Dict[str, List[str]]:
        """カテゴリカル変数の順序定義"""
        return {
            'age': [
                '18歳未満',
                '18〜22歳',
                '23〜26歳',
                '27〜29歳',
                '30〜34歳',
                '35〜39歳',
                '40〜49歳',
                '50〜59歳',
                '60歳以上'
            ],
            'sns_satisfaction': [
                'とても不満がある',
                'やや不満がある',
                'どちらともいえない',
                'やや満足している',
                'とても満足している'
            ],
            'loneliness': [
                'まったくない',
                'ほとんどない',
                'たまにある',
                '時々ある',
                'しばしばある',
                '常にある'
            ],
            'g1_service_interest': [
                'まったく興味がない',
                'あまり興味がない',
                'どちらともいえない',
                'やや興味がある',
                'とても興味がある'
            ],
        }

    @property
    def stopwords(self) -> List[str]:
        """テキスト分析用ストップワード"""
        return [
            'する', 'ある', 'いる', 'なる', 'こと', 'もの', 'の', 'に', 'を', 'は',
            'が', 'と', 'で', 'て', 'た', 'だ', 'です', 'ます', 'ない', 'れる',
            'られる', 'せる', 'させる', 'いう', '思う', '感じる', 'くる', 'やる',
            'ため', 'よう', 'そう', 'など', 'もっと', 'ちょっと', 'たり', 'とか',
            '的', '系', '感', 'さん', 'くん', 'ちゃん', 'お', 'ご', 'これ', 'それ',
            'あれ', 'どれ', 'この', 'その', 'あの', 'どの', 'ここ', 'そこ', 'あそこ',
            'どこ', '何', '誰', 'いつ', 'どう', 'なぜ', 'なに', 'どんな', 'ところ'
        ]

    @property
    def alpha(self) -> float:
        """有意水準"""
        return 0.05

    @property
    def crosstab_tiers(self) -> Dict[int, List[tuple]]:
        """Tier別クロス集計定義"""
        return {
            # Tier 1: PMF判定（最重要）
            1: [
                ('age', 'g1_service_interest'),
                ('loneliness', 'g1_service_interest'),
                ('sns_satisfaction', 'g1_service_interest'),
                ('age', 'g7a_payment_monthly'),
                ('gender', 'g7a_payment_monthly'),
            ],
            # Tier 2: 設計検証
            2: [
                ('ephemeral_evaluation', 'age'),
                ('ai_welcome', 'age'),
                ('ai_topic', 'age'),
                ('g5_continuation', 'ephemeral_evaluation'),
            ],
            # Tier 3: ペルソナ検証
            3: [
                ('hobbies', 'g1_service_interest'),
                ('occupation', 'activity_time'),
                ('offline_friends', 'new_relationship_desire'),
            ],
            # Tier 4: 運用設計
            4: [
                ('dm_prohibition', 'gender'),
                ('dm_prohibition', 'age'),
                ('g11_posting_frequency', 'age'),
            ],
        }

    @property
    def pmf_threshold(self) -> float:
        """PMF判定閾値（ターゲット層の興味度）"""
        return 0.50  # 50%

    @property
    def target_age_range(self) -> tuple:
        """ターゲット年齢層"""
        return ('23〜26歳', '27〜29歳', '30〜34歳')

    @property
    def numeric_mappings(self) -> Dict[str, Dict[str, int]]:
        """カテゴリ→数値変換マッピング"""
        return {
            'sns_satisfaction': {
                'とても満足している': 5,
                'やや満足している': 4,
                'どちらともいえない': 3,
                'やや不満がある': 2,
                'とても不満がある': 1
            },
            'loneliness': {
                '常にある': 6,
                'しばしばある': 5,
                '時々ある': 4,
                'たまにある': 3,
                'ほとんどない': 2,
                'まったくない': 1
            },
            'g1_service_interest': {
                'とても興味がある': 5,
                'やや興味がある': 4,
                'どちらともいえない': 3,
                'あまり興味がない': 2,
                'まったく興味がない': 1
            },
        }

    @property
    def figure_style(self) -> Dict:
        """グラフスタイル設定"""
        return {
            'dpi': 300,
            'figsize_small': (8, 6),
            'figsize_medium': (10, 8),
            'figsize_large': (12, 10),
            'font_size_title': 14,
            'font_size_label': 12,
            'font_size_tick': 10,
            'color_palette': 'Set2',
            'heatmap_cmap': 'RdYlGn_r',
        }
