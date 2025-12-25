/**
 * {{PROJECT_NAME}} アンケートフォーム自動生成スクリプト
 *
 * このテンプレートをGoogle Apps Scriptエディタに貼り付けて使用。
 * {{PLACEHOLDER}} を実際の値に置換してください。
 *
 * 使用方法:
 * 1. https://script.google.com で新規プロジェクト作成
 * 2. このコードを貼り付け
 * 3. プレースホルダーを置換
 * 4. createSurveyForm() を実行
 */

// ========================================
// 設定（要カスタマイズ）
// ========================================

const CONFIG = {
  formTitle: '{{FORM_TITLE}}',
  formDescription: '{{FORM_DESCRIPTION}}',
  confirmationMessage: 'ご回答ありがとうございました。',
  collectEmail: false,
  allowResponseEdits: false,
};

// ========================================
// メイン関数
// ========================================

/**
 * アンケートフォームを作成
 */
function createSurveyForm() {
  const form = FormApp.create(CONFIG.formTitle);
  form.setDescription(CONFIG.formDescription);
  form.setConfirmationMessage(CONFIG.confirmationMessage);
  form.setCollectEmail(CONFIG.collectEmail);
  form.setAllowResponseEdits(CONFIG.allowResponseEdits);

  // セクションを追加
  addSectionA(form);  // 基本属性
  addSectionB(form);  // メイン質問
  addSectionC(form);  // 自由記述

  Logger.log('フォーム作成完了: ' + form.getEditUrl());
  return form;
}

// ========================================
// セクションA: 基本属性
// ========================================

function addSectionA(form) {
  form.addSectionHeaderItem()
    .setTitle('セクションA: 基本属性')
    .setHelpText('まず、あなたについて教えてください');

  // A-1. 年齢
  form.addMultipleChoiceItem()
    .setTitle('A-1. 年齢')
    .setHelpText('あなたの年齢を選択してください')
    .setChoiceValues([
      '18歳未満',
      '18〜22歳',
      '23〜26歳',
      '27〜30歳',
      '31〜34歳',
      '35〜39歳',
      '40歳以上',
    ])
    .setRequired(true);

  // A-2. 性別
  form.addMultipleChoiceItem()
    .setTitle('A-2. 性別')
    .setChoiceValues([
      '男性',
      '女性',
      'その他',
      '回答しない',
    ])
    .setRequired(true);

  // A-3. 職業
  form.addMultipleChoiceItem()
    .setTitle('A-3. 職業')
    .setChoiceValues([
      '会社員（正社員）',
      '会社員（契約・派遣）',
      '公務員',
      '自営業・フリーランス',
      'パート・アルバイト',
      '学生',
      '専業主婦・主夫',
      '無職',
      'その他',
    ])
    .setRequired(true);

  // A-4. 居住地域
  form.addMultipleChoiceItem()
    .setTitle('A-4. 居住地域')
    .setChoiceValues([
      '北海道',
      '東北',
      '関東（東京除く）',
      '東京都',
      '中部',
      '近畿',
      '中国',
      '四国',
      '九州・沖縄',
    ])
    .setRequired(true);
}

// ========================================
// セクションB: メイン質問
// ========================================

function addSectionB(form) {
  form.addSectionHeaderItem()
    .setTitle('セクションB: {{SECTION_B_TITLE}}')
    .setHelpText('{{SECTION_B_DESCRIPTION}}');

  // B-1. 例: 満足度（リッカート尺度）
  form.addScaleItem()
    .setTitle('B-1. 現在のサービスにどの程度満足していますか？')
    .setBounds(1, 5)
    .setLabels('全く満足していない', '非常に満足している')
    .setRequired(true);

  // B-2. 例: 興味度（選択肢）
  form.addMultipleChoiceItem()
    .setTitle('B-2. 新サービスに興味はありますか？')
    .setChoiceValues([
      'とても興味がある',
      'やや興味がある',
      'どちらともいえない',
      'あまり興味がない',
      '全く興味がない',
    ])
    .setRequired(true);

  // B-3. 例: 複数選択
  form.addCheckboxItem()
    .setTitle('B-3. 興味のある機能を選んでください（複数選択可）')
    .setChoiceValues([
      '機能A',
      '機能B',
      '機能C',
      '機能D',
      'その他',
    ])
    .setRequired(false);

  // カスタム質問をここに追加
  // {{CUSTOM_QUESTIONS}}
}

// ========================================
// セクションC: 自由記述
// ========================================

function addSectionC(form) {
  form.addSectionHeaderItem()
    .setTitle('セクションC: ご意見・ご要望')
    .setHelpText('自由にお書きください（任意）');

  // C-1. 自由記述
  form.addParagraphTextItem()
    .setTitle('C-1. その他ご意見・ご要望があればお聞かせください')
    .setRequired(false);
}

// ========================================
// ユーティリティ
// ========================================

/**
 * フォームのURLを取得
 */
function getFormUrls() {
  const form = FormApp.getActiveForm();
  if (!form) {
    Logger.log('アクティブなフォームがありません');
    return;
  }

  Logger.log('編集URL: ' + form.getEditUrl());
  Logger.log('回答URL: ' + form.getPublishedUrl());
  Logger.log('回答スプレッドシートURL: ' + form.getDestinationId());
}

/**
 * 回答をスプレッドシートに接続
 */
function connectToSpreadsheet() {
  const form = FormApp.getActiveForm();
  if (!form) {
    Logger.log('アクティブなフォームがありません');
    return;
  }

  const ss = SpreadsheetApp.create(CONFIG.formTitle + ' 回答');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  Logger.log('スプレッドシート接続完了: ' + ss.getUrl());
}
