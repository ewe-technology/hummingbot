# scripts/hyperliquid_candles_balance_positions.py
from typing import Dict, Set
from decimal import Decimal
from hummingbot.strategy.script_strategy_base import ScriptStrategyBase
from hummingbot.data_feed.candles_feed.candles_factory import CandlesFactory, CandlesConfig
import pandas as pd


class HyperliquidCandlesBalancePositions(ScriptStrategyBase):
    # 必須定義 markets 才能讓 Hummingbot 創建 connector
    # 格式: {"交易所名稱": {"交易對1", "交易對2", ...}}
    markets: Dict[str, Set[str]] = {
        "hyperliquid_perpetual": {"BTC-USD"},  # 注意：Hyperliquid 使用 BTC-USD 而非 BTC-USDC
    }

    # K 線配置
    candles_config = CandlesConfig(
        connector="hyperliquid_perpetual",
        trading_pair="BTC-USD",  # 改為 BTC-USD
        interval="1m",
        max_records=200,
    )
    candles = CandlesFactory.get_candle(candles_config)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 如果要 debugpy，在這裡放
        # import debugpy
        # debugpy.listen(("0.0.0.0", 5678))
        # debugpy.wait_for_client()

        self.candles.start()
        self._last_log_ts = 0
        self._log_interval = 5  # 每 5 秒運行一次
        self._connector_ready_logged = False
        self._ready_wait_count = 0

    def on_tick(self):
        """
        每 tick_size 秒（預設 1 秒）會被呼叫一次。
        """
        now = self.current_timestamp

        # 檢查 connector 是否存在
        perp_connector = self.connectors.get("hyperliquid_perpetual")

        if perp_connector is None:
            if now - self._last_log_ts >= 5:
                self.logger().warning("⚠️ hyperliquid_perpetual connector 不存在")
                self.logger().info(f"可用的 connectors: {list(self.connectors.keys())}")
                self.logger().info("請確認：")
                self.logger().info("  1. Gateway 是否在運行中")
                self.logger().info("  2. Hyperliquid API 是否已配置")
                self.logger().info("  3. 使用 'gateway connect hyperliquid_perpetual' 連接")
                self._last_log_ts = now
            return

        # 檢查 connector 是否就緒
        if not perp_connector.ready:
            if now - self._last_log_ts >= 5:
                self._ready_wait_count += 1
                self.logger().info(f"⏳ 等待 connector 就緒... (已等待 {self._ready_wait_count * 5} 秒)")
                self.logger().info(f"   Connector 類型: {type(perp_connector).__name__}")
                self._last_log_ts = now
            return

        # Connector 就緒
        if not self._connector_ready_logged:
            self.logger().info("=" * 80)
            self.logger().info("✅ hyperliquid_perpetual connector 已就緒！")
            self.logger().info("=" * 80)
            self._connector_ready_logged = True

        # 每隔指定時間執行一次
        if now - self._last_log_ts >= self._log_interval:
            self.logger().info("=" * 80)
            self.logger().info(f"📊 策略運行 Tick - {pd.Timestamp.now()}")
            self.logger().info("=" * 80)

            self._log_candle()
            self._log_account_balance()
            self._log_account_positions()
            self._log_open_orders()
            self._log_market_price()

            self._last_log_ts = now

    # ========= 1. K 線資訊 =========
    def _log_candle(self):
        """獲取並顯示 K 線資訊"""
        try:
            df = getattr(self.candles, "candles_df", None)

            if df is None or df.empty:
                self.logger().info("📈 [K線] 尚未取得資料")
                return

            if "timestamp" in df.columns:
                df = df.copy()
                df["ts_readable"] = pd.to_datetime(df["timestamp"], unit="ms")

            last = df.iloc[-1]
            self.logger().info(
                f"📈 [K線] BTC-USD 1m | "
                f"時間={last.get('ts_readable', '')} | "
                f"開={last.get('open'):.2f} | "
                f"高={last.get('high'):.2f} | "
                f"低={last.get('low'):.2f} | "
                f"收={last.get('close'):.2f} | "
                f"量={last.get('volume'):.4f}"
            )
        except Exception as e:
            self.logger().error(f"📈 [K線] 錯誤: {e}")

    # ========= 2. 帳戶餘額 =========
    def _log_account_balance(self):
        """獲取並顯示帳戶餘額"""
        perp_connector = self.connectors.get("hyperliquid_perpetual")
        if perp_connector is None or not perp_connector.ready:
            return

        self.logger().info("-" * 80)
        self.logger().info("💰 [帳戶餘額]")

        try:
            balances = None

            # 嘗試多種方法
            if hasattr(perp_connector, "get_all_balances"):
                balances = perp_connector.get_all_balances()
            elif hasattr(perp_connector, "_account_balances"):
                balances = perp_connector._account_balances
            elif hasattr(perp_connector, "available_balances"):
                balances = perp_connector.available_balances

            if balances and len(balances) > 0:
                for asset, balance in balances.items():
                    self.logger().info(f"  • {asset}: {balance}")
            else:
                self.logger().info("  • 無餘額資料")

        except Exception as e:
            self.logger().error(f"  ❌ 錯誤: {e}")

    # ========= 3. 當前倉位 =========
    def _log_account_positions(self):
        """獲取並顯示當前持倉"""
        perp_connector = self.connectors.get("hyperliquid_perpetual")
        if perp_connector is None or not perp_connector.ready:
            return

        self.logger().info("-" * 80)
        self.logger().info("📌 [當前倉位]")

        try:
            positions = None

            if hasattr(perp_connector, "account_positions"):
                positions = perp_connector.account_positions
            elif hasattr(perp_connector, "_account_positions"):
                positions = perp_connector._account_positions

            if not positions or len(positions) == 0:
                self.logger().info("  • 目前沒有持倉")
            else:
                for trading_pair, position in positions.items():
                    if isinstance(position, dict):
                        amount = position.get("amount", 0)
                        entry_price = position.get("entry_price", 0)
                        unrealized_pnl = position.get("unrealized_pnl", 0)
                        leverage = position.get("leverage", 1)

                        self.logger().info(
                            f"  • {trading_pair}: "
                            f"數量={amount} | "
                            f"開倉價={entry_price} | "
                            f"未實現盈虧={unrealized_pnl} | "
                            f"槓桿={leverage}x"
                        )
                    else:
                        self.logger().info(f"  • {trading_pair}: {position}")

        except Exception as e:
            self.logger().error(f"  ❌ 錯誤: {e}")

    # ========= 4. 當前掛單 =========
    def _log_open_orders(self):
        """獲取並顯示當前掛單"""
        perp_connector = self.connectors.get("hyperliquid_perpetual")
        if perp_connector is None or not perp_connector.ready:
            return

        self.logger().info("-" * 80)
        self.logger().info("📋 [當前掛單]")

        try:
            orders = None

            if hasattr(perp_connector, "in_flight_orders"):
                orders = perp_connector.in_flight_orders
            elif hasattr(perp_connector, "_in_flight_orders"):
                orders_dict = perp_connector._in_flight_orders
                if orders_dict:
                    orders = list(orders_dict.values())

            if not orders or len(orders) == 0:
                self.logger().info("  • 目前沒有掛單")
            else:
                for order in orders:
                    if hasattr(order, "trading_pair"):
                        self.logger().info(
                            f"  • {order.trading_pair} | "
                            f"{order.order_type.name} | "
                            f"{order.trade_type.name} | "
                            f"價格={order.price} | "
                            f"數量={order.amount}"
                        )
                    else:
                        self.logger().info(f"  • {order}")

        except Exception as e:
            self.logger().error(f"  ❌ 錯誤: {e}")

    # ========= 5. 市場價格 =========
    def _log_market_price(self):
        """獲取並顯示市場價格"""
        perp_connector = self.connectors.get("hyperliquid_perpetual")
        if perp_connector is None or not perp_connector.ready:
            return

        self.logger().info("-" * 80)
        self.logger().info("💹 [市場價格 - BTC-USD]")

        trading_pair = "BTC-USD"

        try:
            # 方法 1: 獲取訂單簿
            best_bid = None
            best_ask = None

            if hasattr(perp_connector, "get_order_book"):
                try:
                    order_book = perp_connector.get_order_book(trading_pair)
                    if order_book and hasattr(order_book, "snapshot"):
                        bids, asks = order_book.snapshot
                        if len(bids) > 0:
                            best_bid = float(bids[0][0])
                        if len(asks) > 0:
                            best_ask = float(asks[0][0])
                except Exception as e:
                    self.logger().debug(f"訂單簿獲取失敗: {e}")

            # 方法 2: 獲取最新價格
            last_price = None
            if hasattr(perp_connector, "get_price"):
                try:
                    last_price = perp_connector.get_price(trading_pair)
                except:
                    pass

            if not last_price and hasattr(perp_connector, "get_mid_price"):
                try:
                    last_price = perp_connector.get_mid_price(trading_pair)
                except:
                    pass

            # 顯示結果
            if best_bid:
                self.logger().info(f"  • 買一價: ${best_bid:,.2f}")
            if best_ask:
                self.logger().info(f"  • 賣一價: ${best_ask:,.2f}")
            if last_price:
                self.logger().info(f"  • 最新價: ${last_price:,.2f}")

            if best_bid and best_ask:
                spread = best_ask - best_bid
                spread_pct = (spread / best_bid) * 100
                self.logger().info(f"  • 價差: ${spread:.2f} ({spread_pct:.4f}%)")

            if not any([best_bid, best_ask, last_price]):
                self.logger().info("  • 無法獲取價格資料")

        except Exception as e:
            self.logger().error(f"  ❌ 錯誤: {e}")

    def on_stop(self):
        """策略停止時的清理工作"""
        if self.candles:
            self.candles.stop()
        self.logger().info("✋ 策略已停止")