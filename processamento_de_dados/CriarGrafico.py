from processamento_de_dados.Dados import Dados
from processamento_de_dados.Filtrar import Filtrar
import plotly.express as px
import pandas as pd

class CriarGrafico:
    def linha(cidades: list, anos: list):
        # o eixo x será os anos selecionados
        # o eixo y será a nota
        # cada cidade terá uma linha individual
        medias_gerais = Dados.media_geral_por_cidade_ano(
            cidades=cidades,
            anos=anos
        )

        figura = px.line(
            medias_gerais,
            x='Ano',
            y='Média Geral',
            color='Município',
            line_group='Município',
            markers=True,
            labels={
                'Ano': 'Ano',
                'Média Geral': 'Nota média',
                'Município': 'Município',
            },
            title='Média das notas por município e ano',
        )
        figura.update_xaxes(type='category')
        figura.update_layout(legend_title_text='Município')

        return figura
        
    def radar(df: pd.DataFrame, cidades: list, ano: int):
        df_filtrado = df.copy()

        if 'Ano' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Ano'].astype(str) == str(ano)]

        if 'Município da Prova' in df_filtrado.columns:
            df_filtrado = Filtrar.filtrar_cidade(cidades, df_filtrado)
            df_filtrado['Município'] = df_filtrado['Município da Prova'].map(
                Filtrar.codigo_para_municipio()
            )
        else:
            df_filtrado = df_filtrado[df_filtrado['Município'].isin(cidades)]

        if 'Área do Conhecimento' not in df_filtrado.columns:
            colunas_notas = [
                'Linguagens e Códigos',
                'Ciências Humanas',
                'Matemática',
                'Ciências da Natureza',
                'Redação',
            ]
            df_filtrado = df_filtrado.melt(
                id_vars=['Município'],
                value_vars=colunas_notas,
                var_name='Área do Conhecimento',
                value_name='Média Geral',
            ).groupby(
                ['Município', 'Área do Conhecimento'], as_index=False
            )['Média Geral'].mean()

        figura = px.line_polar(
            df_filtrado,
            r='Média Geral',
            theta='Área do Conhecimento',
            color='Município',
            line_close=True,
            markers=True,
            labels={
                'Média Geral': 'Nota média',
                'Área do Conhecimento': 'Área do Conhecimento',
                'Município': 'Município',
            },
            title=f'Média das notas por área do conhecimento - {ano}',
        )
        figura.update_layout(legend_title_text='Município')

        return figura