import pandas as pd
import streamlit as st
from fastparquet import ParquetFile
from processamento_de_dados.Filtrar import Filtrar
from config import Config

class Dados:
    @staticmethod
    def filtrar_alunos_por_notas_objetivas(df: pd.DataFrame) -> pd.DataFrame:
        colunas_objetivas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
        ]
        zeros_por_aluno = df[colunas_objetivas].eq(0).sum(axis=1)
        return df.loc[zeros_por_aluno < 2].copy()

    @staticmethod
    def tratar_zeros_redacao_como_ausentes(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if 'Redação' in df.columns:
            df['Redação'] = df['Redação'].mask(df['Redação'].eq(0))
        return df

    @staticmethod
    def ler_ano(ano, columns=None):
        caminho_arquivo = Config.PASTA_SAIDA / f"MICRODADOS_ENEM_{ano}.parquet"
        if not caminho_arquivo.exists():
            raise FileNotFoundError(
                f"Dados do ENEM de {ano} não encontrados em '{caminho_arquivo}'. "
                "Coloque o CSV correspondente em 'microdados_brutos' e reinicie o app."
            )

        if columns is None:
            return pd.read_parquet(caminho_arquivo)

        colunas_parquet = set(ParquetFile(str(caminho_arquivo)).columns)
        colunas_ausentes = set(columns) - colunas_parquet
        coluna_rede = 'Dependência administrativa'
        colunas_ausentes_obrigatorias = colunas_ausentes - {coluna_rede}
        if colunas_ausentes_obrigatorias:
            raise ValueError(
                f"Colunas ausentes no Parquet de {ano}: "
                f"{', '.join(sorted(colunas_ausentes_obrigatorias))}"
            )

        colunas_disponiveis = [
            coluna for coluna in columns if coluna in colunas_parquet
        ]
        df = pd.read_parquet(caminho_arquivo, columns=colunas_disponiveis)
        if coluna_rede in colunas_ausentes:
            df[coluna_rede] = float('nan')
            print(
                f"Aviso: o Parquet de {ano} não contém a dependência da escola; "
                "contagens por rede indisponíveis."
            )
        return df

    @staticmethod
    def estatistica(df):
        df = Dados.filtrar_alunos_por_notas_objetivas(df)
        df = Dados.tratar_zeros_redacao_como_ausentes(df)
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

    @staticmethod
    @st.cache_data
    def medias_por_municipio(cidades: list, ano: int) -> pd.DataFrame:
        colunas_notas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação',
        ]
        colunas_necessarias = colunas_notas + ['Município da Prova']
        df = Dados.ler_ano(ano, columns=colunas_necessarias)
        df = Filtrar.filtrar_cidade(cidades, df)
        df = Dados.filtrar_alunos_por_notas_objetivas(df)
        df = Dados.tratar_zeros_redacao_como_ausentes(df)
        df['Município'] = df['Município da Prova'].map(
            Filtrar.codigo_para_municipio()
        )

        return df.groupby('Município', as_index=False)[colunas_notas].mean()

    @staticmethod
    def media_materias_por_cidade_ano(cidades: list, anos: list) -> pd.DataFrame:
        colunas_objetivas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
        ]
        colunas_notas = colunas_objetivas + ['Redação']
        colunas_contagem = list(Config.COLUNAS_CONTAGEM_REDE.values())
        colunas_necessarias = (
            colunas_notas
            + ['Município da Prova', 'Dependência administrativa']
        )
        
        resultados = []

        for ano in anos:
            caminho_arquivo = (
                Config.PASTA_SAIDA / f"MICRODADOS_ENEM_{ano}.parquet"
            )
            if not caminho_arquivo.exists():
                continue

            df = Dados.ler_ano(ano, columns=colunas_necessarias)
            
            df = Filtrar.filtrar_cidade(cidades, df)

            if df.empty:
                continue

            df['Município'] = df['Município da Prova'].map(
                Filtrar.codigo_para_municipio()
            )

            dependencias = pd.to_numeric(
                df['Dependência administrativa'],
                errors='coerce',
            ).map(Config.DEPENDENCIAS_ESCOLA)
            contagens_por_muni = (
                df.assign(_rede_escolar=dependencias)
                .dropna(subset=['_rede_escolar'])
                .groupby(['Município', '_rede_escolar'])
                .size()
                .unstack(fill_value=0)
                .reindex(
                    index=df['Município'].dropna().unique(),
                    columns=list(Config.DEPENDENCIAS_ESCOLA.values()),
                    fill_value=0,
                )
            )
            colunas_contagem_por_nome = {
                nome: Config.COLUNAS_CONTAGEM_REDE[codigo]
                for codigo, nome in Config.DEPENDENCIAS_ESCOLA.items()
            }
            contagens_por_muni = contagens_por_muni.rename(
                columns=colunas_contagem_por_nome
            )
            possui_dependencias = (
                dependencias.notna()
                .groupby(df['Município'])
                .any()
            )
            contagens_por_muni.loc[
                ~possui_dependencias.reindex(contagens_por_muni.index, fill_value=False),
                colunas_contagem,
            ] = float('nan')
            contagens_por_muni = contagens_por_muni.reset_index()

            df_notas = Dados.filtrar_alunos_por_notas_objetivas(df)
            df_notas = Dados.tratar_zeros_redacao_como_ausentes(df_notas)
            faltas = df_notas[colunas_objetivas].isna().sum(axis=1)
            df_notas = df_notas[faltas < 2]

            medias_por_muni = df_notas.groupby(
                'Município',
                as_index=False,
            )[colunas_notas].mean()
            medias_por_muni['Geral'] = medias_por_muni[colunas_notas].mean(axis=1)

            resultado_ano = medias_por_muni.merge(
                contagens_por_muni,
                on='Município',
                how='outer',
            )
            resultado_ano['Ano'] = str(ano)
            resultados.append(resultado_ano)
            del df, df_notas, dependencias

        if not resultados:
            colunas_finais = (
                ['Ano', 'Município', 'Geral']
                + colunas_notas
                + colunas_contagem
            )
            return pd.DataFrame(columns=colunas_finais)

        df_final = pd.concat(resultados, ignore_index=True)
        
        # Arredonda valores para 2 casas decimais
        cols_num = ['Geral'] + colunas_notas
        df_final[cols_num] = df_final[cols_num].round(2)

        return df_final