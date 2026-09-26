from processamento_de_dados.Dados import Dados
from processamento_de_dados.Filtrar import Filtrar
import plotly.express as px
import pandas as pd

class CriarGrafico:
    def linha(cidades: list, anos: list, materia: str = 'Geral'):
        # o eixo x será os anos selecionados
        # o eixo y será a nota
        # cada cidade terá uma linha individual
        medias_gerais = Dados.media_materias_por_cidade_ano(
            cidades=cidades, anos=anos
        )

        if medias_gerais.empty:
            return px.line(title='Nenhum dado encontrado')

        # --- CASO 1: Selecionou "Todas as Disciplinas" ---
        if materia == 'Todas':
            disciplinas = [
                'Ciências da Natureza',
                'Ciências Humanas',
                'Linguagens e Códigos',
                'Matemática',
                'Redação',
            ]

            # Transforma as colunas das matérias em linhas (formato longo)
            df_longo = medias_gerais.melt(
                id_vars=['Ano', 'Município'],
                value_vars=disciplinas,
                var_name='Disciplina',
                value_name='Nota Média',
            )

            # Se houver mais de uma cidade selecionada, agrupa/distingue o rótulo
            if len(cidades) > 1:
                df_longo['Legenda'] = (
                    df_longo['Município'] + ' - ' + df_longo['Disciplina']
                )
                cor = 'Legenda'
            else:
                cor = 'Disciplina'

            figura = px.line(
                df_longo,
                x='Ano',
                y='Nota Média',
                color=cor,
                markers=True,
                title='Evolução Temporal - Todas as Disciplinas',
            )

        # --- CASO 2: Selecionou uma matéria específica ou "Geral" ---
        else:
            figura = px.line(
                medias_gerais,
                x='Ano',
                y=materia,
                color='Município',
                line_group='Município',
                markers=True,
                labels={
                    'Ano': 'Ano',
                    materia: f'Nota média ({materia})',
                    'Município': 'Município',
                },
                title=f'Média das notas por município e ano - {materia}',
            )

        figura.update_xaxes(type='category')
        figura.update_layout(hovermode='x unified')

        return figura
        
    def radar(cidades: list, ano: int):
        df = Dados.ler_ano(ano)
        df = Filtrar.filtrar_cidade(cidades, df).copy()
        df['Município'] = df['Município da Prova'].map(
            Filtrar.codigo_para_municipio()
        )

        medias_por_materia = (
            df.groupby('Município', as_index=False)[
                ['Ciências da Natureza', 'Ciências Humanas', 'Linguagens e Códigos', 'Matemática', 'Redação']
            ]
            .mean()
            .melt(id_vars='Município', var_name='Matéria', value_name='Nota')
        )

        if medias_por_materia.empty:
                    figura = px.line_polar(title=f"Sem dados para o ano {ano}")
                    return figura

        figura = px.line_polar(
            medias_por_materia,
            r='Nota',
            theta='Matéria',
            color='Município',
            markers=True,
            line_close=True,
            title=f'Comparativo das áreas de conhecimento em {ano}',
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

    def violino(cidades: list, disciplina: str, ano: int):
        # 1. Carrega os dados do ano especificado
        df = Dados.ler_ano(ano)

        # 2. Filtra pelas cidades selecionadas
        df = Filtrar.filtrar_cidade(cidades, df).copy()

        # 3. Mapeia os códigos de município para seus nomes
        df['Município'] = df['Município da Prova'].map(
            Filtrar.codigo_para_municipio()
        )

        disciplinas_provas = [
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação'
        ]

        # --- CASO ESPECIAL: Se for 'Geral', calcula a média geral de cada aluno ---
        if disciplina == 'Geral':
            # Garante que todas as colunas sejam numéricas
            for col in disciplinas_provas:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Calcula a média do aluno nas 5 matérias (linha a linha)
            df['Geral'] = df[disciplinas_provas].mean(axis=1)
        else:
            # Se for uma matéria individual, converte apenas ela
            df[disciplina] = pd.to_numeric(df[disciplina], errors='coerce')

        # 4. Remove linhas sem município ou sem nota na métrica escolhida
        df_filtrado = df.dropna(subset=['Município', disciplina]).copy()

        # Se não houver dados após os filtros, retorna um gráfico limpo
        if df_filtrado.empty:
            figura = px.violin(
                title=f"Sem dados para '{disciplina}' no ano {ano}"
            )
            return figura

        # 5. Criação do gráfico de violino
        figura = px.violin(
            df_filtrado,
            x='Município',
            y=disciplina,
            color='Município',
            box=True,  # Mostra o boxplot interno
            title=f'Distribuição das notas ({disciplina}) por município em {ano}',
            labels={
                disciplina: 'Nota',
                'Município': 'Município da Prova',
            },
        )

        # 6. Cálculo e aplicação do zoom automático
        min_nota = df_filtrado[disciplina].min()
        max_nota = df_filtrado[disciplina].max()

        limite_inferior = max(0, min_nota - 10)
        limite_superior = min(1000, max_nota + 10)

        figura.update_yaxes(
            range=[limite_inferior, limite_superior], showspikes=False
        )
        figura.update_xaxes(showspikes=False)

        # 7. Ajustes de layout
        figura.update_layout(
            height=500,
            autosize=True,
            showlegend=False
        )

        return figura
                