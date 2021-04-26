import logging
import pickle

from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram import ParseMode

from portfolio import Portfolio
from stock import Stock
from stock import StockNotFound
import requests

TOKEN: str = 'TELEGRAM_KEY_HERE'


def start(bot, update):
    """Welcome message."""
    print('Welcome User: ' + str(update.message.chat_id))
    print('Welcome User: ' + str(update.message.chat.first_name))

    bot.send_message(
        chat_id=update.message.chat_id,
        parse_mode=ParseMode.MARKDOWN,
        text="*Olá " + str(update.message.chat.first_name) + "!*\n"
        "\n*Faça o acompanhamento da sua carteira de ativos*\n"

        "\n*Cotação:*\n"
        "/price *[ticker]* - responde com o preço da ação em particular.\n"
        "/dollar - responde com o preço do dólar\n"
        "/euro - responde com o preço do euro\n"
        "/libra - responde com o preço da libra esterlina (british pound)\n"
        "/bitcoin - responde com o preço do bitcoin\n"
        "/ethereum - responde com o preço do ethereum\n"

        "\n*Carteira:*\n"
        "/current - verifica status da carteira.\n"
        "/analytics - analisa sua carteira com alguns indicadores.\n"
        "/dividends - verifica dividendos da carteira.\n"

        "\n*Manutenção da Carteira:*\n"
        "/buy *[quantidade]* *[ticker]* *[preco]* - adiciona ações na carteira.\n"
        "/sell *[quantidade]* *[ticker]* - remove ações na carteira.\n"

        "\n*Aqui temos algumas informações importantes:*\n"
        "/start - menu inicial.\n"
        "/dev - desenvolvedor do bot.\n"
        "/about - sobre o bot.\n"
    )


def price(bot, update, args):
    """Receive a stock code and return the price."""
    if (len(args) <= 0):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"Sua consulta está inválida! Exemplo de uso: */price BBAS3*")
    else:
        stock_code = str(args[0])
        stock = Stock(stock_code)

        if stock.is_valid:
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.MARKDOWN,
                             text=f"*{stock.code}\n{stock.description}*\nPreço Atual: *R${stock.price}*\n"
                             f"Preço Médio (52 sem): *R${((stock.minPriceInYear + stock.maxPriceInYear) / 2):,.2f}*\n"
                             f"ROE: *{stock.return_on_equity}*\n"
                             f"LPA: *{stock.earnings_per_share}*\n"
                             f"M. Líquida: *{stock.net_margin}*\n"
                             f"Score (beta): *{stock.score}*"
                             )
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.MARKDOWN,
                             text=f"O ticker {stock_code} não existe em nosso banco de dados! Exemplo de uso: */price BBAS3*")


def bitcoin(bot, update):
    """return the price of bitcoin."""
    json = requests.get(
        "https://api.biscoint.io/v1/ticker?base=BTC&quote=BRL")
    json = json.json()
    price = json['data']['last']
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text=f"*BTC\nBitcoin*\nPreço Atual: *R${price:,.2f}*")


def ethereum(bot, update):
    """return the price of ethereum."""
    json = requests.get(
        "https://economia.awesomeapi.com.br/all/ETH-BRL")
    json = json.json()
    price = float(json['ETH']['bid'])
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text=f"*ETH\nEthereum*\nPreço Atual: *R${price:,.2f}*")


def dollar(bot, update):
    """return the price of dollar."""
    json = requests.get(
        "https://economia.awesomeapi.com.br/all/USD-BRL")
    json = json.json()
    price = float(json['USD']['bid'])
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text=f"*USD\nDólar Comercial*\nPreço Atual: *R${price:,.2f}*")


def euro(bot, update):
    """return the price of euro."""
    json = requests.get(
        "https://economia.awesomeapi.com.br/all/EUR-BRL")
    json = json.json()
    price = float(json['EUR']['bid'])
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text=f"*EUR\nEuro*\nPreço Atual: *R${price:,.2f}*")


def libra(bot, update):
    """return the price of libra."""
    json = requests.get(
        "https://economia.awesomeapi.com.br/all/GBP-BRL")
    json = json.json()
    price = float(json['GBP']['bid'])
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text=f"*GBP\nLibra Esterlina*\nPreço Atual: *R${price:,.2f}*")


def buy(bot, update, args):
    """Add a new asset to the portfolio."""
    try:
        quantity = int(args[0])
        code = str(args[1]).upper()
        price = float(args[2])

        # If we cannot find the file for this client, we create a new portfolio
        try:
            with open(f'users/{update.message.chat_id}.p', 'r+b') as data_file:
                portfolio = pickle.load(data_file)
        except FileNotFoundError:
            portfolio = Portfolio(client_id=update.message.chat_id)

        portfolio.buy_stock(code=code, quantity=quantity, price=price)

        # Save data to pickle
        with open(f'users/{portfolio.client_id}.p', 'wb') as data_file:
            pickle.dump(portfolio, data_file)

        # Send the updated portfolio
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"*{code}* :: {quantity} :: {price:.2f} adicionada!\n\n"
                              f"TOTAL: "
                              f"{portfolio.stocks[code].quantity} :: "
                              f"{portfolio.stocks[code].code} :: "
                              f"*R${portfolio.stocks[code].avg_price:.2f}*")

    except (ValueError, IndexError):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text="Não foi possível adicionar o ativo a sua carteira! Exemplo de uso: */buy 100 BBAS3 34.00*")
    except StockNotFound as error:
        bot.send_message(chat_id=update.message.chat_id, text=str(error))


def sell(bot, update, args):
    """Remove the specified quantity of the asset that the user want."""
    try:
        quantity = int(args[0])
        code = str(args[1]).upper()

        with open(f'users/{update.message.chat_id}.p', 'r+b') as data_file:
            portfolio = pickle.load(data_file)  # type: Portfolio
        try:
            portfolio.sell_stock(code=code, quantity=quantity)
        except (StockNotFound, ValueError) as error:
            bot.send_message(chat_id=update.message.chat_id, text=str(error))
            return

        bot.send_message(chat_id=update.message.chat_id,
                         text=f"{quantity} - {code} foi vendida.")

        # If after sold, you still have any stock
        if code in portfolio.stocks:
            bot.send_message(
                chat_id=update.message.chat_id,
                parse_mode=ParseMode.MARKDOWN,
                text=f'Agora você tem *{portfolio.stocks[code].quantity}* :: *{portfolio.stocks[code].code}*')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.MARKDOWN,
                             text=f'Agora você tem ZERO - *{code}*')

        with open(f'users/{portfolio.client_id}.p', 'wb') as data_file:
            pickle.dump(portfolio, data_file)

    except (ValueError, IndexError):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text="Não foi possível vender o ativo da sua carteira! Exemplo de uso: */sell 100 BBAS3*")

    except FileNotFoundError:
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text="Você não possui uma carteira ainda! adicione ativos nela pelo comando: */buy 100 BBAS3 34.00*")


def current(bot, update):
    """Show the current entire portfolio value."""
    try:
        with open(f'users/{update.message.chat_id}.p', 'rb') as data_file:
            portfolio = pickle.load(data_file)  # type: Portfolio

        portfolio.update_all_stocks()

        msg = "Carteira de Ativos\n"
        for code, stock in sorted(portfolio.stocks.items(), key=lambda item: item[0]):
            if stock.type == 'stock':
                msg += f"\n*{stock.code}*\n" \
                    f"{stock.description}\n" \
                    f"*{stock.quantity}* :: *R${stock.price:,.2f}*\n" \
                    f"*{stock.change}%* :: R${stock.value:,.2f}\n" \
                    f"R${stock.value - (stock.avg_price * stock.quantity):,.2f} :: R${stock.avg_price * stock.quantity:,.2f} \n"

                print(code + " >> " + msg)
                bot.send_message(chat_id=update.message.chat_id,
                                 parse_mode=ParseMode.MARKDOWN,
                                 text=msg)
                msg = ""

        for code, stock in sorted(portfolio.stocks.items(), key=lambda item: item[0]):
            if stock.type == 'fii':
                msg += f"\n*{stock.code}*\n" \
                    f"{stock.description}\n" \
                    f"*{stock.quantity}* :: *R${stock.price:,.2f}*\n" \
                    f"*{stock.change}%* :: R${stock.value:,.2f}\n" \
                    f"R${stock.value - (stock.avg_price * stock.quantity):,.2f} :: R${stock.avg_price * stock.quantity:,.2f} \n"

                print(code + " >> " + msg)
                bot.send_message(chat_id=update.message.chat_id,
                                 parse_mode=ParseMode.MARKDOWN,
                                 text=msg)
                msg = ""

        msg += f'\nTOTAL:\n' \
            f'*{portfolio.change:.2f}%* :: *R${portfolio.value:,.2f}*'

        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=msg)

    except (FileNotFoundError, ZeroDivisionError, ValueError):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"Você não possui uma carteira ainda! adicione ativos nela pelo comando: */buy 100 BBAS3 34.00*")


def dividends(bot, update):
    """Show the current entire portfolio value."""
    try:
        with open(f'users/{update.message.chat_id}.p', 'rb') as data_file:
            portfolio = pickle.load(data_file)  # type: Portfolio

        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"Estamos recuperando seus dividendos... aguarda um minutinho!")
        portfolio.update_all_dividends()

        msg = "Ano :: 2020\n"
        for code, stock in sorted(portfolio.stocks.items(), key=lambda item: (item[0])):
            msg += f"\n*{code}*\n" \
                f"{stock.description}\n" \
                f"*{stock.quantity}* :: *R${stock.price:,.2f}*\n"
            for dividend in stock.dividends:
                msg += f'{dividend.declared_at} :: *R${dividend.value:,.2f}* :: {dividend.type}\n'

            print(msg)
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode=ParseMode.MARKDOWN,
                             text=msg)
            msg = ""

    except (FileNotFoundError, ZeroDivisionError, ValueError):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"Você não possui uma carteira ainda! adicione ativos nela pelo comando: */buy 100 BBAS3 34.00*")


def analytics(bot, update):
    """Show the abalytics portfolio value."""
    try:
        with open(f'users/{update.message.chat_id}.p', 'rb') as data_file:
            portfolio = pickle.load(data_file)  # type: Portfolio

        portfolio.update_all_stocks()

        msg = "Carteira de Ativos\n"
        for code, stock in sorted(portfolio.stocks.items(), key=lambda item: (item[0])):
            if stock.type == 'stock':
                msg += f"\n*{stock.code}*\n" \
                    f"{stock.description}\n" \
                    f"*{stock.quantity}* :: *R${stock.price:,.2f}*\n" \
                    f"*{stock.change}%* :: R${stock.value:,.2f}\n" \
                    f"R${stock.value - (stock.avg_price * stock.quantity):,.2f} :: R${stock.avg_price * stock.quantity:,.2f} \n" \
                    f"Preço Médio (52 sem): *R${((stock.minPriceInYear + stock.maxPriceInYear) / 2):,.2f}*\n" \
                    f"Preço Médio: *R${stock.avg_price:,.2f}*\n" \
                    f"ROE: *{stock.return_on_equity}*\n" \
                    f"LPA: *{stock.earnings_per_share}*\n" \
                    f"M. Líquida: *{stock.net_margin}*\n" \
                    f"Score (beta): *{stock.score}*\n"

                print(code + " >> " + msg)
                bot.send_message(chat_id=update.message.chat_id,
                                 parse_mode=ParseMode.MARKDOWN,
                                 text=msg)
                msg = ""

        for code, stock in sorted(portfolio.stocks.items(), key=lambda item: (item[0])):
            if stock.type == 'fii':
                msg += f"\n*{stock.code}*\n" \
                    f"{stock.description}\n" \
                    f"*{stock.quantity}* :: *R${stock.price:,.2f}*\n" \
                    f"*{stock.change}%* :: R${stock.value:,.2f}\n" \
                    f"R${stock.value - (stock.avg_price * stock.quantity):,.2f} :: R${stock.avg_price * stock.quantity:,.2f} \n" \
                    f"Preço Médio (52 sem): *R${((stock.minPriceInYear + stock.maxPriceInYear) / 2):,.2f}*\n" \
                    f"Preço Médio: *R${stock.avg_price:,.2f}*\n"

                print(code + " >> " + msg)
                bot.send_message(chat_id=update.message.chat_id,
                                 parse_mode=ParseMode.MARKDOWN,
                                 text=msg)
                msg = ""

        msg += f'\nLegenda:\n' \
            f'*ROE* - Mede a capacidade de agregar valor de uma empresa a partir de seus próprios recursos e do dinheiro de investidores. Se este número estiver acima de 10%, a empresa é considerada como boa e acima de 20% excelente.\n' \
            f'*LPA* - Indica se a empresa é ou não lucrativa. Se este número estiver negativo, a empresa está com margens baixas, acumulando prejuízos.\n' \
            f'*M. Líquida* - Revela a porcentagem de lucro em relação às receitas de uma empresa. Aqui depende do setor que ela está, precisa ser comparado com outras empresas do mesmo segmento.\n'

        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=msg)

    except (FileNotFoundError, ZeroDivisionError, ValueError):
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode=ParseMode.MARKDOWN,
                         text=f"Você não possui uma carteira ainda! adicione ativos nela pelo comando: */buy 100 BBAS3 34.00*")


def dev(bot, update):
    print("Dev Curiosity")
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text="Desenvolvido por: *Jeferson Cruz* \n"
                     "Escrito em *Python* <3\n\n"
                     "*GitHub*: https://github.com/JefersonOC \n"
                     "*BLACKFISH LABS*: https://blackfishlabs.com.br ")


def about(bot, update):
    print("Bot Curiosity")
    bot.send_message(chat_id=update.message.chat_id,
                     parse_mode=ParseMode.MARKDOWN,
                     text="O que é: \n"
                     "Um bot que permite visualizar o desempenho de uma carteira de ativos. \n\n"
                     "Qual a origem dos dados: \n"
                     "Todos os dados são extraídos automaticamente do site da B3. \n\n"
                     "O bot coleta alguma informação: \n"
                     "Nenhum dado da carteira é salvo em texto plano em nossos servidores. \n"
                     "A lista de ativos é armazenada apenas pelo número do usuario do Telegram e encriptada, para que na próxima vez que visitar o bot sua carteira possa ser restaurada. \n\n")


def main():
    """Bot main function."""
    # Setup the logging system
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # Setup the bot updater and dispatcher
    updater = Updater(token=TOKEN, use_context=False)
    dispatcher = updater.dispatcher

    # Add command handler to start function
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("price", price, pass_args=True))
    dispatcher.add_handler(CommandHandler("bitcoin", bitcoin))
    dispatcher.add_handler(CommandHandler("ethereum", ethereum))
    dispatcher.add_handler(CommandHandler("dollar", dollar))
    dispatcher.add_handler(CommandHandler("euro", euro))
    dispatcher.add_handler(CommandHandler("libra", libra))
    dispatcher.add_handler(CommandHandler("buy", buy, pass_args=True))
    dispatcher.add_handler(CommandHandler("sell", sell, pass_args=True))
    dispatcher.add_handler(CommandHandler("current", current))
    dispatcher.add_handler(CommandHandler("analytics", analytics))
    dispatcher.add_handler(CommandHandler("dividends", dividends))
    dispatcher.add_handler(CommandHandler("dev", dev))
    dispatcher.add_handler(CommandHandler("about", about))

    # Start the Bot
    # updater.start_webhook(listen="0.0.0.0",
    #                      port=int(PORT),
    #                      url_path=TOKEN)
    # updater.bot.setWebhook(
    #    'http://domain.com.br/' + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
