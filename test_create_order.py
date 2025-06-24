import uuid
from src.bot.trading_bot import TradingBot

if __name__ == "__main__":
    bot = TradingBot(trading_pair="BTCUSDT", interval="5")
    orderLinkId = uuid.uuid4().hex
    params = {
        "category": "spot",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "positionIdx": 0,
        "orderType": "Limit",
        "qty": "0.001",
        "price": "10000",
        "timeInForce": "GTC",
        "orderLinkId": orderLinkId
    }
    endpoint = "/v5/order/create"
    method = "POST"
    print(f"Placing order with params: {params}")
    response = bot.HTTP_Request(endpoint, method, params, "Create")
    print(f"Order response: {response.text}") 