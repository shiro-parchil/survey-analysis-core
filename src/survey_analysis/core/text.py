"""
テキスト分析モジュール

形態素解析、頻出語分析、TF-IDF、ワードクラウド生成を提供。
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import warnings
import re

import pandas as pd
import numpy as np

from survey_analysis.base.config import SurveyConfig

warnings.filterwarnings('ignore')

# オプショナル依存
_JANOME_AVAILABLE: bool = False
_SKLEARN_AVAILABLE: bool = False
_WORDCLOUD_AVAILABLE: bool = False

try:
    from janome.tokenizer import Tokenizer
    _JANOME_AVAILABLE = True
except ImportError:
    Tokenizer = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    _SKLEARN_AVAILABLE = True
except ImportError:
    TfidfVectorizer = None

try:
    from wordcloud import WordCloud
    _WORDCLOUD_AVAILABLE = True
except ImportError:
    WordCloud = None


# デフォルトストップワード（日本語）
DEFAULT_STOPWORDS = [
    'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ',
    'ある', 'いる', 'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や',
    'れる', 'など', 'なっ', 'ない', 'この', 'ため', 'その', 'あっ', 'よう',
    'また', 'もの', 'という', 'あり', 'まで', 'られ', 'なる', 'へ', 'か',
    'だ', 'これ', 'によって', 'により', 'おり', 'より', 'による', 'ず', 'なり',
    'られる', 'において', 'ば', 'なかっ', 'なく', 'しかし', 'について', 'せ',
    'だっ', 'その他', 'できる', 'それ', 'ない', 'です', 'ます', 'でし',
    'ませ', 'ん', 'よ', 'ね', 'けど', 'けれど', 'だけ', 'でも', 'じゃ',
    '思う', '思い', '感じ', '欲しい', 'ほしい', 'たい', 'くださ', 'ください',
    '特に', 'とても', 'すごく', 'やはり', 'やっぱり', '本当', 'ほんと',
]


def check_janome_available() -> bool:
    """Janomeが利用可能か確認"""
    return _JANOME_AVAILABLE


def check_wordcloud_available() -> bool:
    """WordCloudが利用可能か確認"""
    return _WORDCLOUD_AVAILABLE


def tokenize_japanese_text(
    text: str,
    pos_filter: Optional[List[str]] = None,
    stopwords: Optional[List[str]] = None,
    min_length: int = 2
) -> List[str]:
    """
    日本語テキストを形態素解析してトークン化

    Args:
        text: 入力テキスト
        pos_filter: 抽出する品詞（None=名詞・動詞・形容詞）
        stopwords: 除外する単語
        min_length: 最小文字数

    Returns:
        List[str]: トークンリスト
    """
    if not _JANOME_AVAILABLE:
        raise ImportError("janomeがインストールされていません: pip install janome")

    if pd.isna(text) or not isinstance(text, str) or not text.strip():
        return []

    if pos_filter is None:
        pos_filter = ['名詞', '動詞', '形容詞']

    if stopwords is None:
        stopwords = DEFAULT_STOPWORDS

    tokenizer = Tokenizer()
    tokens = []

    for token in tokenizer.tokenize(text):
        # 品詞フィルタ
        pos = token.part_of_speech.split(',')[0]
        if pos not in pos_filter:
            continue

        # 基本形を使用
        base_form = token.base_form
        if base_form == '*':
            base_form = token.surface

        # フィルタリング
        if len(base_form) < min_length:
            continue
        if base_form in stopwords:
            continue
        if re.match(r'^[0-9０-９]+$', base_form):  # 数字のみ除外
            continue

        tokens.append(base_form)

    return tokens


def extract_word_frequency(
    texts: List[str],
    config: Optional[SurveyConfig] = None,
    top_n: int = 50,
    pos_filter: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    テキストリストから頻出語を抽出

    Args:
        texts: テキストリスト
        config: SurveyConfig（stopwords使用）
        top_n: 上位N語
        pos_filter: 品詞フィルタ

    Returns:
        pd.DataFrame: 頻出語と出現回数
    """
    stopwords = config.stopwords if config else DEFAULT_STOPWORDS

    all_tokens = []
    for text in texts:
        tokens = tokenize_japanese_text(
            text,
            pos_filter=pos_filter,
            stopwords=stopwords
        )
        all_tokens.extend(tokens)

    word_counts = Counter(all_tokens)
    top_words = word_counts.most_common(top_n)

    return pd.DataFrame(top_words, columns=['word', 'count'])


def extract_tfidf_keywords(
    texts: List[str],
    config: Optional[SurveyConfig] = None,
    top_n: int = 20,
    max_features: int = 1000
) -> pd.DataFrame:
    """
    TF-IDFでキーワードを抽出

    Args:
        texts: テキストリスト
        config: SurveyConfig
        top_n: 上位N語
        max_features: 最大特徴数

    Returns:
        pd.DataFrame: キーワードとTF-IDFスコア
    """
    if not _SKLEARN_AVAILABLE:
        raise ImportError("scikit-learnがインストールされていません")

    stopwords = config.stopwords if config else DEFAULT_STOPWORDS

    # テキストをトークン化して結合
    tokenized_texts = []
    for text in texts:
        tokens = tokenize_japanese_text(text, stopwords=stopwords)
        tokenized_texts.append(' '.join(tokens))

    # 空のテキストを除去
    tokenized_texts = [t for t in tokenized_texts if t.strip()]

    if not tokenized_texts:
        return pd.DataFrame(columns=['word', 'tfidf_score'])

    # TF-IDF計算
    vectorizer = TfidfVectorizer(max_features=max_features)
    tfidf_matrix = vectorizer.fit_transform(tokenized_texts)

    # 平均TF-IDFスコア
    mean_tfidf = tfidf_matrix.mean(axis=0).A1
    words = vectorizer.get_feature_names_out()

    word_scores = list(zip(words, mean_tfidf))
    word_scores.sort(key=lambda x: x[1], reverse=True)

    return pd.DataFrame(word_scores[:top_n], columns=['word', 'tfidf_score'])


def generate_wordcloud(
    texts: List[str],
    config: Optional[SurveyConfig] = None,
    save_path: Optional[Path] = None,
    width: int = 800,
    height: int = 400,
    background_color: str = 'white',
    font_path: Optional[str] = None
) -> Optional[Any]:
    """
    ワードクラウドを生成

    Args:
        texts: テキストリスト
        config: SurveyConfig
        save_path: 保存パス
        width: 幅
        height: 高さ
        background_color: 背景色
        font_path: 日本語フォントパス

    Returns:
        WordCloud: 生成されたワードクラウド（またはNone）
    """
    if not _WORDCLOUD_AVAILABLE:
        raise ImportError("wordcloudがインストールされていません: pip install wordcloud")

    stopwords = config.stopwords if config else DEFAULT_STOPWORDS

    # トークン化
    all_tokens = []
    for text in texts:
        tokens = tokenize_japanese_text(text, stopwords=stopwords)
        all_tokens.extend(tokens)

    if not all_tokens:
        print("警告: トークンが抽出できませんでした")
        return None

    text_combined = ' '.join(all_tokens)

    # フォントパス検出（日本語対応）
    if font_path is None:
        font_path = _find_japanese_font()

    # ワードクラウド生成
    wc_params = {
        'width': width,
        'height': height,
        'background_color': background_color,
        'max_words': 100,
        'collocations': False,
    }

    if font_path:
        wc_params['font_path'] = font_path

    wc = WordCloud(**wc_params)
    wc.generate(text_combined)

    if save_path:
        wc.to_file(str(save_path))
        print(f"  ✓ ワードクラウド保存: {save_path.name}")

    return wc


def _find_japanese_font() -> Optional[str]:
    """日本語フォントを検索"""
    import platform

    font_paths = []

    if platform.system() == 'Darwin':  # macOS
        font_paths = [
            '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc',
            '/System/Library/Fonts/Hiragino Sans GB.ttc',
            '/Library/Fonts/Arial Unicode.ttf',
        ]
    elif platform.system() == 'Windows':
        font_paths = [
            'C:/Windows/Fonts/msgothic.ttc',
            'C:/Windows/Fonts/meiryo.ttc',
            'C:/Windows/Fonts/YuGothM.ttc',
        ]
    else:  # Linux
        font_paths = [
            '/usr/share/fonts/truetype/fonts-japanese-gothic.ttf',
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf',
        ]

    for path in font_paths:
        if Path(path).exists():
            return path

    return None


def analyze_freetext_column(
    df: pd.DataFrame,
    column: str,
    config: Optional[SurveyConfig] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    自由記述カラムを分析

    Args:
        df: データフレーム
        column: カラム名
        config: SurveyConfig
        output_dir: 出力ディレクトリ

    Returns:
        dict: 分析結果
    """
    # 有効なテキストを抽出
    texts = df[column].dropna().astype(str).tolist()
    texts = [t for t in texts if t.strip() and t.lower() != 'nan']

    result = {
        'column': column,
        'total_responses': len(texts),
        'word_frequency': None,
        'tfidf_keywords': None,
        'wordcloud_path': None
    }

    if len(texts) == 0:
        print(f"  警告: '{column}' に有効なテキストがありません")
        return result

    print(f"\n分析中: {column} ({len(texts)} 件)")

    # 頻出語
    try:
        result['word_frequency'] = extract_word_frequency(texts, config, top_n=30)
        print(f"  ✓ 頻出語抽出完了 (上位30語)")
    except Exception as e:
        print(f"  警告: 頻出語抽出に失敗 - {e}")

    # TF-IDF
    try:
        if _SKLEARN_AVAILABLE:
            result['tfidf_keywords'] = extract_tfidf_keywords(texts, config, top_n=20)
            print(f"  ✓ TF-IDFキーワード抽出完了 (上位20語)")
    except Exception as e:
        print(f"  警告: TF-IDF抽出に失敗 - {e}")

    # ワードクラウド
    if output_dir and _WORDCLOUD_AVAILABLE:
        try:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            wc_path = output_dir / f"wordcloud_{column}.png"
            generate_wordcloud(texts, config, save_path=wc_path)
            result['wordcloud_path'] = str(wc_path)
        except Exception as e:
            print(f"  警告: ワードクラウド生成に失敗 - {e}")

    return result


def analyze_all_freetext(
    df: pd.DataFrame,
    freetext_columns: List[str],
    config: Optional[SurveyConfig] = None,
    output_dir: Optional[Path] = None
) -> Dict[str, Dict[str, Any]]:
    """
    複数の自由記述カラムを一括分析

    Args:
        df: データフレーム
        freetext_columns: 自由記述カラムのリスト
        config: SurveyConfig
        output_dir: 出力ディレクトリ

    Returns:
        dict: カラム名 → 分析結果のマッピング
    """
    print("\n" + "=" * 60)
    print("テキスト分析")
    print("=" * 60)

    results = {}

    for column in freetext_columns:
        if column not in df.columns:
            print(f"警告: カラム '{column}' が見つかりません")
            continue

        result = analyze_freetext_column(df, column, config, output_dir)
        results[column] = result

    print("\n" + "=" * 60)
    print(f"テキスト分析完了: {len(results)} カラム")
    print("=" * 60)

    return results


def export_text_analysis_results(
    results: Dict[str, Dict[str, Any]],
    output_dir: Path
) -> List[Path]:
    """
    テキスト分析結果をCSVに出力

    Args:
        results: 分析結果
        output_dir: 出力ディレクトリ

    Returns:
        List[Path]: 出力したファイルパス
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    saved_files = []

    for column, result in results.items():
        # 頻出語
        if result.get('word_frequency') is not None:
            freq_path = output_dir / f"word_freq_{column}.csv"
            result['word_frequency'].to_csv(freq_path, index=False, encoding='utf-8-sig')
            saved_files.append(freq_path)

        # TF-IDF
        if result.get('tfidf_keywords') is not None:
            tfidf_path = output_dir / f"tfidf_{column}.csv"
            result['tfidf_keywords'].to_csv(tfidf_path, index=False, encoding='utf-8-sig')
            saved_files.append(tfidf_path)

    print(f"テキスト分析結果を保存: {len(saved_files)} ファイル")
    return saved_files
