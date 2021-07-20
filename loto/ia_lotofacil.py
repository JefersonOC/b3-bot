# -*- coding: utf-8 -*-
"""
# Importando bibliotecas
# pip install tensorflow --upgrade --force-reinstall
"""

import random
from unicodedata import normalize
from sklearn.model_selection import train_test_split
from keras.layers import Dense
from keras.models import Sequential
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno
import requests
from bs4 import BeautifulSoup

pd.set_option('display.max_columns', 500)

print('Download HTML')
url = 'http://loterias.caixa.gov.br/wps/portal/loterias/landing/lotofacil/!ut/p/a1/04_Sj9CPykssy0xPLMnMz0vMAfGjzOLNDH0MPAzcDbz8vTxNDRy9_Y2NQ13CDA0sTIEKIoEKnN0dPUzMfQwMDEwsjAw8XZw8XMwtfQ0MPM2I02-AAzgaENIfrh-FqsQ9wBmoxN_FydLAGAgNTKEK8DkRrACPGwpyQyMMMj0VAcySpRM!/dl5/d5/L2dBISEvZ0FBIS9nQSEh/pw/Z7_HGK818G0K85260Q5OIRSC42046/res/id=historicoHTML/c=cacheLevelPage/=/'
target_path = 'd_lotfac.htm'

response = requests.get(url, stream=True)
handle = open(target_path, "wb")
for chunk in response.iter_content(chunk_size=512):
    if chunk:  # filter out keep-alive new chunks
        handle.write(chunk)
handle.close()
# with zipfile.ZipFile(target_path) as zf:
#    zf.extractall()

print('Parser no html extraído')
fileHtml = 'd_lotfac.htm'

print('Read in the file')
with open(fileHtml, 'r', encoding='utf-8') as file:
    filedata = file.read()

print('Replace the target string')
filedata = normalize('NFKD', filedata).encode(
    'ASCII', 'ignore').decode('ASCII')

print('Write the file out again')
with open(fileHtml, 'w') as file:
    file.write(filedata)

print('HTML Normalizado para uso')
f = open(fileHtml, 'r', encoding='utf-8')
table = f.read()

soup = BeautifulSoup(table, 'html.parser')
table = soup.find(name='table')

table_str = str(table)
print('Lendo HTML')
df = pd.read_html(table_str)[0]

print('Check dataset')
df.shape
df.dtypes

print('Transformando dados')
df['data_sorteio_conv'] = df.iloc[:, 1]
df.data_sorteio_conv = pd.to_datetime(df.data_sorteio_conv)

df['day'] = df.data_sorteio_conv.dt.day
df['month'] = df.data_sorteio_conv.dt.month
df['year'] = df.data_sorteio_conv.dt.year

df_ganhadores = df[:]
df_ganhadores.head()

print('Limpando dataset')
print('Gerando Imagem da Visão Geral do Dataframe')
fig = msno.matrix(df=df.iloc[:, 0:df.shape[1]],
                  figsize=(20, 5), color=(0.42, 0.1, 0.05))
fig_copy = fig.get_figure()
fig_copy.savefig('dataframe.png', bbox_inches='tight')

print('Removendo Valores Nulos')
df = df.dropna(subset=['Concurso'])
fig = msno.matrix(df=df.iloc[:, 0:df.shape[1]],
                  figsize=(20, 5), color=(0.42, 0.1, 0.05))
fig_copy = fig.get_figure()
fig_copy.savefig('dataframe_not_null.png', bbox_inches='tight')

print('Analisando dezenas sorteadas')
df.groupby(['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Bola7', 'Bola8', 'Bola9',
           'Bola10', 'Bola11', 'Bola12', 'Bola13', 'Bola14', 'Bola15']).size().sort_values(ascending=False)

print('Dezenas mais sorteadas em todos os jogos')
dezenas = pd.DataFrame(df['Bola1'].tolist() + df['Bola2'].tolist() + df['Bola3'].tolist() + df['Bola4'].tolist() + df['Bola5'].tolist() + df['Bola6'].tolist() + df['Bola7'].tolist() + df['Bola8'].tolist() + df['Bola9'].tolist() + df['Bola10'].tolist() + df['Bola11'].tolist() + df['Bola12'].tolist() +
                       df['Bola13'].tolist() + df['Bola14'].tolist() + df['Bola15'].tolist(), columns=['numeros'])

fig = dezenas['numeros'].value_counts().sort_values(ascending=True).plot(
    kind='barh', title='As quinze dezenas mais sorteadas em todos os jogos', figsize=(10, 5), fontsize=12, legend=True, color='gray')
fig_copy = fig.get_figure()
fig_copy.savefig('dataframe_more.png', bbox_inches='tight')

print('Preparando o dataset para o modelo')
print('Criando dataframe que vamos usar nos modelos')
df_clean = df
index = 0
anterior = ''
for concurso in df['Concurso']:
    if(concurso == anterior):
        df_clean = df_clean.drop(index)
    index += 1
    anterior = concurso

df_clean.shape
df_nn = df_clean[['Bola1', 'Bola2', 'Bola3', 'Bola4', 'Bola5', 'Bola6', 'Bola7', 'Bola8',
                  'Bola9', 'Bola10', 'Bola11', 'Bola12', 'Bola13', 'Bola14', 'Bola15', 'Ganhadores_15_Nmeros']]

df_nn.columns = map(str.lower, df_nn.columns)
df_nn.head(15)

fig = df_nn[df_nn['ganhadores_15_nmeros'] > 1].groupby('ganhadores_15_nmeros')['ganhadores_15_nmeros'].agg(
    'count').plot(kind='bar', figsize=(10, 5), color='gray', fontsize=12)
fig_copy = fig.get_figure()
fig_copy.savefig('dataframe_winner.png', bbox_inches='tight')

df_nn.loc[df_nn['ganhadores_15_nmeros'] > 0, 'ganhadores_15_nmeros'] = 1

fig = df_nn['ganhadores_15_nmeros'].value_counts().plot(
    kind='bar', figsize=(10, 5), color='gray', fontsize=12)
fig_copy = fig.get_figure()
fig_copy.savefig('dataframe_winner_final.png', bbox_inches='tight')

print(df_nn['ganhadores_15_nmeros'].value_counts())

print('Rede neural')
print('Definição do seed para a reproducidade do modelo')
np.random.seed(8)

print('Separando target e classes')
features = df_nn.iloc[:, 0:15]
target = df_nn.iloc[:, 15]

print('Dividindo dataset entre treino e teste')
X_train, X_test, y_train, y_test = train_test_split(
    target, features, test_size=0.33, random_state=8)

print('Criando modelo')
modelo = Sequential()
modelo.add(Dense(10, input_dim=15, activation='relu'))
modelo.add(Dense(12, activation='relu'))
modelo.add(Dense(1, activation='sigmoid'))

print('Compilando o modelo')
modelo.compile(loss='binary_crossentropy',
               optimizer='adam', metrics=['accuracy'])

print('Treinando modelo')
modelo.fit(y_train, X_train, epochs=30, batch_size=10)

print('Validando Modelo')
print('Avaliando modelo')
scores = modelo.evaluate(y_test, X_test)
print("\n")
print(">> Acuracia do modelo")
print("\n%s: %2f%%" % (modelo.metrics_names[1], scores[1]*100))

print('Predict')
print('Teste de probabilidade de um jogo')

numero_sorteio = [[1, 3, 4, 5, 9, 10, 11, 12, 13, 14, 18, 20, 22, 24, 25]]

y_predict = pd.DataFrame(numero_sorteio)
y_predict

predict_class = modelo.predict_classes(y_predict)
print("1 = Tem chance de ganhar / 0 = Não tem chance de ganhar")
print("\n")
print(numero_sorteio)
print("Previsão Modelo: ", predict_class[0][0])

print('Achando a probabilidade')
predict_proba = modelo.predict_proba(y_predict)
print("Probabilidade: ", round((predict_proba[0][0]*100), 2), "%")

print('Gerando numero')
random.seed(25)

probabilidade_boa = 99
probabilidade_atual = 0

print('Gerando lista com as dezenas sorteadas')
dezenas_sorteadas = df_nn[['bola1', 'bola2', 'bola3', 'bola4', 'bola5', 'bola6', 'bola7',
                           'bola8', 'bola9', 'bola10', 'bola11', 'bola12', 'bola13', 'bola14', 'bola15']].values.tolist()

print('Gerar sequencia de numeros até que a probabilidade seja maior ou igual que 99%')
while(probabilidade_atual < probabilidade_boa):
    dezenas = random.sample(range(1, 25), 15)

    # Numero gerado já foi sorteado?
    if not dezenas in dezenas_sorteadas:
        # Valida qual a probabilidade da seguência ser sorteada
        probabilidade_atual = int(modelo.predict(
            pd.DataFrame([dezenas]))[0][0]*100)


print("Probabilidade de {0} % -> Dezenas: {1}"
      .format(probabilidade_atual, sorted(dezenas)))

# Gera sequencia de número
dezenas_random = random.sample(range(1, 25), 15)

# Numero gerado já foi sorteado?
if not dezenas_random in dezenas_sorteadas:
    # Valida qual a probabilidade da seguência ser sorteada
    probabilidade_atual = int(modelo.predict(
        pd.DataFrame([dezenas_random]))[0][0]*100)

print("Probabilidade de {0} % -> Dezenas: {1}"
      .format(probabilidade_atual, sorted(dezenas_random)))

print('Gerando jogos baseando na tendência de que n bolas do jogo anterior se repetem no próximo')
valConcurso = []
valConcurso.append(0)
probabildade_n_bolas_repetidas = []
probabildade_n_bolas_repetidas.append(0)
for n in range(15):
    concurso = []
    counts = []
    anterior = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    arr = []
    nConcurso = 0
    for index, row in df_nn.iterrows():
        nConcurso += 1
        concurso = []
        concurso.append(row['bola1'])
        concurso.append(row['bola2'])
        concurso.append(row['bola3'])
        concurso.append(row['bola4'])
        concurso.append(row['bola5'])
        concurso.append(row['bola6'])
        concurso.append(row['bola7'])
        concurso.append(row['bola8'])
        concurso.append(row['bola9'])
        concurso.append(row['bola10'])
        concurso.append(row['bola11'])
        concurso.append(row['bola12'])
        concurso.append(row['bola13'])
        concurso.append(row['bola14'])
        concurso.append(row['bola15'])
        count = 0
        for x in range(15):
            if np.count_nonzero(concurso == anterior[x]) > 0:
                count += 1
            if count == n:
                arr.append(nConcurso)
                counts.append(count)
                break
        anterior = concurso
    valConcurso.append(arr)
    print('Probabilidade de repetir {0:d} números do jogo anterior: {1:.2f}%'
          .format(n, (len(counts)/df_nn.shape[0])*100))
    print('{} vezes que {} números se repetiram no próximo jogo, em um total de {} jogos'
          .format(len(counts), n, df_nn.shape[0]))
    probabildade_n_bolas_repetidas.append(len(counts))

ax = pd.DataFrame(probabildade_n_bolas_repetidas, columns=['Valor']).plot(
    kind='bar', title='Quantidade de números repetidos do jogo anterior', figsize=(15, 5), fontsize=12, legend=True, color='gray')
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x()
                * 1.005, p.get_height() * 1.005))

fig_copy = ax.get_figure()
fig_copy.savefig('dataframe_repeat_num.png', bbox_inches='tight')

"""Aqui podemos analisar quais concursos tiveram repetição de "num_bolas" do concurso anterior. Podemos inferir probabilidades disso ocorrer novamente no futuro."""
num_bolas = 6
print(valConcurso[num_bolas])

ultimo_sorteio = sorted(anterior)
allFinal = []
jogos = 20
jogo_ok = False
print("####################################################################")
print("################        Dicas para concurso nº      ################")
print("################               {0}                 ################"
      .format(df_nn.shape[0]+1))
print("####################################################################")
print("")
print("Concurso anterior: ", ultimo_sorteio)
print("")
for x in range(jogos):
    indexes = random.sample(range(0, 15), num_bolas)
    valores = [ultimo_sorteio[i] for i in indexes]
    final = valores.copy()
    indexes = random.sample(range(0, 15), 15)
    for index in indexes:
        if not dezenas[index] in valores and not dezenas[index] in ultimo_sorteio:
            final.append(dezenas[index])
        if(len(final) == 15):
            break
    if len(final) < 15:
        valor_faltando = 15 - len(final)
        while valor_faltando:
            valor_aleatorio = random.sample(range(1, 25), 1)[0]
            if not valor_aleatorio in valores and not valor_aleatorio in final and not valor_aleatorio in ultimo_sorteio:
                final.append(valor_aleatorio)
                valor_faltando -= 1

        jogo_ok = True
    elif final in dezenas_sorteadas:
        print('Já sorteado')
    if jogo_ok:
        probabilidade_atual = int(modelo.predict(
            pd.DataFrame([final]))[0][0]*100)
        allFinal.append(sorted(final))
        print("{0} % -> {1} || Números do concurso anterior: {2}"
              .format(probabilidade_atual, sorted(final), sorted(valores)))
