from itertools import combinations


def filterResults(gameDefinition):
    attrs = vars(gameDefinition)
    print(attrs)
    games = list(combinations(gameDefinition.finalNumbers, 15))
    print('Total de jogos possiveis: ' + str(len(games)))

    for game in reversed(games):
        # count numbers in the list which are greater than X
        count = len([elem for elem in game if elem % 2 == 0])
        if(count != gameDefinition.pairs):
            games.remove(game)
            continue

        count = len([elem for elem in game if elem % 3 == 0])
        if(count != gameDefinition.multipleThree):
            games.remove(game)
            continue

        count = len([elem for elem in game if elem in PRIME])
        if(count != gameDefinition.prime):
            games.remove(game)
            continue

        count = len([elem for elem in game if elem in FIBONACCI])
        if(count != gameDefinition.fibonacci):
            games.remove(game)
            continue

        count = sum(game)
        if(count > gameDefinition.maxValue or count < gameDefinition.minValue):
            games.remove(game)
            continue

    for game in games:
        print(*game)
    print('Resultados gerados ' + str(len(games)))


class GameDefinition:
    def __init__(self, pairs, prime, multipleThree, fibonacci, maxValue, minValue):
        self.pairs = pairs
        self.prime = prime
        self.multipleThree = multipleThree
        self.fibonacci = fibonacci
        self.maxValue = maxValue
        self.minValue = minValue
        self.finalNumbers = []


FIBONACCI = [1, 2, 3, 5, 8, 13, 21]
PRIME = [2, 3, 5, 7, 11, 13, 17, 19, 23]
ALL_POSSIBILITIES = [1, 2, 3, 4, 5, 6, 7, 8, 9,
                     10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]


opcoesDefault = input("Utilizar opcoes default? [s/n] ")
gameDefinition = None

if(opcoesDefault.strip().lower() == 's'):
    gameDefinition = GameDefinition(7, 5, 5, 4, 200, 180)
else:
    pares = input("Digite a quantidade de numeros pares que deseja: ")
    primos = input("Digite a quantidade de numeros primos: ")
    multiploTres = input("Digite a quantidade de multiplos de 3: ")
    fibonacci = input("Digite a quantidade de numeros de fibonacci: ")
    valorMaximo = input(
        "Digite a o valor maximo esperado da soma das dezenas: ")
    valorMinimo = input(
        "Digite a o valor minimo esperado da soma das dezenas: ")
    gameDefinition = GameDefinition(
        pares, primos, multiploTres, fibonacci, valorMaximo, valorMinimo)

# capturar 5 numeros que menos sairam no geral (https://www.lotoloto.com.br/lotofacil/)
removedNumbers = input(
    "Digite os numeros que deseja remover separados por virgulas (5 a 7): ")
removedNumbers = list((int(x) for x in removedNumbers.split(',')))
gameDefinition.finalNumbers = [
    i for i in ALL_POSSIBILITIES if i not in removedNumbers]

filterResults(gameDefinition)
