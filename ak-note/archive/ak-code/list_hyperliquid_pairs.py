import requests

from hummingbot.connector.derivative.hyperliquid_perpetual.hyperliquid_perpetual_constants import (
    META_INFO,
    PERPETUAL_BASE_URL,
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
