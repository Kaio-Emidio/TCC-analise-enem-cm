import plotly.express as px

class CriarGrafico:
    def linha(df, cidades, anos):
        # o eixo x será os anos selecionados
        # o eixo y será a nota
        # cada cidade terá uma linha individual
        df_filtrado = df[
            df['Ano'].astype(str).isin(map(str, anos))
            & df['Município'].isin(cidades)
        ].copy()

        figura = px.line(
            df_filtrado,
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
        
