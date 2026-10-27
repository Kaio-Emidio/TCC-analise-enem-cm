from pathlib import Path
import pandas as pd
from config import Config
from processamento_de_dados.Dados import Dados

def criar_tabelas(recriar: bool = False) -> Path:
    anos = list(range(2009, 2025))
    disciplinas = [
        'Ciências da Natureza',
        'Ciências Humanas',
        'Linguagens e Códigos',
        'Matemática',
        'Redação',
        'Geral',
    ]
    colunas_contagem = list(Config.COLUNAS_CONTAGEM_REDE.values())
    colunas_tabela = disciplinas + colunas_contagem
    pasta_saida = Config.PASTA_PROJETO / 'Tabelas_graficos'
    arquivo_saida = pasta_saida / 'medias_enem_por_municipio.xlsx'
    pasta_saida.mkdir(parents=True, exist_ok=True)

    if arquivo_saida.exists() and not recriar:
        colunas_existentes = pd.read_excel(
            arquivo_saida,
            sheet_name=0,
            nrows=0,
        ).columns
        arquivos_parquet = [
            Config.PASTA_SAIDA / f"MICRODADOS_ENEM_{ano}.parquet"
            for ano in anos
        ]
        datas_parquet = [
            arquivo.stat().st_mtime
            for arquivo in arquivos_parquet
            if arquivo.exists()
        ]
        planilha_atualizada = (
            not datas_parquet
            or arquivo_saida.stat().st_mtime >= max(datas_parquet)
        )
        if (
            set(colunas_tabela).issubset(colunas_existentes)
            and planilha_atualizada
        ):
            return arquivo_saida

    cidades = list(Config.CODIGOS_MUNICIPIOS)
    medias = Dados.media_materias_por_cidade_ano(cidades, anos)

    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as escritor:
        for cidade in cidades:
            dados_cidade = medias.loc[medias['Município'].eq(cidade)].copy()
            if not dados_cidade.empty:
                dados_cidade['Ano'] = pd.to_numeric(
                    dados_cidade['Ano'],
                    errors='raise',
                ).astype(int)

            tabela = (
                dados_cidade.set_index('Ano')
                .reindex(anos)[colunas_tabela]
                .rename_axis('Ano')
                .reset_index()
            )
            nome_aba = cidade[:31]
            tabela.to_excel(escritor, sheet_name=nome_aba, index=False)

            planilha = escritor.sheets[nome_aba]
            planilha.freeze_panes = 'A2'
            planilha.auto_filter.ref = planilha.dimensions
            for coluna, largura in {
                'A': 10,
                'B': 24,
                'C': 24,
                'D': 24,
                'E': 16,
                'F': 14,
                'G': 12,
                'H': 22,
                'I': 22,
                'J': 22,
                'K': 22,
            }.items():
                planilha.column_dimensions[coluna].width = largura

            for linha in planilha.iter_rows(min_row=2, min_col=2, max_col=7):
                for celula in linha:
                    celula.number_format = '0.00'

            for linha in planilha.iter_rows(min_row=2, min_col=8, max_col=11):
                for celula in linha:
                    celula.number_format = '#,##0'

    return arquivo_saida
