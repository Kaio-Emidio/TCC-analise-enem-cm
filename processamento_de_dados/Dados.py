import pandas as pd
import streamlit as st
from processamento_de_dados.Filtrar import Filtrar
from config import Config

class Dados:
    @st.cache_data
    def ler_ano(ano, columns=None):
        caminho_arquivo = f"{Config.PASTA_SAIDA}/MICRODADOS_ENEM_{ano}.parquet"
        df = pd.read_parquet(caminho_arquivo, columns=columns)
        return df

    def estatistica(df):
        disciplinas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação'
        ]
        colunas_enem = disciplinas + ['Geral']

        resultado = {}

        progress_bar = st.progress(0.0)
        status_text = st.empty()
        passo_progresso = 1.0 / len(colunas_enem)
        progresso_atual = 0.0

        for coluna in colunas_enem:
            status_text.text(f"Analisando notas de {coluna}...")
            if coluna == 'Geral':
                media_alunos = df[disciplinas].mean(axis=1)
                
                resultado[coluna] = {
                    'media': float(media_alunos.mean().round(2)),
                    'mediana': float(media_alunos.median()),
                    'desvio_padrao': float(media_alunos.std()),
                }
            elif coluna in df.columns:
                resultado[coluna] = {
                    'media': float(df[coluna].mean().round(2)),
                    'mediana': float(df[coluna].median()),
                    'desvio_padrao': float(df[coluna].std()),
                }

            progresso_atual = min(1.0, progresso_atual + passo_progresso)
            progress_bar.progress(progresso_atual)

        status_text.empty()
        progress_bar.empty()

        return resultado

    def media_materias_por_cidade_ano(cidades: list, anos: list) -> pd.DataFrame:
        colunas_objetivas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
        ]
        colunas_notas = colunas_objetivas + ['Redação']
        colunas_necessarias = colunas_notas + ['Município da Prova']
        
        resultados = []

        for ano in anos:
            df = Dados.ler_ano(ano, columns=colunas_necessarias)
            
            df = Filtrar.filtrar_cidade(cidades, df)

            if df.empty:
                continue

            faltas = df[colunas_objetivas].isna().sum(axis=1)
            df = df[faltas < 2]

            if df.empty:
                continue

            df['Município'] = df['Município da Prova'].map(
                Filtrar.codigo_para_municipio()
            )

            # 1. Agrupa e calcula as médias por município para cada matéria
            medias_por_muni = df.groupby('Município', as_index=False)[colunas_notas].mean()
            
            # 2. Calcula a média geral por município
            medias_por_muni['Geral'] = medias_por_muni[colunas_notas].mean(axis=1)
            medias_por_muni['Ano'] = str(ano)

            resultados.append(medias_por_muni)

        if not resultados:
            colunas_finais = ['Ano', 'Município', 'Geral'] + colunas_notas
            return pd.DataFrame(columns=colunas_finais)

        df_final = pd.concat(resultados, ignore_index=True)
        
        # Arredonda valores para 2 casas decimais
        cols_num = ['Geral'] + colunas_notas
        df_final[cols_num] = df_final[cols_num].round(2)

        return df_final