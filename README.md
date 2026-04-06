# imc-prosperity


visualizer from discord, you can download logs from

https://prosperity.equirag.com/


the default template for trader.py is linked in 

https://imc-prosperity.notion.site/writing-an-algorithm-in-python


backtester

https://github.com/chrispyroberts/imc-prosperity-4


else:
                        if best_ask <= 9999 and buy_volume > 0:
                            take_size = min(-order_depth.sell_orders[best_ask], buy_volume)
                            if take_size > 0:
                                orders.append(Order(product, best_ask, take_size))

                        if best_bid >= 10001 and sell_volume > 0:
                            take_size = min(order_depth.buy_orders[best_bid], sell_volume)
                            if take_size > 0:
                                orders.append(Order(product, best_bid, -take_size))