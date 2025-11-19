"""
目前卡死在 connector 沒辦法正確建立連線

"""


import asyncio
import logging
import os
from dotenv import load_dotenv
import inspect

from hummingbot.data_feed.candles_feed.candles_factory import CandlesFactory, CandlesConfig

# ★ 這兩個 import 是重點：拉進 Hyperliquid 現貨 connector ＋ config_map
from hummingbot.connector.exchange.hyperliquid.hyperliquid_exchange import HyperliquidExchange
from hummingbot.client.config.client_config_map import ClientConfigMap
from hummingbot.client.config.config_helpers import ClientConfigAdapter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def init_hyperliquid_spot_connector() -> HyperliquidExchange:
    """
    建立一個 Hyperliquid 現貨 connector 實例，用來查餘額 / 下單。
    這版會自動偵測 HyperliquidExchange.__init__ 的參數名稱，
    只塞得進去的東西，避免出現 unexpected keyword argument。
    """

    # 讀 .env
    load_dotenv()
    env = os.environ.copy()

    api_key = env.get("HYPERLIQUID_API_KEY")
    api_secret = env.get("HYPERLIQUID_API_SECRET")
    use_vault_env = env.get("HYPERLIQUID_USE_VAULT", "false").lower()
    use_vault = use_vault_env in ("1", "true", "yes")

    if not api_key or not api_secret:
        raise RuntimeError("請先設定 HYPERLIQUID_API_KEY / HYPERLIQUID_API_SECRET 環境變數")

    # Hummingbot 的 global config map（最小配置就好）
    client_config_map = ClientConfigAdapter(ClientConfigMap())

    # 🔍 讀取 HyperliquidExchange.__init__ 的實際參數列表
    sig = inspect.signature(HyperliquidExchange.__init__)
    params = sig.parameters

    # 預設我們想提供的值（可能不會全用到，看參數名稱）
    candidate_values = {
        "client_config_map": client_config_map,
        "config_map": client_config_map,
        "client_config": client_config_map,

        "hyperliquid_api_key": api_key,
        "api_key": api_key,

        "hyperliquid_api_secret": api_secret,
        "api_secret": api_secret,

        "use_vault": use_vault,
        "trading_pairs": [],      # 只查餘額，不需要實際交易對
        "domain": "",             # 預設主網
    }

    init_kwargs = {}
    for name in params:
        if name == "self":
            continue
        if name in candidate_values:
            init_kwargs[name] = candidate_values[name]

    logger.info(f"🧩 HyperliquidExchange.__init__ 參數 = {list(params.keys())}")
    logger.info(f"🧩 實際會帶入的 kwargs = {init_kwargs}")

    connector = HyperliquidExchange(**init_kwargs)

    # 啟動網路：不同版本方法名字可能不一樣，循序嘗試
    started = False
    start_candidates = ["start_network", "start", "_initialize"]
    for method_name in start_candidates:
        method = getattr(connector, method_name, None)
        if method is None:
            continue

        logger.info(f"🚀 使用 {method_name} 啟動 Hyperliquid connector")
        if inspect.iscoroutinefunction(method):
            await method()
        else:
            method()
        started = True
        break

    if not started:
        logger.warning("⚠️ 找不到啟動 Hyperliquid connector 的方法（start_network/start/_initialize 都不存在）")

    logger.info("✅ Hyperliquid spot connector 已啟動")
    return connector


async def log_hyperliquid_spot_balances(connector: HyperliquidExchange):
    """
    透過 connector 取得現貨資產餘額並印出。
    get_all_balances() 是 ExchangePyBase 的標準介面，回傳 dict[asset, Decimal]
    參考很多官方 strategy / executor 都是這樣拿餘額。:contentReference[oaicite:1]{index=1}
    """
    try:
        balances = connector.get_all_balances()
    except Exception as e:
        logger.exception(f"讀取 Hyperliquid 餘額失敗: {e}")
        return

    if not balances:
        logger.info("💤 Hyperliquid 餘額目前是空的（或尚未同步完成）")
        return

    logger.info("💰 Hyperliquid Spot Balances:")
    for asset, amount in balances.items():
        # 可以視情況 filter 掉 0 或非常小的值
        if amount and amount != 0:
            logger.info(f"  - {asset}: {amount}")


async def strategy_loop():
    """
    Hyperliquid 行情 + 現貨餘額 Hello World：
    - 用 perpetual candles 看 BTC-USDC 1m K 線（跟你原本的一樣）
    - 同時建立 Hyperliquid 現貨 connector
    - 每 5 秒印一次最新一根 K 線
    - 每 30 秒印一次現貨餘額
    """

    perp_connector_name = "hyperliquid_perpetual"
    trading_pair = "BTC-USDC"

    logger.info("🟢 初始化 Hyperliquid perp candles...")
    candles_config = CandlesConfig(
        connector=perp_connector_name,
        trading_pair=trading_pair,
        interval="1m",
        max_records=200,
    )
    candles = CandlesFactory.get_candle(candles_config)
    candles.start()

    # ★ 初始化現貨 connector
    logger.info("🟢 初始化 Hyperliquid spot connector...")
    spot_connector = await init_hyperliquid_spot_connector()

    logger.info("✅ 資料源已啟動，先等幾秒讓 K 線資料進來...")
    await asyncio.sleep(5)

    i = 0
    last_balance_ts = 0

    try:
        while True:
            # 1. 讀取 perp K 線
            try:
                df = candles.candles_df
            except AttributeError:
                logger.warning("⚠️ candles 物件沒有 candles_df 屬性，可能版本介面不同")
                await asyncio.sleep(5)
                continue

            if df is None or df.empty:
                logger.info("⏳ 尚未取得 K 線資料，等一下再試...")
            else:
                last = df.iloc[-1]
                ts = last.get("timestamp")
                open_ = last.get("open")
                high = last.get("high")
                low = last.get("low")
                close = last.get("close")
                volume = last.get("volume")

                logger.info(
                    f"[{i}] {perp_connector_name} {trading_pair} 1m K "
                    f"ts={ts} O={open_} H={high} L={low} C={close} V={volume}"
                )
                i += 1

            # 2. 每 30 秒印一次現貨餘額
            now = asyncio.get_event_loop().time()
            if now - last_balance_ts > 30:
                await log_hyperliquid_spot_balances(spot_connector)
                last_balance_ts = now

            await asyncio.sleep(5)

    finally:
        # 稍微優雅地關閉 network
        try:
            await spot_connector.stop_network()
        except Exception:
            pass
        logger.info("👋 strategy loop 結束，已停止 Hyperliquid spot connector")


def main():
    try:
        asyncio.run(strategy_loop())
    except KeyboardInterrupt:
        logger.info("👋 收到中斷訊號，停止策略...")


if __name__ == "__main__":
    main()
