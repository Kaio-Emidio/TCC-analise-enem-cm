import math

import numpy as np
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
        return df.loc[zeros_por_aluno < 2]

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
    def iterar_ano(ano, columns):
        caminho_arquivo = Config.PASTA_SAIDA / f"MICRODADOS_ENEM_{ano}.parquet"
        if not caminho_arquivo.exists():
            raise FileNotFoundError(
                f"Dados do ENEM de {ano} não encontrados em '{caminho_arquivo}'. "
                "Coloque o CSV correspondente em 'microdados_brutos' e reinicie o app."
            )

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
        arquivo = ParquetFile(str(caminho_arquivo))
        for bloco in arquivo.iter_row_groups(columns=colunas_disponiveis):
            if coluna_rede in colunas_ausentes:
                bloco[coluna_rede] = float('nan')
            yield bloco

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
    @st.cache_data
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

            estatisticas_parciais = []
            contagens_parciais = []
            municipios = []
            municipios_vistos = set()
            municipios_com_dependencia = set()

            for df in Dados.iterar_ano(ano, columns=colunas_necessarias):
                df = Filtrar.filtrar_cidade(cidades, df)
                if df.empty:
                    continue

                df['Município'] = df['Município da Prova'].map(
                    Filtrar.codigo_para_municipio()
                )
                for municipio in df['Município'].dropna().unique():
                    if municipio not in municipios_vistos:
                        municipios.append(municipio)
                        municipios_vistos.add(municipio)

                dependencias = pd.to_numeric(
                    df['Dependência administrativa'],
                    errors='coerce',
                ).map(Config.DEPENDENCIAS_ESCOLA)
                municipios_com_dependencia.update(
                    dependencias[dependencias.notna()]
                    .groupby(df['Município'])
                    .any()
                    .loc[lambda valores: valores]
                    .index
                )
                contagens = (
                    df.assign(_rede_escolar=dependencias)
                    .dropna(subset=['_rede_escolar'])
                    .groupby(['Município', '_rede_escolar'])
                    .size()
                )
                if not contagens.empty:
                    contagens_parciais.append(contagens)

                df_notas = Dados.filtrar_alunos_por_notas_objetivas(df)
                faltas = df_notas[colunas_objetivas].isna().sum(axis=1)
                df_notas = df_notas.loc[faltas < 2]
                if not df_notas.empty:
                    estatisticas_notas = {}
                    for coluna in colunas_notas:
                        notas = df_notas[coluna]
                        if coluna == 'Redação':
                            notas = notas.mask(notas.eq(0))
                        estatisticas_notas[coluna] = notas.groupby(
                            df_notas['Município']
                        ).agg(['sum', 'count'])
                    estatisticas_parciais.append(
                        pd.concat(estatisticas_notas, axis=1)
                    )

                del df, df_notas, dependencias

            if contagens_parciais:
                contagens_por_muni = (
                    pd.concat(contagens_parciais)
                    .groupby(level=[0, 1])
                    .sum()
                    .unstack(fill_value=0)
                    .reindex(
                        index=municipios,
                        columns=list(Config.DEPENDENCIAS_ESCOLA.values()),
                        fill_value=0,
                    )
                )
            else:
                contagens_por_muni = pd.DataFrame(
                    0,
                    index=municipios,
                    columns=list(Config.DEPENDENCIAS_ESCOLA.values()),
                )

            colunas_contagem_por_nome = {
                nome: Config.COLUNAS_CONTAGEM_REDE[codigo]
                for codigo, nome in Config.DEPENDENCIAS_ESCOLA.items()
            }
            contagens_por_muni = contagens_por_muni.rename(
                columns=colunas_contagem_por_nome
            )
            if municipios:
                possui_dependencias = pd.Index(municipios).isin(
                    municipios_com_dependencia
                )
                contagens_por_muni.loc[
                    ~possui_dependencias, colunas_contagem
                ] = float('nan')
            contagens_por_muni = contagens_por_muni.reset_index(
                names='Município'
            )

            if estatisticas_parciais:
                estatisticas = (
                    pd.concat(estatisticas_parciais)
                    .groupby(level=0)
                    .sum()
                )
                medias_por_muni = pd.DataFrame(index=estatisticas.index)
                for coluna in colunas_notas:
                    medias_por_muni[coluna] = (
                        estatisticas[(coluna, 'sum')]
                        / estatisticas[(coluna, 'count')].replace(0, float('nan'))
                    )
                medias_por_muni = medias_por_muni.reset_index(
                    names='Município'
                )
            else:
                medias_por_muni = pd.DataFrame(
                    columns=['Município'] + colunas_notas
                )
            medias_por_muni['Geral'] = medias_por_muni[colunas_notas].mean(axis=1)

            resultado_ano = medias_por_muni.merge(
                contagens_por_muni,
                on='Município',
                how='outer',
            )
            resultado_ano['Ano'] = str(ano)
            resultados.append(resultado_ano)

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


    # ------------------------------------------------------------------
    # Medidas de tendência (Kendall e Sen)
    # ------------------------------------------------------------------
    @staticmethod
    def _preparar_serie(x, y):
        """Converte x e y em arrays float e descarta pares com valor ausente."""
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        validos = ~(np.isnan(x) | np.isnan(y))
        return x[validos], y[validos]

    @staticmethod
    def kendall(x, y):
        """Calcula o tau-b de Kendall e o p-valor do teste de Mann-Kendall.

        x é o tempo (anos) e y é a série de notas médias. O tau varia de -1
        (queda constante) a 1 (alta constante). Retorna (tau, p_valor), ou
        (nan, nan) quando há menos de 3 pontos válidos.
        """
        x, y = Dados._preparar_serie(x, y)
        n = len(x)
        if n < 3:
            return float('nan'), float('nan')

        # Compara todos os pares (i < j): +1 concordante, -1 discordante.
        i, j = np.triu_indices(n, k=1)
        sinal_x = np.sign(x[j] - x[i])
        sinal_y = np.sign(y[j] - y[i])
        s = float((sinal_x * sinal_y).sum())

        # tau-b: desconta os pares empatados em x e em y.
        total_pares = n * (n - 1) / 2
        denominador = math.sqrt(
            (total_pares - (sinal_x == 0).sum())
            * (total_pares - (sinal_y == 0).sum())
        )
        if denominador == 0:
            return float('nan'), float('nan')
        tau = s / denominador

        # Teste de Mann-Kendall (aproximação normal, com correção de empates em y).
        _, repeticoes = np.unique(y, return_counts=True)
        correcao_empates = (
            repeticoes * (repeticoes - 1) * (2 * repeticoes + 5)
        ).sum()
        variancia = (n * (n - 1) * (2 * n + 5) - correcao_empates) / 18
        if variancia <= 0:
            return float(tau), float('nan')

        z = 0.0 if s == 0 else (s - np.sign(s)) / math.sqrt(variancia)
        p_valor = math.erfc(abs(z) / math.sqrt(2))
        return float(tau), float(p_valor)

    @staticmethod
    def inclinacao_sen(x, y):
        """Inclinação de Sen: mediana das inclinações entre todos os pares de pontos.

        O resultado está na unidade de y por unidade de x (pontos de nota por
        ano). Retorna nan quando há menos de 2 pontos válidos.
        """
        x, y = Dados._preparar_serie(x, y)
        if len(x) < 2:
            return float('nan')

        i, j = np.triu_indices(len(x), k=1)
        delta_x = x[j] - x[i]
        validos = delta_x != 0
        if not validos.any():
            return float('nan')

        inclinacoes = (y[j] - y[i])[validos] / delta_x[validos]
        return float(np.median(inclinacoes))

    @staticmethod
    def angulo_sen(x, y):
        """Ângulo, em graus, da reta de Sen (arco tangente da inclinação).

        Positivo indica tendência de alta e negativo, de queda.
        """
        inclinacao = Dados.inclinacao_sen(x, y)
        if math.isnan(inclinacao):
            return float('nan')
        return float(math.degrees(math.atan(inclinacao)))