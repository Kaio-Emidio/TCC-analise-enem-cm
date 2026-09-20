import pandas as pd
import streamlit as st
from processamento_de_dados.Filtrar import Filtrar
from config import Config

class Dados:
    def ler_ano(ano):
        caminho_arquivo = f"{Config.PASTA_SAIDA}/MICRODADOS_ENEM_{ano}.parquet"
        df = pd.read_parquet(caminho_arquivo)
        return df

    def estatistica(df):
        colunas_enem = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação',
            'Geral'
        ]

        resultado = {}

        progress_bar = st.sidebar.progress(0)
        status_text = st.sidebar.empty()

        for coluna in colunas_enem:
            status_text.text(f"Analisando notas de {coluna}...")
            if coluna == 'Geral':
                resultado[coluna] = {
                    'media': float(df[['Ciências da Natureza', 'Ciências Humanas', 'Linguagens e Códigos', 'Matemática', 'Redação']].mean(axis=1).mean().round(2)),
                    'mediana': float(df[['Ciências da Natureza', 'Ciências Humanas', 'Linguagens e Códigos', 'Matemática', 'Redação']].mean(axis=1).median()),
                    'desvio_padrao': float(df[['Ciências da Natureza', 'Ciências Humanas', 'Linguagens e Códigos', 'Matemática', 'Redação']].mean(axis=1).std()),
                }
            elif coluna in df.columns:
                resultado[coluna] = {
                    'media': float(df[coluna].mean().round(2)),
                    'mediana': float(df[coluna].median()),
                    'desvio_padrao': float(df[coluna].std()),
                }            
            progress_bar.progress((colunas_enem.index(coluna) + 1) / len(colunas_enem))

        status_text.empty()
        progress_bar.empty()

        return resultado
    
    def media_geral_por_cidade_ano(cidades: list, anos: list):
        colunas_notas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação',
        ]
        resultados = []

        for ano in anos:
            df = Dados.ler_ano(ano)
            df = Filtrar.filtrar_cidade(cidades, df).copy()
            df['Município'] = df['Município da Prova'].map(
                Filtrar.codigo_para_municipio()
            )
            df['Média Geral'] = df[colunas_notas].mean(axis=1)

            resultado_ano = (
                df.groupby('Município', as_index=False)['Média Geral']
                .mean()
                .assign(Ano=str(ano))
            )
            resultados.append(resultado_ano)

        if not resultados:
            return pd.DataFrame(columns=['Ano', 'Município', 'Média Geral'])

        return pd.concat(resultados, ignore_index=True)[
            ['Ano', 'Município', 'Média Geral']
        ]