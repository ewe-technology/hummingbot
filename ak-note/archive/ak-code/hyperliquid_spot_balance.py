"""
簡化版本: 拿掉即時行情websocket  但是他的connector就是一定會接上這個  所以還是卡死在connector沒辦法正確建立連線

"""

import asyncio
import inspect
import logging
import os

from dotenv import load_dotenv

from hummingbot.client.config.client_config_map import ClientConfigMap
from hummingbot.client.config.config_helpers import ClientConfigAdapter
from hummingbot.connector.exchange.hyperliquid.hyperliquid_exchange import HyperliquidExchange

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def init_hyperliquid_spot_connector() -> HyperliquidExchange:
    """
    建立一個 Hyperliquid 現貨 connector 實例，用來查餘額。
    一定是用 Hummingbot 的 HyperliquidExchange。

    這版會自動讀 HyperliquidExchange.__init__ 的參數名稱，
    只傳入「它真的有的參數」，避免 unexpected keyword argument。
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

    # 🔑 這邊很重要：
    # HYPERLIQUID_API_KEY  = 你的 Hyperliquid 錢包地址 (0x 開頭)
    # HYPERLIQUID_API_SECRET = 對應那個錢包的私鑰 (32 bytes, 64 hex，通常也是 0x 開頭的長字串)
    # 如果長度錯誤，會出現之前那個「private key length」的錯誤

    client_config_map = ClientConfigAdapter(ClientConfigMap())

    # 🔍 讀取 HyperliquidExchange.__init__ 的實際參數列表
    sig = inspect.signature(HyperliquidExchange.__init__)
    params = sig.parameters

    # 我們「想」提供的候選值（不一定都用得到）
    candidate_values = {
        # config 類參數
        "client_config_map": client_config_map,
        "config_map": client_config_map,
        "client_config": client_config_map,

        # API key / secret 類參數
        "hyperliquid_api_key": api_key,
        "api_key": api_key,

        "hyperliquid_api_secret": api_secret,
        "api_secret": api_secret,

        # 其他常見參數
        "use_vault": use_vault,
        "trading_pairs": [],   # 只查餘額不用指定 trading_pairs
        "domain": "",          # 預設主網 domain
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

    # 啟動 connector 的網路邏輯（不同版本方法名字可能不同）
    started = False
    start_candidates = ["start_network", "start", "_initialize"]
    for method_name in start_candidates:
        method = getattr(connector, method_name, None)
        if method is None:
            continue

        logger.info(f"🚀 使用 {method_name} 啟動 Hyperliquid spot connector")
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
    get_all_balances() 是 ExchangePyBase 標準介面，回傳 dict[asset, Decimal]
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
        if amount and amount != 0:
            logger.info(f"  - {asset}: {amount}")


async def main_async():
    # 只初始化「現貨 connector」，不建立任何 candles / perpetual
    logger.info("🟢 初始化 Hyperliquid spot connector...")
    connector = await init_hyperliquid_spot_connector()

    try:
        # 每 30 秒印一次餘額
        while True:
            await log_hyperliquid_spot_balances(connector)
            await asyncio.sleep(30)
    finally:
        # 有的版本有 stop_network，如果沒有可以拿掉
        try:
            await connector.stop_network()
        except Exception:
            pass


def main():
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("👋 收到中斷訊號，停止程式...")


if __name__ == "__main__":
    main()
