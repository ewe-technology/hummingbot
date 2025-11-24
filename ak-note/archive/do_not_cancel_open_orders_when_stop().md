# 結論先說：沒有。

在現在的 Hummingbot（v2 scripts）裡，不管是 CLI 的 stop 指令，還是你在 script 裡呼叫的 HummingbotApplication.main_application().stop()，都會把當前 strategy 的 active orders 取消掉。官方文件也有明寫：

> Run stop command to stop the running strategy. Doing this will also cancel all active orders.
> hummingbot.org

exit 也是一樣，會 cancel 掉 outstanding orders 才退出介面。
> hummingbot.org

所以答案是：**沒有一個「正常的 stop」可以保留未成交訂單。**

## 那如果你真的想「停策略但保留掛單」要怎麼做？

### 方案 A：不要呼叫 HummingbotApplication.main_application().stop()

你現在的流程大概是：

```python
if self._order_placed < self._target_building_times:
    self._place_demo_orders(...)
    self._order_placed += 1
else:
    self.logger().info("🎉 建倉任務完成，準備停止策略…")
    HummingbotApplication.main_application().stop()
    return
```

如果你的目的是：

- 下完 N 次單之後，不要再下新單，但 **保留** 已掛在交易所上的單

做法可以是改成讓策略進入「idle 模式」，而不是真正去 stop() Hummingbot：

```python
if self._order_placed < self._target_building_times:
    self._place_demo_orders(spot_connector_name, perp_connector_name)
    self._order_placed += 1
else:
    if not self._stopped:
        self.logger().info("🎉 建倉任務完成，進入 idle 模式（不再下單，但保留現有掛單）")
        self._stopped = True

    # 這裡直接 return，不呼叫 stop()
    return
```

然後在 on_tick 最一開始就已經有：

```python
if self._stopped:
    return
```

這樣的效果會是：

- Hummingbot instance & script 還在跑（還能下 status 看掛單、餘額、log 等）
- 不會再呼叫 _place_demo_orders()，所以不會有新單
- 因為你沒有呼叫 .stop() 或 CLI stop，現有的掛單就會照常留在交易所

要真正關掉 bot / instance 的時候，你可以自己操作：

- 手動到交易所把掛單清掉，然後在 CLI 輸入 exit
- 或者先下 stop（這時候才會把掛單 cancel），再 exit

### 方案 B（不太建議）：暴力關閉 Process 來保留掛單

官方文件有提到一個「順手但危險」的方式：如果你用 binary 版，直接關掉視窗，active orders 會留在交易所，不會被 cancel。
> hummingbot.org

類似地，如果你是自己從 source 跑 Python，把 process kill -9 / 關掉 terminal，也通常會留下掛單不動。

但這有幾個問題：

- Hummingbot 來不及做任何 cleanup，之後重啟時 script 一開始的狀態跟交易所真實狀態可能不同（會有你之前講的「ghost orders」問題）
  > GitHub
- 對長期穩定運行不友善（debug 也變難）

所以這個我只會當成「緊急狀況」用，不會用在你這種「設計好的自動流程」。

## 小結：實務建議

你的 use case 比較像：

「自動掛完一組期現單 → 然後程式就不要再動，但讓掛單繼續留在 Hyperliquid / 交易所上。」

**最乾淨的作法：**

1. 拿掉 `HummingbotApplication.main_application().stop()` 那一行。

2. 用你自己 `_stopped` flag 控制 on_tick 不再做任何事（不下新單）：
   - `_place_demo_orders` 僅執行固定次數
   - 之後 on_tick 只 log 或完全 return

3. 之後要清倉 / 收掛單的時候：
   - 手動到交易所按「取消全部掛單」
   - 或是在 Hummingbot 這邊自己寫個關倉 script / 下一個策略來處理
