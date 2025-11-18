# 參數選項 
常見的範例code中
```commandline
    connector_name = "hyperliquid_perpetual"
    trading_pair = "BTC-USDC"

    logger.info("🟢 初始化 Hyperliquid candles...")

    candles_config = CandlesConfig(
        connector=connector_name,
        trading_pair=trading_pair,
        interval="1m",
        max_records=200,
    )

    candles = CandlesFactory.get_candle(candles_config)

    # 啟動 candles（內部會自己開 task 去抓資料）
    candles.start()

其中的 candles_config 我們要怎知道可以填哪些?

```

1. connector 可以填什麼？要去哪裡查？
   1. 路徑： hummingbot / connector / (derivative or exchange) 每個資料夾就是一個 connector。
   2. 如 hummingbot / connector / derivative / hyperliquid_perpetual  就是填 hyperliquid_perpetual
2. trading_pair 可以填什麼？要去哪裡查？
   1. 沒有本地清單，要自己打 API 拿，因為市場是浮動的
   2. 範例程式如下
   ```
   import requests
   from hummingbot.connector.hyperliquid_perpetual.hyperliquid_perpetual_constants import (
       PERPETUAL_BASE_URL,
       META_INFO,
   )
   
   def fetch_pairs():
       url = PERPETUAL_BASE_URL + "/info"
   
       # Hyperliquid 的 meta 請求類型，對應 constants 裡的 META_INFO = "meta"
       payload = {"type": META_INFO}
   
       resp = requests.post(url, json=payload, timeout=10)
       resp.raise_for_status()
       data = resp.json()
   
       # 先印出 data 的 key，方便你自己看結構
       print("keys:", list(data.keys()))
   
       # 一般 hyperliquid /info(meta) 會有類似 universe / assetCtxs 之類的欄位
       universe = data.get("universe") or data.get("assetCtxs") or []
   
       print("=== Hyperliquid perpetual markets ===")
       for asset in universe:
           # 這裡的欄位名稱要照實際回傳為準
           # 常見的結構裡會有像 name / index / szDecimals 等
           print(asset)
   
   if __name__ == "__main__":
       fetch_pairs()
   ```
3. interval 可以填什麼？要去哪裡查？
   1. interval 是 Candle Feed 自己定義的，不是交易所定義的
   2. 直接看 repo 這裡：hummingbot/data_feed/candles_feed/candles_base.py
   3. 搜尋 SUPPORTED_INTERVALS 
   4. 會看到類似: 
   ```
      SUPPORTED_INTERVALS = [
    "1s",
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1h",
    "4h",
    "1d",
   ]
   ```
   5. 不過每間交易所可以接受的 intervals 都有點不同 像是hyperliquid 就不支援 1s ，等到時候噴錯時錯誤訊息上面也會寫
4. max_records
   1. 最多保留多少 K 線資料
   2. max_records=200 → 只保留 200 根 K 線（最常用）
   3. max_records=1500 → 最大值，佔記憶體較多
5. start_time（可選）如果你想要 一次把歷史資料抓回來，可以加這個：start_time=int(time.time()*1000) - 7*24*60*60*1000  # 往前 7 天
6. end_time （可選）多用於回測情境。