
"""
Melhores Ações com Bons descontos
https://en.wikipedia.org/wiki/Magic_formula_investing

O objetivo aqui é rankear as ações pela formula de greenblat, temos a API do statusinvest aberta que nos fornece os indicadores necessarios.

Existem duas versões da formula, a mais conhecida usa P/L e ROE, que atende a todo tipo
de ação, a outra usa EV/EBIT (Enterprise Value/EBITDA) e ROIC, que não serve para bancos, pois os mesmos nao possuem
ROIC, sendo excluidos automaticamente.

As ações são ordenadas primeiro por P/L, recebendo nota, 
o menor P/L recebe a maior nota(numero total de ações que participam do ranking) 
e o maior P/L recebe 1. 

O mesmo processo é feito para o ROE, sendo que o maior ROE recebe a maior nota. 

A soma das duas notas determina a classificação do ranking.
"""
import requests
import json

def greenblatt(category):
    print("### greenblattApi ###")

    resp = requests.get(
        'https://statusinvest.com.br/category/advancedsearchresult?CategoryType=1&search={"liquidezMediaDiaria":{"Item1":200000,"Item2":null},"valorMercado":{"Item1":50000000,"Item2":null}}')
    stocksJson = json.loads(resp.text)

    param1 = 'p_L'
    param2 = 'roe'
    if category == 'cat2':
        param1 = 'eV_Ebit'
        param2 = 'roic'

    for idx in range(len(stocksJson)-1, -1, -1):
        stock = stocksJson[idx]
        if param1 not in stock or param2 not in stock:
            stocksJson.pop(idx)
            continue
        if int(stock[param1]) <= 0 or int(stock[param2]) <= 0:
            stocksJson.pop(idx)
            continue

    stocksJson.sort(key=lambda x: (x[param1]), reverse=True)
    for idx, stock in enumerate(stocksJson):
        stock[param1 + '_Score'] = idx

    stocksJson.sort(key=lambda x: (x[param2]))
    for idx, stock in enumerate(stocksJson):

        stock[param2 + '_Score'] = idx
        stock['final_Score'] = int(
            stock[param1 + '_Score']) + int(stock[param2 + '_Score'])

        for key in ['companyId', 'price', 'p_VP', 'p_Ebit', 'p_Ativo', 'margemBruta', 'margemEbit', 'margemLiquida',
                    'p_SR', 'p_CapitalGiro', 'p_AtivoCirculante', 'giroAtivos', 'roa',
                    'dividaliquidaPatrimonioLiquido', 'dividaLiquidaEbit', 'pl_Ativo', 'passivo_Ativo',
                    'liquidezCorrente', 'peg_Ratio', 'receitas_Cagr5', 'liquidezMediaDiaria', 'vpa', 'lpa',
                    'valorMercado', 'lucros_Cagr5', 'dy']:
            stock.pop(key, None)

        stock['p_L'] = '%.2f' % round(stock['p_L'], 2)
        stock['eV_Ebit'] = '%.2f' % (
            int(0) if "eV_Ebit" not in stock else round(stock['eV_Ebit'], 2))
        stock['roe'] = '%.2f' % round(stock['roe'], 2)
        stock['roic'] = '%.2f' % (
            int(0) if "roic" not in stock else round(stock['roic'], 2))
            

    stocksJson.sort(key=lambda x: (x["final_Score"]), reverse=True)

    with open("greenblat.json", "w") as outfile:
        outfile.write(json.dumps(stocksJson, indent=4, sort_keys=False))

    return json.dumps(stocksJson, indent=4)

print(greenblatt("cat1"))