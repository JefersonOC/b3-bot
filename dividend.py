class Dividend:
    def __init__(self, declared_at, ticker, value, type):
        self.ticker = ticker.upper()
        self.declared_at = declared_at
        self.value = float(value)
        self.type = type

    def __str__(self):
        return self.ticker + " - " + self.declared_at + " - " + self.type + " - " + str(self.value)
