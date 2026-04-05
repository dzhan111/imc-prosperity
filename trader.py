from datamodel import OrderDepth, UserId, TradingState, Order
from datamodel import OrderDepth, TradingState, Order
from typing import List, Dict


class Trader:

    def bid(self):
        return 1
    

    POSITION_LIMITS = {
        "EMERALDS": 20,
        "TOMATOES": 20,
    }

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        conversions = 0
        traderData = ""

        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            position = state.position.get(product, 0)

            # emeralds are stable -> just market make 
            if product == "EMERALDS":
                limit = self.POSITION_LIMITS[product]

                if order_depth.buy_orders and order_depth.sell_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_ask = min(order_depth.sell_orders.keys())

                    buy_volume = limit - position
                    sell_volume = limit + position
                    
                    bid_price = best_bid + 1
                    ask_price = best_ask - 1

                    # only quote if there is still a valid spread after improving
                    if bid_price < ask_price:
                        quote_size = 5

                        if buy_volume > 0:
                            orders.append(
                                Order(product, bid_price, min(quote_size, buy_volume))
                            )

                        if sell_volume > 0:
                            orders.append(
                                Order(product, ask_price, -min(quote_size, sell_volume))
                            )

                    else:
                        # if spread is too tight, just lean on fair value 10000
                        if best_ask <= 9999 and buy_volume > 0:
                            take_size = min(-order_depth.sell_orders[best_ask], buy_volume)
                            if take_size > 0:
                                orders.append(Order(product, best_ask, take_size))

                        if best_bid >= 10001 and sell_volume > 0:
                            take_size = min(order_depth.buy_orders[best_bid], sell_volume)
                            if take_size > 0:
                                orders.append(Order(product, best_bid, -take_size))

            elif product == "TOMATOES":
                limit = self.POSITION_LIMITS[product]
                FAIR_VALUE = 4995
                THRESHOLD = 3

                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = -order_depth.sell_orders[best_ask]

                    if best_ask < FAIR_VALUE - THRESHOLD:
                        buy_qty = min(best_ask_volume, limit - position)
                        if buy_qty > 0:
                            orders.append(Order(product, best_ask, buy_qty))

                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]

                    if best_bid > FAIR_VALUE + THRESHOLD:
                        sell_qty = min(best_bid_volume, limit + position)
                        if sell_qty > 0:
                            orders.append(Order(product, best_bid, -sell_qty))

            result[product] = orders

        # used for rollign avg
        traderData = "SAMPLE" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData
        