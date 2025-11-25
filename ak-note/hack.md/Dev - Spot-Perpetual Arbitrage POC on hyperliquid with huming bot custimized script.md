# Dev - Spot-Perpetual Arbitrage POC on hyperliquid with huming bot custimized script

## Scope : Hyperliquild

## 目前已完成

1. 用市價單，現貨與期貨各敲數次，用以建立起目標倉位或是加倉的 script (hyperliquid_spot_perp_position_building_bot.py)

## 待開發功能

### 倉位建立、加減倉與平倉

1. 用市價單，現貨與期貨各敲數次，用以關閉或減少目標倉位的 script
2. 用限價單，現貨與期貨各敲數次，用以建立起目標倉位或是加倉的 script
3. 期貨用市價，現貨用限價單，加以倉位管理的邏輯，偵測到現貨單被成交後立即用市價敲期貨把倉位進行對沖，用以建立起目標倉位或是加倉的 script
4. 期貨用市價，現貨用限價單，加以倉位管理的邏輯，偵測到現貨單被成交後立即用市價敲期貨把倉位進行對沖，用以建立起目標倉位或是加倉的 script
5. 期現都用限價單，加以倉位管理的邏輯，一有任何一邊的限價單被成交，立即另外一邊進行市價單敲入，用以建立起目標倉位或是加倉的 script
6. 期現都用限價單，加以倉位管理的邏輯，一有任何一邊的限價單被成交，立即另外一邊進行市價單敲入，用以關閉或減少目標倉位的 script

### 系統優化
7. 參數化配置，將目標倉位數量等變數改為環境變數
8. 共用函數抽象化，建立可複用的函數庫
9. 任務完成最基礎的通知功能 -> 初步方案：可以先接 telegram bot之類的

## 待確認與釐清的部分

1. Hummingbot 會在停止策略時 關閉所有訂單 -> 研究結果為底層 framework 的限制，不改底層的狀況下就是要在控制邏輯那邊控制，等到所有目標訂單都完成在關閉策略等方式
2. 無 UI 快速啟動目前還沒能成功執行 -> 待排除 `./bin/hummingbot_quickstart.py -p <PASSWORD> -f hyperliquid_candles_balance_positions.py --headless`
-> 有UI 帶參數的執行目前有測試可以 `./start -p a -f hyperliquid_spot_perp_position_building_bot.py`
3. 由於 humming bot 底層的限制 `in_flight_order` 取不到非由此script所發出的其他未成交訂單 -> 若未來需要取得所有未成交訂單可能要改底層或是另外去交易所拿
