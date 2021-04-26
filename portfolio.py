import asyncio

from typing import Dict
from typing import Optional

from stock import Stock
from stock import StockNotFound

from dividend import Dividend


class Portfolio:
    """This class is a portfolio representation which hold assets."""

    def __init__(self, client_id: int, *, stocks: Optional[Dict[str, Stock]] = None):
        if stocks is None:
            stocks = dict()

        self.client_id = client_id
        self.stocks = stocks

    @property
    def value(self) -> float:
        """Value sum of all stocks in portfolio."""
        return sum(stock.value for code, stock in self.stocks.items())

    @property
    def change(self) -> float:
        """Percentage change of portfolio value for the day."""
        return sum(stock.value * stock.change for code, stock in self.stocks.items()) / self.value

    def buy_stock(self, code: str, quantity: int = 0, price: float = 0):
        """Add stocks to the portfolio."""

        stock = Stock(code=code, quantity=quantity, initial_price=price)

        if stock.is_valid:
            if code in self.stocks:
                self.stocks[code] += stock
            else:
                self.stocks[code] = stock
        else:
            raise StockNotFound(
                f"O ticker {stock.code} não foi encontrado no banco de dados, verifique se este código está correto!")

    def sell_stock(self, code: str, quantity: int) -> None:
        """Remove a certain quantity of stocks from the portfolio."""
        if quantity <= 0:
            raise ValueError("Não é possível vender menos de um ativo!")

        if code in self.stocks:
            # Only remove the quantity if this portfolio holds enough of this stock
            if self.stocks[code].quantity >= quantity:
                self.stocks[code].quantity -= quantity
                # Delete the dict entry if the number of stocks reaches zero
                if self.stocks[code].quantity == 0:
                    del self.stocks[code]
            else:
                raise ValueError(
                    "Não é possível vender mais do que você tem!")
        else:
            raise StockNotFound(f'Não há {code} na sua carteira!')

    def update_all_stocks(self):
        """Updates all the stocks from the portfolio asynchronously, speeding the process up in 70%."""
        # Generate a list of tasks to be ran by the loop
        task_list = asyncio.wait([stock.update_task()
                                  for stock_code, stock in self.stocks.items()])
        # Create the loop, run and close
        loop = asyncio.new_event_loop()
        loop.run_until_complete(task_list)
        loop.close()

    def update_all_dividends(self):
        """Updates all the dividends from the portfolio"""
        for code, stock in self.stocks.items():
            print(code)
            loop = asyncio.new_event_loop()
            loop.run_until_complete(stock.update_task_dividends())
            loop.close()
