from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+


def timestamp_to_taipei_datetime(ts):
    # 使用 UTC 建立 timezone-aware 的 datetime 物件
    utc_time = datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))

    # 轉換為台北時間
    taipei_time = utc_time.astimezone(ZoneInfo("Asia/Taipei"))

    return taipei_time.strftime('%Y-%m-%d %H:%M UTC+8')


if __name__ == "__main__":
    # 測試
    ts = 1753171200  # 這是某個 timestamp
    print(timestamp_to_taipei_datetime(ts))
