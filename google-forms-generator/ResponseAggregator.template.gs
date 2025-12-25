/**
 * {{PROJECT_NAME}} アンケート回答集約スクリプト
 *
 * Googleフォームの回答をCSVエクスポート用に整形。
 * survey-analysis-coreパッケージでの分析用にデータを準備。
 *
 * 使用方法:
 * 1. フォームに紐付いたスプレッドシートでスクリプトエディタを開く
 * 2. このコードを貼り付け
 * 3. aggregateResponses() を実行
 */

// ========================================
// 設定（要カスタマイズ）
// ========================================

const AGGREGATOR_CONFIG = {
  // 回答シート名
  responseSheetName: 'フォームの回答 1',

  // 出力シート名
  outputSheetName: '集約データ',

  // 除外する列（個人情報など）
  excludeColumns: [
    'メールアドレス',
    'タイムスタンプ',
  ],

  // 列名のリネーム（元の列名 → 新しい列名）
  renameColumns: {
    'A-1. 年齢': 'age',
    'A-2. 性別': 'gender',
    'A-3. 職業': 'occupation',
    // 必要に応じて追加
  },
};

// ========================================
// メイン関数
// ========================================

/**
 * 回答データを集約
 */
function aggregateResponses() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 回答シートを取得
  const responseSheet = ss.getSheetByName(AGGREGATOR_CONFIG.responseSheetName);
  if (!responseSheet) {
    Logger.log('回答シートが見つかりません: ' + AGGREGATOR_CONFIG.responseSheetName);
    return;
  }

  // データを取得
  const data = responseSheet.getDataRange().getValues();
  if (data.length < 2) {
    Logger.log('回答データがありません');
    return;
  }

  // ヘッダー行
  const headers = data[0];

  // 除外列のインデックスを取得
  const excludeIndices = [];
  headers.forEach((header, index) => {
    if (AGGREGATOR_CONFIG.excludeColumns.includes(header)) {
      excludeIndices.push(index);
    }
  });

  // 新しいヘッダーを作成
  const newHeaders = headers
    .filter((_, index) => !excludeIndices.includes(index))
    .map(header => AGGREGATOR_CONFIG.renameColumns[header] || header);

  // データ行を処理
  const newData = [newHeaders];
  for (let i = 1; i < data.length; i++) {
    const row = data[i].filter((_, index) => !excludeIndices.includes(index));
    newData.push(row);
  }

  // 出力シートを作成または取得
  let outputSheet = ss.getSheetByName(AGGREGATOR_CONFIG.outputSheetName);
  if (outputSheet) {
    outputSheet.clear();
  } else {
    outputSheet = ss.insertSheet(AGGREGATOR_CONFIG.outputSheetName);
  }

  // データを書き込み
  outputSheet.getRange(1, 1, newData.length, newData[0].length).setValues(newData);

  Logger.log('集約完了: ' + (newData.length - 1) + ' 件の回答');
}

/**
 * CSVとしてエクスポート
 */
function exportToCsv() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(AGGREGATOR_CONFIG.outputSheetName);

  if (!sheet) {
    Logger.log('集約シートが見つかりません。先にaggregateResponses()を実行してください');
    return;
  }

  const data = sheet.getDataRange().getValues();
  const csv = data.map(row => row.map(cell => {
    // セル内にカンマや改行がある場合はダブルクォートで囲む
    const str = String(cell);
    if (str.includes(',') || str.includes('\n') || str.includes('"')) {
      return '"' + str.replace(/"/g, '""') + '"';
    }
    return str;
  }).join(',')).join('\n');

  // BOM付きUTF-8でBlob作成
  const bom = '\uFEFF';
  const blob = Utilities.newBlob(bom + csv, 'text/csv', 'survey_responses.csv');

  // ドライブに保存
  const file = DriveApp.createFile(blob);
  Logger.log('CSVエクスポート完了: ' + file.getUrl());
}

/**
 * 基本統計を出力
 */
function outputBasicStats() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName(AGGREGATOR_CONFIG.outputSheetName);

  if (!sheet) {
    Logger.log('集約シートが見つかりません');
    return;
  }

  const data = sheet.getDataRange().getValues();
  const headers = data[0];
  const rowCount = data.length - 1;

  Logger.log('===== 基本統計 =====');
  Logger.log('回答数: ' + rowCount);
  Logger.log('列数: ' + headers.length);

  // 各列の回答分布（上位5件）
  headers.forEach((header, colIndex) => {
    const values = data.slice(1).map(row => row[colIndex]).filter(v => v !== '');
    const counts = {};
    values.forEach(v => {
      counts[v] = (counts[v] || 0) + 1;
    });

    const sorted = Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    Logger.log('\n【' + header + '】');
    sorted.forEach(([value, count]) => {
      const pct = ((count / values.length) * 100).toFixed(1);
      Logger.log('  ' + value + ': ' + count + ' (' + pct + '%)');
    });
  });
}

// ========================================
// トリガー設定
// ========================================

/**
 * 新規回答時に自動集約するトリガーを設定
 */
function createFormSubmitTrigger() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();

  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'onFormSubmit') {
      ScriptApp.deleteTrigger(trigger);
    }
  });

  // 新しいトリガーを作成
  ScriptApp.newTrigger('onFormSubmit')
    .forSpreadsheet(ss)
    .onFormSubmit()
    .create();

  Logger.log('フォーム送信トリガーを設定しました');
}

/**
 * フォーム送信時のハンドラー
 */
function onFormSubmit(e) {
  // 集約処理を実行
  aggregateResponses();
  Logger.log('新規回答を集約しました: ' + new Date());
}
