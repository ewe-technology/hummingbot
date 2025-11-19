
# **Hummingbot Connector In-Flight Orders 限制說明**
版本：v1.0  
作者：AK（依 ChatGPT 解說整理）  
日期：2025-11-19

---

## 📌 **結論（最重要）**

### **❌ Hummingbot 無法取得「交易所帳號下的所有 open orders」**  
### **❌ Connector 也不會自動同步交易所所有 open orders**  
### **❌ Hummingbot 沒有任何變數可存放帳號全部 open orders**  

### **✔ Hummingbot 只能追蹤「它自己送出的訂單」 → in_flight_orders**

這是 Hummingbot 官方架構的刻意設計，不是 bug。

---

# 1️⃣ 為什麼 Hummingbot 的 `in_flight_orders` 永遠不會包含交易所全部 open orders？

根據 Hummingbot 官方 connector 架構：

> **InFlightOrder = 由 Hummingbot 自己送出、並由訂單追蹤器管理的訂單。**  
> （不是帳號下所有訂單）

意義上：

- InFlightOrders 代表 Hummingbot 所下的、正在交易所中進行生命週期追蹤的訂單  
- Hummingbot 不會主動同步帳號所有 open orders  
- 交易所手動下單、其他 bot 下單等都不會被 Hummingbot 追蹤

---

# 2️⃣ Hummingbot 使用哪些變數「只追蹤自己下的訂單」？

| 變數 / 方法 | 內容 | 是否包含帳號全部 open orders？ |
|------------|------|--------------------------------|
| `in_flight_orders` | Hummingbot 送出的 active 訂單追蹤器 | ❌ |
| `get_active_orders()` | 同上 | ❌ |
| `active_orders_df()` | 將 in_flight_orders 轉成 DataFrame | ❌ |
| `order_tracker` | 保存 InFlightOrders | ❌ |
| `get_order_status()` | 查某個 orderId 的狀態 | ❌（需要 ID，不能列全部） |

➡ **這些 API 都只認識 Hummingbot 自己送出的 order**  
➡ **所有「外部來源的訂單」都不會出現在任何變數裡**

包含：

- 網頁 UI 下的單  
- 手機 App 下的單  
- 其他 bot 下的單  
- 甚至是同一個帳號、但在以前 session 下的單（除非 HBOT 當時有追蹤）

---

# 3️⃣ Hummingbot 為什麼不支援「抓帳號所有 open orders」？

官方設計原因包括：

### **1. 性能與延遲**
查詢 openOrders API 在很多交易所：

- 速率限制高  
- latency 大  
- 開銷重

Hummingbot 重視 **低延遲、即時做市**，所以不依賴這種高頻查詢。

---

### **2. 避免混淆 order lifecycle**
如果帳號有手動單 + bot 單，會出現：

- orderId 不一致  
- 無法追蹤下單來源  
- 同步衝突  
- race condition（交易所回報 vs bot local state）

所以 Hummingbot 只追蹤「自己知道的訂單」。

---

### **3. connector 模型簡化**
所有 connector（Binance, Bybit, OKX, Hyperliquid…）都遵守相同模式：

> **不會自動同步帳號 open orders，只追蹤本 instance 的訂單生命週期**

---

# 4️⃣ 那要如何取得「真正的帳號全部 open orders」？

答案是：

# ⭐ **自己 call 交易所 API**

以 Hyperliquid 為例：

### REST API：
```http
POST https://api.hyperliquid.xyz/info
Content-Type: application/json

{
  "type": "openOrders",
  "user": "0x你的地址",
  "dex": ""
}
```

你可以在 Hummingbot script 裡寫（示意）：

```python
import aiohttp

async def fetch_hl_open_orders(self):
    url = "https://api.hyperliquid.xyz/info"
    payload = {
        "type": "openOrders",
        "user": self.owner_address,
        "dex": ""
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            return await resp.json()
```

---

# 5️⃣ 整合建議：同時使用兩種訂單來源

| 來源 | 用途 |
|------|------|
| `in_flight_orders` | Hummingbot 自己下的單（可 cancel / modify） |
| `openOrders API` | 帳號實際全部 open orders（用於監控 / 風控 / 對帳） |

合併後你可以做：

- 真正意義上的「全帳號訂單監控」  
- 偵測是否有外部來源的單  
- 自動對帳（例如發現 ghost order）  
- 自動清理非 HBOT 單的風控動作

---

# 6️⃣ 小結：你只需要記住這幾點

### ❌ Hummingbot connector 不會同步帳號 open orders  
### ❌ Hummingbot 沒有任何變數保存帳號 open orders  
### ❗ 你看到的 `in_flight_orders` 只代表 **Hummingbot 自己送出的訂單**  
### ⭐ 想要全部 open orders → 自己打交易所 API

---
