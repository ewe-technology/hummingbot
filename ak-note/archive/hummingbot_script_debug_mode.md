# 開發hummingbot script要如何進入 debug mode?
1. 使用 vsCode (pycharm community版不行)
2. 安裝 VSCode + Python extension（一次性）
   1. 裝 VSCode
   2. 在 Extensions 搜 Python，裝官方的 Python 擴充。
3. 在 VSCode 建 launch.json
   1. 在你的 hummingbot 專案根目錄開 VSCode
   2. 左側點「執行與偵錯（小蟲子 ▶）」
   3. 點「建立 launch.json」
   4. 選「Python」
   5. 內容改成這樣（或把下面加進去你原本的 configurations 裡）：
        ```
        {
        "version": "0.2.0",
        "configurations": [
            {
            "name": "Attach to Hummingbot (debugpy)",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "127.0.0.1",
                "port": 5678
            },
            "justMyCode": false
            }
        ]
        }

        ```
4. 實際 Debug 流程（以 Windows + cmd 為例）
   1. 在開 Hummingbot 前設環境變數
   2. cmd `set HBOT_DEBUGPY=1`
   3. 實測上需要這段
      ```
        # # 如果要 debugpy，在這裡放
        # import debugpy

        # debugpy.listen(("0.0.0.0", 5678))
        # self.logger().info("🐞 Debugger waiting... Attach with VSCode.")
        # # 這行會讓 HBOT 停在這裡，直到 VSCode attach
        # debugpy.wait_for_client()
      ```
      但是如果不註解掉的話會沒辦法正確stop，要註解這段才能重新啟動
   4. 啟動 hummingbot `python bin\hummingbot.py`
   5. 進入 Hummingbot CLI 後： `start --script hyperliquid_candles_balance_positions.py`
   6. 此時 script 會跑到 debugpy.wait_for_client() 就停住，log 會看到： `🐞 debugpy 等待連線 port 5678 ...`
5. 在 VSCode Attach
   1. 打開 VSCode（已開你的專案）
   2. 左邊 Debug panel 選擇 「Attach to Hummingbot (debugpy）」
   3. 按「Start Debugging」
   4. 連上後，script 會繼續往下跑，你在 VSCode 裡設的 breakpoints（例如 on_tick、_log_candle）就會開始生效。
6. 平常不用 debug 時，關掉 Hummingbot，重新開一個 cmd，不要設定 HBOT_DEBUGPY，就會像現在一樣正常跑，不會卡。
