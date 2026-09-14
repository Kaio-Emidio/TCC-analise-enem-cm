import pandas as pd
from pathlib import Path

pasta_entrada = Path("microdados_brutos")
pasta_saida = Path("microdados_filtrados")

pasta_entrada.mkdir(parents=True, exist_ok=True)
pasta_saida.mkdir(parents=True, exist_ok=True)

for arquivo in pasta_entrada.glob("*.csv"):
    tabela_int = pd.read_csv(arquivo, encoding='latin-1', delimiter=';')

    colunas_de_interesse = ['CO_MUNICIPIO_PROVA','NU_NOTA_CN','NU_NOTA_CH','NU_NOTA_LC','NU_NOTA_MT','NU_NOTA_REDACAO']
    novos_nomes = {
        'NU_NOTA_CN': 'Ciências da Natureza',
        'NU_NOTA_CH': 'Ciências Humanas',
        'NU_NOTA_LC': 'Linguagens e Códigos',
        'NU_NOTA_MT': 'Matemática',
        'NU_NOTA_REDACAO': 'Redação',
        'CO_MUNICIPIO_PROVA': 'Município da Prova'
    }

    tabela_filtrada = tabela_int[colunas_de_interesse]

    tabela_filtrada.rename(inplace=True, columns=novos_nomes)

    caminho_final = pasta_saida / arquivo.name
    tabela_filtrada.to_csv(caminho_final, sep=';', index=False, encoding='utf-8-sig')

