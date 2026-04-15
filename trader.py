from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict
import json


class Trader:
    POSITION_LIMITS = {
        "EMERALDS": 80,
        "TOMATOES": 80,
    }

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        conversions = 0

        # load persistent state
        if state.traderData:
            trader_data = json.loads(state.traderData)
        else:
            trader_data = {}

        ALPHA = 0.3
        #default values to make backtester happt
        buy_volume = 0
        sell_volume = 0

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position = state.position.get(product, 0)
            limit = self.POSITION_LIMITS.get(product, 20)

            if not order_depth.buy_orders or not order_depth.sell_orders:
                result[product] = orders
                continue

            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())
            mid = (best_bid + best_ask) / 2

            if product == "EMERALDS":
                buy_volume = limit - position
                sell_volume = limit + position

                bid_price = best_bid + 1
                ask_price = best_ask - 1

                # only place quotes if they do not cross
                if bid_price < ask_price:
                    size = 10

                    if buy_volume > 0:
                        orders.append(Order(product, bid_price, min(size, buy_volume)))

                    if sell_volume > 0:
                        orders.append(Order(product, ask_price, -min(size, sell_volume)))

                else:
                    if best_ask <= 9999 and buy_volume > 0:
                        take_size = min(-order_depth.sell_orders[best_ask], buy_volume)
                        if take_size > 0:
                            orders.append(Order(product, best_ask, take_size))

                    if best_bid >= 10001 and sell_volume > 0:
                        take_size = min(order_depth.buy_orders[best_bid], sell_volume)
                        if take_size > 0:
                            orders.append(Order(product, best_bid, -take_size))

            elif product == "TOMATOES":
                prev_ema = trader_data.get("tomatoes_ema")
                ema = mid if prev_ema is None else ALPHA * mid + (1 - ALPHA) * prev_ema
                trader_data["tomatoes_ema"] = ema

                fair = ema
                market_spread = best_ask - best_bid
                edge = max(1, market_spread // 2)

                inventory_shift = round(position * 0.05)

                bid_price = int(round(fair - edge)) - inventory_shift
                ask_price = int(round(fair + edge)) - inventory_shift

                # take favorable prices first
                if best_ask < fair and buy_volume > 0:
                    take_size = min(-order_depth.sell_orders[best_ask], buy_volume)
                    if take_size > 0:
                        orders.append(Order(product, best_ask, take_size))
                        buy_volume -= take_size

                if best_bid > fair and sell_volume > 0:
                    take_size = min(order_depth.buy_orders[best_bid], sell_volume)
                    if take_size > 0:
                        orders.append(Order(product, best_bid, -take_size))
                        sell_volume -= take_size

                # keep passive quotes passive
                bid_price = min(bid_price, best_ask - 1)
                ask_price = max(ask_price, best_bid + 1)

                if bid_price < ask_price:
                    size = 20
                    if buy_volume > 0:
                        orders.append(Order(product, bid_price, min(size, buy_volume)))
                    if sell_volume > 0:
                        orders.append(Order(product, ask_price, -min(size, sell_volume)))
            result[product] = orders

        traderData = json.dumps(trader_data)
        return result, conversions, traderData