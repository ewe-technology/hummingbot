import asyncio
import logging

from hummingbot.data_feed.candles_feed.candles_factory import CandlesFactory, CandlesConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


async def strategy_loop():
    """
    Hyperliquid 行情 Hello World（不使用 is_ready，而是直接看 candles_df）：
    - 建立 Hyperliquid perpetual 的 1m K 線
    - 啟動後每 5 秒印一次最新一根 K 線
    """

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

    logger.info("✅ Candles 已啟動，先等幾秒讓資料進來...")
    await asyncio.sleep(5)

    i = 0
    while True:
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
                f"[{i}] {connector_name} {trading_pair} 1m K "
                f"ts={ts} O={open_} H={high} L={low} C={close} V={volume}"
            )
            i += 1

        await asyncio.sleep(5)


def main():
    try:
        asyncio.run(strategy_loop())
    except KeyboardInterrupt:
        logger.info("👋 收到中斷訊號，停止策略...")


if __name__ == "__main__":
    main()
