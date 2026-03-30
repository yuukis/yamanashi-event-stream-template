# yamanashi-event-stream Consumer 最小構成テンプレート

## 目的

このテンプレートは、別アカウントで運用されている [yamanashi-event-stream](https://github.com/yuukis/yamanashi-event-stream) から Amazon EventBridge 経由でイベントを受信し、自分の AWS アカウント内の Lambda で処理するための最小構成です。

まずは **動作確認しやすい最小版** として、受信したイベントを CloudWatch Logs に出力します。

## アーキテクチャ

```
[Producer Account]                    [Consumer Account (このテンプレート)]
EventBridge (default bus)    →       Custom EventBridge Bus
                                      ↓ EventBridge Rule
                                      Consumer Lambda
                                      ↓
                                      CloudWatch Logs
```

## デプロイ方法

### 前提条件

- AWS CLI がインストール・設定済み
- AWS SAM CLI がインストール済み
- Producer アカウント ID を知っている

### デプロイ手順

1. このリポジトリをクローン/ダウンロード

2. SAM ビルド
   ```bash
   sam build
   ```

3. SAM デプロイ
   ```bash
   sam deploy --guided
   ```

4. 初回デプロイ時は以下のパラメータを設定:
   - **ProducerAccountId**: Producer を運用している AWS アカウント ID（12桁）
   - **ConsumerBusName**: EventBridge bus 名（デフォルト: `yamanashi-event-consumer`）
   - **FilterGroupKey**: 特定の group_key のみ受信したい場合に指定（空なら全件受信）

### デプロイ例

```bash
# 全件受信する場合
sam deploy --parameter-overrides ProducerAccountId=703459494350

# 特定のグループのみ受信する場合
sam deploy --parameter-overrides ProducerAccountId=703459494350 FilterGroupKey=jawsug-yamanashi
```

## パラメータ

| パラメータ名 | 型 | デフォルト値 | 説明 |
|---|---|---|---|
| ProducerAccountId | String | なし（必須） | Producer を運用している AWS アカウント ID |
| ConsumerBusName | String | yamanashi-event-consumer | 作成する custom EventBridge bus の名前 |
| FilterGroupKey | String | 空文字 | 特定の group_key のみ受信したい場合に指定。空なら全件受信 |

## デプロイ後に取得できる情報

デプロイ完了後、以下の情報が出力されます：

- **ConsumerEventBusName**: 作成された EventBridge bus の名前
- **ConsumerEventBusArn**: 作成された EventBridge bus の ARN
- **ConsumerFunctionName**: Consumer Lambda 関数名
- **ConsumerRuleName**: EventBridge ルール名

これらの情報は AWS コンソールの CloudFormation スタックの「出力」タブでも確認できます。

## Producer 側に伝えるべき情報

Producer 側の管理者に以下の情報を伝えてください：

1. **あなたの AWS アカウント ID**: `aws sts get-caller-identity` で確認
2. **Consumer EventBridge bus ARN**: デプロイ後の出力から取得

Producer 側では、あなたのアカウント・bus に対してクロスアカウント送信設定を行います。

## 動作確認

### CloudWatch Logs で受信確認

1. AWS コンソールで CloudWatch Logs を開く
2. `/aws/lambda/{ConsumerFunctionName}` のロググループを確認
3. イベント受信時に以下の情報がログ出力されます：
   - Source
   - Detail-type
   - UID
   - Title
   - Group key
   - Event URL

### ログ出力例

```
[INFO] Source: yamanashi.tech.events
[INFO] Detail-type: event.created
[INFO] UID: connpass-123456
[INFO] Title: JAWS-UG 山梨 LT会
[INFO] Group key: jawsug-yamanashi
[INFO] Event URL: https://connpass.com/event/123456/
```

## 受信するイベント形式

このテンプレートは以下の形式のイベントを受信します：

- **source**: `yamanashi.tech.events`
- **detail-type**: `event.created`
- **detail**: イベントの詳細（JSON）

### detail の全フィールド

| フィールド | 型 | 説明 | 必須 |
|---|---|---|---|
| schema_version | String | スキーマバージョン | ✓ |
| event_kind | String | イベント種別（`event.created`） | ✓ |
| uid | String | イベントの一意識別子 | ✓ |
| event_id | Number or null | 元サービスでのイベントID | - |
| title | String | イベントタイトル | - |
| catch | String | イベントの概要・キャッチコピー | - |
| event_url | String | イベントページのURL | - |
| hash_tag | String | イベントのハッシュタグ | - |
| started_at | String | 開始日時（ISO 8601形式） | - |
| ended_at | String | 終了日時（ISO 8601形式） | - |
| updated_at | String | 最終更新日時（ISO 8601形式） | - |
| open_status | String | 募集状況（`open`、`closed`など） | - |
| owner_name | String | 主催者名 | - |
| place | String | 開催場所名 | - |
| address | String | 開催場所の住所 | - |
| group_key | String or null | グループの識別キー | - |
| group_name | String | グループ名 | - |
| group_url | String | グループのURL | - |

### detail JSON サンプル

```json
{
  "schema_version": "1",
  "event_kind": "event.created",
  "uid": "connpass-123456",
  "event_id": 123456,
  "title": "JAWS-UG 山梨 LT会",
  "catch": "AWSをテーマにしたLT会です",
  "event_url": "https://connpass.com/event/123456/",
  "hash_tag": "#jawsug",
  "started_at": "2026-03-20T19:00:00+09:00",
  "ended_at": "2026-03-20T21:00:00+09:00",
  "updated_at": "2026-03-10T08:30:00+09:00",
  "open_status": "open",
  "owner_name": "JAWS-UG 山梨",
  "place": "山梨県立図書館",
  "address": "山梨県甲府市...",
  "group_key": "jawsug-yamanashi",
  "group_name": "JAWS-UG 山梨",
  "group_url": "https://..."
}
```

## トラブルシューティング

### イベントが受信できない場合

1. **Producer 側の設定確認**
   - あなたのアカウントID・bus ARN が正しく設定されているか
   - Producer 側のアクセス権限が正しく設定されているか

2. **EventBridge ルールの確認**
   - AWS コンソールで EventBridge ルールが有効になっているか
   - フィルタ条件が想定通りか（特に `FilterGroupKey` の設定）

3. **Lambda の確認**
   - Lambda 関数が正常にデプロイされているか
   - CloudWatch Logs でエラーが出ていないか

### よくある問題

- **group_key フィルタ**: `FilterGroupKey` を設定すると、その値と完全一致するイベントのみ受信します。部分一致やワイルドカードは使用できません。
- **null 値**: `group_key` や `event_id` は null の場合があります。フィルタ設定時は注意してください。

## カスタマイズ

このテンプレートは最小構成です。必要に応じて以下の拡張を検討してください：

- DynamoDB へのイベント保存
- Slack/Discord への通知
- SQS/SNS を経由した非同期処理
- エラーハンドリングの強化

## リソース

- [Amazon EventBridge ユーザーガイド](https://docs.aws.amazon.com/eventbridge/)
- [AWS SAM 開発者ガイド](https://docs.aws.amazon.com/serverless-application-model/)
- [AWS Lambda 開発者ガイド](https://docs.aws.amazon.com/lambda/)