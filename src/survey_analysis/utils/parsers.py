"""
ユーティリティモジュール

データパース、変換ユーティリティを提供。
"""

import re
from typing import Optional, Any, List, Dict


def parse_first_yen_amount(text: str) -> Optional[int]:
    """
    テキストから最初の円金額を抽出

    Args:
        text: 入力テキスト

    Returns:
        int or None: 抽出された金額（円）

    Examples:
        >>> parse_first_yen_amount("月額500円程度")
        500
        >>> parse_first_yen_amount("1,000円〜2,000円")
        1000
        >>> parse_first_yen_amount("無料")
        None
    """
    if not text or not isinstance(text, str):
        return None

    # パターン: 数字（カンマ区切り対応）+ 円
    pattern = r'([0-9,０-９，]+)\s*円'
    match = re.search(pattern, text)

    if not match:
        return None

    amount_str = match.group(1)

    # 全角→半角変換
    amount_str = amount_str.translate(str.maketrans('０１２３４５６７８９，', '0123456789,'))

    # カンマ除去
    amount_str = amount_str.replace(',', '')

    try:
        return int(amount_str)
    except ValueError:
        return None


def parse_range_to_midpoint(text: str) -> Optional[float]:
    """
    範囲テキストから中間値を抽出

    Args:
        text: 入力テキスト（例: "500円〜1,000円"）

    Returns:
        float or None: 中間値

    Examples:
        >>> parse_range_to_midpoint("500円〜1,000円")
        750.0
        >>> parse_range_to_midpoint("1000円以上")
        1000.0
    """
    if not text or not isinstance(text, str):
        return None

    # 範囲パターン
    range_pattern = r'([0-9,０-９，]+)\s*円?\s*[〜～\-−]\s*([0-9,０-９，]+)\s*円'
    match = re.search(range_pattern, text)

    if match:
        low = parse_first_yen_amount(match.group(1) + '円')
        high = parse_first_yen_amount(match.group(2) + '円')
        if low is not None and high is not None:
            return (low + high) / 2

    # 単一金額
    single = parse_first_yen_amount(text)
    if single is not None:
        return float(single)

    return None


def normalize_japanese_text(text: str) -> str:
    """
    日本語テキストを正規化

    Args:
        text: 入力テキスト

    Returns:
        str: 正規化されたテキスト
    """
    if not text or not isinstance(text, str):
        return ''

    # 全角→半角（英数字）
    text = text.translate(str.maketrans(
        'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ０１２３４５６７８９',
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    ))

    # 半角→全角（カタカナ）
    # ※必要に応じて実装

    # 空白の正規化
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def extract_numbers(text: str) -> List[int]:
    """
    テキストから全ての数値を抽出

    Args:
        text: 入力テキスト

    Returns:
        List[int]: 抽出された数値リスト
    """
    if not text or not isinstance(text, str):
        return []

    # 全角→半角
    text = text.translate(str.maketrans('０１２３４５６７８９', '0123456789'))

    # 数値抽出（カンマ区切り対応）
    pattern = r'[0-9,]+'
    matches = re.findall(pattern, text)

    numbers = []
    for match in matches:
        try:
            num = int(match.replace(',', ''))
            numbers.append(num)
        except ValueError:
            continue

    return numbers


def split_multiselect(
    text: str,
    delimiters: Optional[List[str]] = None
) -> List[str]:
    """
    複数選択テキストを分割

    Args:
        text: 入力テキスト
        delimiters: 区切り文字リスト

    Returns:
        List[str]: 分割された値リスト
    """
    if not text or not isinstance(text, str):
        return []

    if delimiters is None:
        delimiters = ['、', ',', '，', ';', '；']

    # 区切り文字で分割
    pattern = '|'.join(re.escape(d) for d in delimiters)
    parts = re.split(pattern, text)

    # 空白除去と空文字除外
    return [p.strip() for p in parts if p.strip()]


def categorize_by_threshold(
    value: Any,
    thresholds: List[tuple],
    default: str = 'その他'
) -> str:
    """
    値を閾値に基づいてカテゴリに分類

    Args:
        value: 分類する値
        thresholds: (上限値, カテゴリ名) のリスト（昇順）
        default: デフォルトカテゴリ

    Returns:
        str: カテゴリ名

    Examples:
        >>> thresholds = [(500, '低'), (1000, '中'), (float('inf'), '高')]
        >>> categorize_by_threshold(300, thresholds)
        '低'
        >>> categorize_by_threshold(800, thresholds)
        '中'
    """
    if value is None:
        return default

    for threshold, category in thresholds:
        if value <= threshold:
            return category

    return default


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    パーセンテージをフォーマット

    Args:
        value: パーセンテージ値
        decimals: 小数点以下桁数

    Returns:
        str: フォーマットされた文字列
    """
    return f"{value:.{decimals}f}%"


def format_number_japanese(value: int) -> str:
    """
    数値を日本語表記でフォーマット

    Args:
        value: 数値

    Returns:
        str: フォーマットされた文字列

    Examples:
        >>> format_number_japanese(12345)
        '1万2,345'
        >>> format_number_japanese(100000000)
        '1億'
    """
    if value >= 100000000:  # 1億以上
        oku = value // 100000000
        remainder = value % 100000000
        if remainder == 0:
            return f"{oku:,}億"
        else:
            man = remainder // 10000
            return f"{oku:,}億{man:,}万" if man > 0 else f"{oku:,}億"

    elif value >= 10000:  # 1万以上
        man = value // 10000
        remainder = value % 10000
        if remainder == 0:
            return f"{man:,}万"
        else:
            return f"{man:,}万{remainder:,}"

    else:
        return f"{value:,}"
