# Claude Code 設定テンプレート

survey-analysis-coreパッケージを利用するプロジェクト向けのClaude Code設定テンプレート。

## 使用方法

1. テンプレートファイルをプロジェクトの `.claude/` ディレクトリにコピー
2. `{{PLACEHOLDER}}` を実際の値に置換
3. ファイル名から `.template` を削除

## プレースホルダー一覧

| プレースホルダー | 説明 | 例 |
|-----------------|------|-----|
| `{{PROJECT_NAME}}` | プロジェクト名 | Cocoon, PoliParchil |
| `{{RESPONSE_COUNT}}` | 回答数 | 289 |
| `{{COLLECTION_PERIOD}}` | 収集期間 | 2025-12-05〜2025-12-06 |
| `{{QUESTION_COUNT}}` | 設問数 | 67 |
| `{{RAW_DATA_PATH}}` | 生データパス | data/survey.csv |
| `{{OUTPUT_DIR}}` | 出力ディレクトリ | output/survey-analysis |
| `{{CONFIG_PATH}}` | 設定ファイルパス | src/config.py |
| `{{PROJECT_CONFIG_MODULE}}` | 設定モジュール | myproject.config |
| `{{PROJECT_CONFIG_CLASS}}` | 設定クラス名 | MySurveyConfig |
| `{{TARGET_SEGMENT_DEFINITION}}` | ターゲット定義 | 23-34歳、オタク趣味 |
| `{{PMF_CRITERIA}}` | PMF判定基準 | ターゲット層50%以上が興味あり |
| `{{TIER_DEFINITIONS}}` | Tier定義 | - Tier 1: 年齢×興味 |
| `{{QUESTION_MAPPING_TABLE}}` | 質問マッピング表 | \| age \| Q1. 年齢 \| |
| `{{CUSTOM_KEYWORDS}}` | カスタムキーワード | - PoliPoli |
| `{{CUSTOM_TRIGGERS}}` | カスタムトリガー | - 政策レコメンド |

## ディレクトリ構造

```
claude-code/
├── README.md              # このファイル
├── agents/
│   └── survey-analysis-agent.template.md
├── commands/
│   └── survey-analysis.template.md
├── skills/
│   └── survey-analysis.template.md
└── rules/
    └── survey-statistical-analysis.md  # 汎用ルール（テンプレートではない）
```

## 設定例（Cocoon）

`examples/cocoon-config/` に完全な実装例があります。

## 注意事項

- `rules/survey-statistical-analysis.md` はテンプレートではなく、そのまま使用可能
- agents/ と skills/ は用途に応じて選択（両方使う必要はない）
- commands/ は `/survey-analysis` のようなSlash Commandを定義
