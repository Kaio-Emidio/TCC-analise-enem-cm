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
        
    def radar(cidades: list, ano: int):
        df = Dados.ler_ano(ano)
        df = Filtrar.filtrar_cidade(cidades, df).copy()
        df['Município'] = df['Município da Prova'].map(
            Filtrar.codigo_para_municipio()
        )
        df['Média Geral'] = df[
            ['Ciências da Natureza', 
            'Ciências Humanas', 
            'Linguagens e Códigos', 
            'Matemática', 
            'Redação']
            ].mean(axis=1)

        medias_por_materia = (
            df.groupby('Município', as_index=False)[
                ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens e Códigos', 'Matemática', 'Redação']
            ]
            .mean()
            .melt(id_vars='Município', var_name='Matéria', value_name='Nota')
        )

        figura = px.line_polar(
            medias_por_materia,
            r='Nota',
            theta='Matéria',
            color='Município',
            line_close=True,
            title=f'Comparativo das áreas de conhecimento - {ano}',
            labels={
                'Nota': 'Nota média',
                'Matéria': 'Área de conhecimento',
                'Município': 'Município',
            }
        )

        menor_nota = medias_por_materia['Nota'].min()
        maior_nota = medias_por_materia['Nota'].max()

        limite_inferior = max(0, menor_nota - 10)
        limite_superior = min(1000, maior_nota + 10)

        # Configuração do zoom e da cor dos números da escala
        figura.update_polars(
            radialaxis=dict(
                visible=True,
                range=[limite_inferior, limite_superior],
                tickfont=dict(
                    color='black',
                    size=12
                ),
                tickangle=45,
            )
        )

        figura.update_layout(
            height=500,
            autosize=True
        )

        return figura