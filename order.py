class Order:
    def __init__(self, ticker, operation, market_type, title, quantity, price, value, debitcredit):
        self.ticker = ticker
        self.operation = operation
        self.market_type = market_type
        self.title = title
        self.quantity = quantity
        self.price = price
        self.value = value
        self.debitcredit = debitcredit

    def __str__(self):
        return f"Ticker: {self.ticker}, Operation: {self.operation}, Market Type: {self.market_type}, Quantity: {self.quantity}, Price: {self.price}, Value: {self.value}, DebitCredit: {self.debitcredit}"
    
