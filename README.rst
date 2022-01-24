Welcome to candlestick_symphony - Futures trade bot
=================================

This is Python wrapper for the `Binance Futures`. I am in no way affiliated with Binance, use at your own risk.

For use this you need:
  - Python 3.8.10 
  - Ubuntu 20.04 
  - pip 20.0.2 
  - or other specifications



 
 
 




.. code:: python

    # How it works...
    # After start candlestick_symphony.py
    # Check for signal doji star  # search_doji()
    if Signal == SUCCESS:
    
    # CALCULATION_POSITION  # calculate_summ_order_in():
    balance = 20  # USDT
    balance = balance * leverage_trade / symbol_trade_price
    market_position_summ = balance / 2  # for LONG or SHORT
    market_position_summ -= market_position_summ / 10 # for SL buffer
    market_position_summ = market_position_summ / 2  # for 1 market order
    limit_average_position_summ = market_position_summ / 2  # for 2 limit order
    
    # PLACE_ORDER
    For LONG Place 1 market BUY, 2 limit BUY, 4 limit SELL and 4 limit SELL if limit BUY success  # place_doji_long()
    For SHORT Place 1 market SELL, 2 limit SELL, 4 limit BUY and 4 limit BUY if limit SELL success  # place_doji_short()
    Place SL and TP

- Will work automatically and trade in Futures Hedge mode
- This version is only for timeframe = 15m, leverage = 10 and symbol whose price is floating point(0.***)
