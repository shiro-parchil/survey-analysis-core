# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-25

### Added

- `SurveyConfig` 抽象クラスによる依存注入パターン
- `ReportGenerator` 抽象クラス（レポート生成インターフェース）
- コアモジュール
  - `loader.py`: データ読み込み、エンコーディング自動検出、前処理
  - `stats.py`: 統計検定（χ²、t検定、ANOVA、相関）、FDR補正
  - `crosstab.py`: クロス集計、Tier別分析
  - `viz.py`: 可視化（ヒートマップ、棒グラフ、円グラフ）
  - `text.py`: テキスト分析（形態素解析、TF-IDF、ワードクラウド）
  - `audit.py`: データ品質監査
- ユーティリティ
  - `parsers.py`: 金額パース、日本語正規化、複数選択分割
- Claude Code設定テンプレート
- GASテンプレート（Googleフォーム生成、回答集約）
- Cocoon実装サンプル

### Technical Notes

- Python 3.10+ 対応
- オプション依存: `[text]` でJanome/WordCloud/scikit-learn
- 日本語フォント対応（japanize-matplotlib）
- ゼロコスト原則: LLM APIを使用しない設計
