import re
import time
import sqlite3
import pycountry
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import cm
from IPython.display import display
from sklearn.feature_extraction.text import CountVectorizer
import warnings
warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")


def conecta():
    return sqlite3.connect("C:/Users/Gabriel/Documents/Programação/PythonFundamentos-master/Cap06/Notebooks/imdb.db")

#Função para retornar os genêros


def main(num):
    """conn = conecta()
    tabelas = pd.read_sql_query("SELECT NAME AS 'Table_Name' FROM sqlite_master WHERE type = 'table'", conn)
    #print(type(tabelas))
    print(tabelas.head())
    tabelas = tabelas["Table_Name"]. values.tolist()
    for tabela in tabelas:
        consulta = "PRAGMA TABLE_INFO({})".format(tabela)
        resultado = pd.read_sql_query(consulta, conn)
        print("Esquema da tabela:", tabela)
        display(resultado)
        print("-"*100)
        print("\n")"""
    perguntas = {
        "1": pergunta1,
        "2": pergunta2,
        "3": pergunta3,
        "4": pergunta4,
        "5": pergunta5,
        "6": pergunta6,
        "7": pergunta7,
        "8": pergunta8,
        "9": pergunta9,
        "10": pergunta10,
    }
    perguntas[num]()


def pergunta1():
    # Cria a consulta SQL
    conn = conecta()
    consulta1 = '''SELECT TYPE, count(*) AS COUNT FROM titles GROUP BY type'''

    # Extrai e vizulaliza o resultado
    resultado1 = pd.read_sql_query(consulta1, conn)
    #display(resultado1)
    resultado1['percentual'] = (resultado1['COUNT']/ resultado1['COUNT'].sum())*100

    # Vamos criar um gráfico com apenas 4 categorias:
    # As 3 categorias com mais títulos e 1 categoria com todo o restante

    # Cria um dicionário vazio

    others = {}
    # Filtra o percentual em 5% e soma o total
    others['COUNT'] = resultado1[resultado1['percentual'] < 5]['COUNT'].sum()
    # Grava o percentual
    others['percentual'] = resultado1[resultado1['percentual'] <5]['percentual'].sum()
    # Ajusta o nome
    others['type'] = 'others'
    #print(others)

    # Filtra o dataframe de resultado
    resultado1 = resultado1[resultado1['percentual'] > 5]

    # Append com o dataframe de outras categorias
    resultado1 = resultado1.append(others, ignore_index= True)

    # Ordena o resultado
    resultado1 = resultado1.sort_values(by = 'COUNT', ascending = False)
    #display(resultado1.head())

    # Ajusta os labels
    labels = [str(resultado1['type'][i]) + ' ' + '[' + str(round(resultado1['percentual'][i], 2)) + '%' + ']' for i in
              resultado1.index]

    # Plot
    # Mapa de cores
    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    cs = cm.Set3(np.arange(100))

    # Cria a figura
    f = plt.figure()

    # Pie Plot
    plt.pie(resultado1['COUNT'], labeldistance = 1, radius = 1.5, colors = cs, wedgeprops = dict(width = 0.5))
    plt.legend(labels = labels, loc = 'center', prop = {'size':12})
    plt.title("Distribuição de Títulos", loc = 'Center', fontdict = {'fontsize':20,'fontweight':20})
    plt.show()


def pergunta2():
    # Consulta SQL
    conn = conecta()
    consulta2 = '''SELECT genres, COUNT(*) FROM titles WHERE type = 'movie' GROUP BY genres'''

    # Resultado
    resultado2 = pd.read_sql_query(consulta2, conn)
    display(resultado2)

    # Converte as strings para minúsculo
    resultado2['genres'] = resultado2['genres'].str.lower().values

    # Remove valores NA (ausentes)
    temp = resultado2['genres'].dropna()

    # Vamos criar um vetor usando expressão regular para filtrar as strings
    padrao = '(?u)\\b[\\w-]+\\b'
    vetor = CountVectorizer(token_pattern=padrao, analyzer='word')

    # Aplica a vetorização ao dataset sem valores NA
    bag_generos = vetor.fit_transform(temp)

    # Retorna gêneros únicos
    generos_unicos = vetor.get_feature_names()

    # Cria o dataframe de gêneros
    generos = pd.DataFrame(bag_generos.todense(), columns = generos_unicos, index=temp.index)
    print(generos.info)

    # Drop da coluna n
    generos = generos.drop(columns = 'n', axis = 0)

    # Calcula o percentual
    generos_percentual = 100 * pd.Series(generos.sum()).sort_values(ascending = False) / generos.shape[0]
    generos_percentual.head(10)

    # Plot
    plt.figure(figsize = (16,8))
    sns.barplot(x = generos_percentual.values, y = generos_percentual.index, orient = 'h', palette = "terrain")
    plt.ylabel("Gênero")
    plt.xlabel("\nPercentual de Filmes (%)")
    plt.title("\n Número (Percentual) de Títulos por Gênero\n")
    plt.show()


def pergunta3():
    # Consulta SQL
    conn = conecta()
    consulta3 = '''SELECT rating, genres, ratings.title_id AS RtTitle FROM ratings JOIN titles ON RtTitle = titles.title_id
    WHERE premiered <= 2022 AND type = "movie"'''

    # Resultado
    resultado3 = pd.read_sql_query(consulta3,conn)
    display(resultado3)

    def retorna_generos(df):
        df['genres'] = df['genres'].str.lower().values
        temp = df['genres'].dropna()
        vetor = CountVectorizer(token_pattern='(?u)\\b[\\w-]+\\b', analyzer='word')
        generos_unicos = vetor.fit_transform(temp)
        print(generos_unicos)
        generos_unicos = [genre for genre in generos_unicos if genre.nonzero()]
        return generos_unicos

    generos_unicos = retorna_generos(resultado3)
    print(generos_unicos)

'''
    genero_counts = []
    genero_ratings = []

    for item in generos_unicos:
        consulta = 'SELECT COUNT (rating) FROM ratings JOIN titles ON RtTitle=title_id ' \
                   'WHERE GENRES like '+ '\''+'%'+item+'%'+'\' AND type =\'movie\''
        resultado = pd.read_sql_query(consulta, conn)
        genero_counts.append(resultado.values[0][0])
        consulta = 'SELECT rating FROM ratings JOIN titles ON RtTitle=titles.title_id ' \
                   'WHERE genres LIKE '+ '\''+'%'+item+'%'+'\' AND type=\'movie\''
        resultado = pd.read_sql_query(consulta, conn)
        genero_ratings.append(np.median(resultado['rating']))

    # Prepara o dataframe final
    df_genero_ratings = pd.DataFrame()
    df_genero_ratings['genres'] = generos_unicos
    df_genero_ratings['count'] = genero_counts
    df_genero_ratings['rating'] = genero_ratings

    # Visualiza
    print(df_genero_ratings.head(20))

    # Drop do índice 18 (news)
    # Não queremos essa informação como gênero
    df_genero_ratings = df_genero_ratings.drop(index=18)

    # Ordena o resultado
    df_genero_ratings = df_genero_ratings.sort_values(by = 'rating', ascending = False)

    #Plot

    #Figura
    plt.figure(figsize = (8,5))

    #Barplot
    sns.barplot(y = df_genero_ratings.genres, x = df_genero_ratings.rating, orient = "h")

    #Textos do gráfico
    for i in range(len(df_genero_ratings)):
        plt.text(4.0, i+0.25, str(df_genero_ratings['count'][df_genero_ratings.index[i]]) + "filmes")
        plt.text(df_genero_ratings.rating[df_genero_ratings.index[i]], i + 0.25, round(df_genero_ratings["rating"][df_genero_ratings.index[i]], 2))

    plt.ylabel("Gênero")
    plt.xlabel("Mediana de Avaliação")
    plt.title("\nMediana de Avaliação Por Gênero\n")
    plt.show()
'''

def pergunta4():
    #Consulta SQL
    conn = conecta()
    consulta4 = '''SELECT rating AS Rating, premiered FROM ratings JOIN titles ON ratings.title_id = titles.title_id 
    WHERE premiered <= 2022 AND type = "movie" ORDER  BY  premiered'''

    #Resultado
    resultado4 = pd.read_sql_query(consulta4, conn)
    display(resultado4)

    #Calculamos a mediana ao longo do tempo(anos)
    ratings = []
    for year in set(resultado4['premiere']):
        ratings.append(np.median(resultado4[resultado4['premiered'] == year]['Rating']))
    print(type(ratings))
    print(ratings[1:10])

    #Lista de anos
    anos = list(set(resultado4['premiered']))
    print(anos[1:10])

    #Plot
    plt.figure(figsize = (16,8))
    plt.plot(anos,ratings)
    plt.xlabel('\nAno')
    plt.ylabel('Mediana de Avaliação')
    plt.title('\n Mediana de Avaliação dos Filmes em Relação ao Ano de Estréia\n')
    plt.show()


def pergunta5():
    # Consulta SQL
    conn = conecta()
    consulta5 = '''SELECT genres  FROM  titles'''

    #Resultado
    resultado5 = pd.read_sql_query(consulta5, conn)
    print(display(resultado5))

    # Retorna e vizualiza gêneros únicos
    generos_unicos = retorna_generos(resultado5)
    print(generos_unicos)

    # Agora fazemos a contagem
    genero_count = []
    for item in generos_unicos:
        consulta = 'SELECT COUNT(*) COUNT FROM  titles  WHERE genres ' \
                   'LIKE ' + '\'' + '%' + item + '%' + '\' AND type=\'movie\' AND premiered <= 2022'
        resultado = pd.read_sql_query(consulta, conn)
        genero_count.append(resultado['COUNT'].values[0])

    # Prepara o dataframe
    df_genero_count = pd.DataFrame()
    df_genero_count['genre'] = generos_unicos
    df_genero_count['Count'] = genero_count

    # Calcula os top 5
    df_genero_count = df_genero_count[df_genero_count['genre'] != 'n']
    df_genero_count = df_genero_count.sort_values(by = 'Count', ascending = False)
    top_generos = df_genero_count.head()['genre'].values

    # Plot
    # Figura
    plt.figure(figsize=(16, 8))

    # Loop e Plot
    for item in top_generos:
        consulta = 'SELECT COUNT(*) Number_of_movies, premiered Year FROM  titles  WHERE genres LIKE ' + '\'' + '%' + item + '%' + '\' AND type=\'movie\' AND Year <=2022 GROUP BY Year'
        resultado = pd.read_sql_query(consulta, conn)
        plt.plot(resultado['Year'], resultado['Number_of_movies'])

    plt.xlabel('\nAno')
    plt.ylabel('Número de Filmes Avaliados')
    plt.title('\nNúmero de Filmes Avaliados Por Gênero Em Relação ao Ano de Estréia\n')
    plt.legend(labels=top_generos)
    plt.show()

def pergunta6():
    # Consulta SQL
    conn = conecta()
    consulta6 = '''
            SELECT runtime_minutes Runtime 
            FROM titles 
            WHERE type = 'movie' AND Runtime != 'NaN'
            '''

    # Resultado
    resultado6 = pd.read_sql_query(consulta6, conn)
    print(display(resultado6))

    # Loop para cálculo dos percentis
    for i in range(101):
        val = i
        perc = round(np.percentile(resultado6['Runtime'].values, val), 2)
        print('{} percentil da duração (runtime) é: {}'.format(val,perc))

    # Refazendo a consulta e retornando o filme com maior duração
    consulta6 = '''
                SELECT runtime_minutes Runtime, primary_title
                FROM titles 
                WHERE type = 'movie' AND Runtime != 'NaN'
                ORDER BY Runtime DESC
                LIMIT 10
                '''
    resultado6 = pd.read_sql_query(consulta6, conn)
    print(resultado6)


def pergunta7():
    # Consulta SQL
    conn = conecta()
    consulta7 = '''
            SELECT AVG(runtime_minutes) Runtime, genres 
            FROM titles 
            WHERE type = 'movie'
            AND runtime_minutes != 'NaN'
            GROUP BY genres
            '''

    # Resultado
    resultado7 = pd.read_sql_query(consulta7, conn)

    # Retorna gêneros únicos
    generos_unicos = retorna_generos(resultado7)

    # Visualiza
    print(generos_unicos)

    # Calcula duração por gênero
    genero_runtime = []
    for item in generos_unicos:
        consulta = 'SELECT runtime_minutes Runtime FROM  titles  WHERE genres ' \
                   'LIKE ' + '\'' + '%' + item + '%' + '\' AND type=\'movie\' AND Runtime!=\'NaN\''
        resultado = pd.read_sql_query(consulta, conn)
        genero_runtime.append(np.median(resultado['Runtime']))

    # Prepara o dataframe
    df_genero_runtime = pd.DataFrame()
    df_genero_runtime["genre"] = generos_unicos
    df_genero_runtime["runtime"] = genero_runtime

    # Remove índice 18 (news)
    df_genero_runtime = df_genero_runtime.drop(index=18)

    # Ordena os dados
    df_genero_runtime = df_genero_runtime.sort_values(by='runtime', ascending=False)

    # Plot

    # Tamanho da figura
    plt.figure(figsize=(16, 8))

    # Barplot
    sns.barplot(y=df_genero_runtime.genre, x=df_genero_runtime.runtime, orient="h")

    # Loop
    for i in range(len(df_genero_runtime.index)):
        plt.text(df_genero_runtime.runtime[df_genero_runtime.index[i]],
                 i + 0.25,
                 round(df_genero_runtime["runtime"][df_genero_runtime.index[i]], 2))

    plt.ylabel('Gênero')
    plt.xlabel('\nMediana de Tempo de Duração (Minutos)')
    plt.title('\nRelação Entre Duração e Gênero\n')
    plt.show()


def pergunta8():

    # Consulta SQL
    conn = conecta()
    consulta8 = '''
                SELECT region, COUNT(*) Number_of_movies FROM 
                akas JOIN titles ON 
                akas.title_id = titles.title_id
                WHERE region != 'None'
                AND type = \'movie\'
                GROUP BY region
                '''
    # Resultado
    resultado8 = pd.read_sql_query(consulta8, conn)
    display(resultado8)

    # Shape
    resultado8.shape
    # Número de linhas
    resultado8.shape[0]

    # Listas auxiliares
    nomes_paises = []
    contagem = []

    # Loop para obter o país de acordo com a região
    for i in range(resultado8.shape[0]):
        try:
            coun = resultado8['region'].values[i]
            nomes_paises.append(pycountry.countries.get(alpha_2=coun).name)
            contagem.append(resultado8['Number_of_movies'].values[i])
        except:
            continue

    # Prepara o dataframe
    df_filmes_paises = pd.DataFrame()
    df_filmes_paises['country'] = nomes_paises
    df_filmes_paises['Movie_Count'] = contagem

    # Ordena o resultado
    df_filmes_paises = df_filmes_paises.sort_values(by='Movie_Count', ascending=False)

    # Visualiza
    df_filmes_paises.head(10)

    # Plot

    # Figura
    plt.figure(figsize=(20, 8))

    # Barplot
    sns.barplot(y=df_filmes_paises[:20].country, x=df_filmes_paises[:20].Movie_Count, orient="h")

    # Loop
    for i in range(0, 20):
        plt.text(df_filmes_paises.Movie_Count[df_filmes_paises.index[i]] - 1,
                 i + 0.30,
                 round(df_filmes_paises["Movie_Count"][df_filmes_paises.index[i]], 2))

    plt.ylabel('País')
    plt.xlabel('\nNúmero de Filmes')
    plt.title('\nNúmero de Filmes Produzidos Por País\n')
    plt.show()


def pergunta9():
    conn = conecta()
    consulta9 = '''
                SELECT primary_title AS Movie_Name, genres, rating
                FROM 
                titles JOIN ratings
                ON  titles.title_id = ratings.title_id
                WHERE titles.type = 'movie' AND ratings.votes >= 25000
                ORDER BY rating DESC
                LIMIT 10          
                '''
    top10_melhores_filmes = pd.read_sql_query(consulta9, conn)
    display(top10_melhores_filmes)

def pergunta10():
    conn = conecta()
    consulta10 = '''SELECT primary_title AS Movie_Name, genres, rating FROM titles JOIN ratings \
                ON  titles.title_id = ratings.title_id WHERE titles.type = 'movie' AND ratings.votes >= 25000 \
                ORDER BY rating ASC LIMIT 10'''
    top10_piores_filmes = pd.read_sql_query(consulta10, conn)
    display(top10_piores_filmes)


print("Bem vindo ao IMDB Search")
print("Lista de perguntas: \n")
print(" 1- Quais São as Categorias de Filmes Mais Comuns no IMDB?\n \
2- Qual o Número de Títulos Por Gênero?\n \
3- Qual a Mediana de Avaliação dos Filmes Por Gênero?\n \
4- Qual a Mediana de Avaliação dos Filmes Em Relação ao Ano de Estréia?\n \
5- Qual o Número de Filmes Avaliados Por Gênero Em Relação ao Ano de Estréia?\n \
6- Qual o Filme Com Maior Tempo de Duração? Calcule os Percentis.\n \
7- Qual a Relação Entre Duração e Gênero? \n \
8- Qual o Número de Filmes Produzidos Por País? \n \
9- Quais São os Top 10 Melhores Filmes? \n \
10- Quais São os Top 10 Piores Filmes?\n")
pergunta = input("Digite o número referente a informação desejada\n")
main(pergunta)