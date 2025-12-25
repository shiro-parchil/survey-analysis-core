# Google Apps Script テンプレート

Googleフォームでアンケートを作成・集約するためのGASテンプレート。

## ファイル構成

| ファイル | 用途 |
|---------|------|
| `FormGenerator.template.gs` | フォーム自動生成 |
| `ResponseAggregator.template.gs` | 回答集約・CSVエクスポート |

## 使用方法

### 1. フォーム生成

1. [Google Apps Script](https://script.google.com) で新規プロジェクト作成
2. `FormGenerator.template.gs` の内容を貼り付け
3. プレースホルダーを置換:
   - `{{PROJECT_NAME}}` → プロジェクト名
   - `{{FORM_TITLE}}` → フォームタイトル
   - `{{FORM_DESCRIPTION}}` → フォーム説明
   - `{{SECTION_B_TITLE}}` → セクションBのタイトル
   - `{{SECTION_B_DESCRIPTION}}` → セクションBの説明
4. `createSurveyForm()` を実行
5. ログにフォームURLが出力される

### 2. 回答集約

1. フォームに紐付いたスプレッドシートを開く
2. 拡張機能 → Apps Script
3. `ResponseAggregator.template.gs` の内容を貼り付け
4. プレースホルダーを置換
5. `aggregateResponses()` を実行

### 3. CSVエクスポート

```javascript
// スクリプトエディタで実行
exportToCsv()
// → Google DriveにCSVファイルが作成される
```

### 4. 自動集約トリガー設定

```javascript
// 新規回答時に自動で集約
createFormSubmitTrigger()
```

## プレースホルダー一覧

### FormGenerator

| プレースホルダー | 説明 | 例 |
|-----------------|------|-----|
| `{{PROJECT_NAME}}` | プロジェクト名 | Cocoon |
| `{{FORM_TITLE}}` | フォームタイトル | ユーザーニーズ調査 |
| `{{FORM_DESCRIPTION}}` | フォーム説明 | サービス改善のためのアンケートです |
| `{{SECTION_B_TITLE}}` | セクションBタイトル | サービス利用状況 |
| `{{SECTION_B_DESCRIPTION}}` | セクションB説明 | 現在のSNS利用について |
| `{{CUSTOM_QUESTIONS}}` | カスタム質問 | 追加質問のコード |

### ResponseAggregator

| プレースホルダー | 説明 | 例 |
|-----------------|------|-----|
| `{{PROJECT_NAME}}` | プロジェクト名 | Cocoon |

## カスタマイズ例

### 質問を追加

`addSectionB()` 関数内に追加:

```javascript
// 複数選択（チェックボックス）
form.addCheckboxItem()
  .setTitle('B-4. よく使う機能を選んでください')
  .setChoiceValues(['機能A', '機能B', '機能C'])
  .setRequired(true);

// グリッド形式
form.addGridItem()
  .setTitle('B-5. 各機能の重要度を評価してください')
  .setRows(['機能A', '機能B', '機能C'])
  .setColumns(['非常に重要', '重要', '普通', 'あまり重要でない', '全く重要でない'])
  .setRequired(true);
```

### 除外列を変更

`ResponseAggregator` の `excludeColumns` を編集:

```javascript
excludeColumns: [
  'メールアドレス',
  'タイムスタンプ',
  '個人情報フィールド',  // 追加
],
```

### 列名をリネーム

```javascript
renameColumns: {
  'A-1. 年齢': 'age',
  'A-2. 性別': 'gender',
  'B-1. 満足度': 'satisfaction',  // 追加
},
```

## survey-analysis-core との連携

エクスポートしたCSVを `SurveyConfig.raw_data_path` に配置して分析:

```python
from survey_analysis.core import load_and_prepare_data
from my_project.config import MySurveyConfig

config = MySurveyConfig()  # raw_data_path = 'data/survey_responses.csv'
df = load_and_prepare_data(config)
print(f"読み込み完了: {len(df)} 件")
```

## 注意事項

- GASの実行時間制限: 6分/回
- 大量回答（1000件以上）は分割処理を検討
- 個人情報は除外列に追加して出力しない
- CSVはBOM付きUTF-8で出力（Excel対応）
