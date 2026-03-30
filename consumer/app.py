import json
import logging
from typing import Dict, Any

# ログレベルを設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    EventBridge からイベントを受信して CloudWatch Logs に出力する
    """
    try:
        logger.info("Received event from EventBridge")
        
        # EventBridge イベントの基本情報を取得
        source = event.get("source", "")
        detail_type = event.get("detail-type", "")
        detail = event.get("detail", {})
        
        # detail から主要な項目を取得（安全に）
        uid = detail.get("uid", "")
        title = detail.get("title", "")
        group_key = detail.get("group_key", "")
        event_url = detail.get("event_url", "")
        
        # ログ出力
        logger.info(f"Source: {source}")
        logger.info(f"Detail-type: {detail_type}")
        logger.info(f"UID: {uid}")
        logger.info(f"Title: {title}")
        logger.info(f"Group key: {group_key}")
        logger.info(f"Event URL: {event_url}")
        
        # 受信したイベント全体をデバッグ用に出力
        logger.info(f"Full event detail: {json.dumps(detail, ensure_ascii=False)}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Event processed successfully",
                "uid": uid,
                "title": title
            }, ensure_ascii=False)
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        logger.error(f"Event: {json.dumps(event, default=str, ensure_ascii=False)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Failed to process event",
                "message": str(e)
            }, ensure_ascii=False)
        }