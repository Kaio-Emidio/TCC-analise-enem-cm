import streamlit as st
import pandas as pd
import plotly.express as px
from processamento_de_dados.Dados import Dados
from processamento_de_dados.Filtrar import Filtrar
from processamento_de_dados.CriarGrafico import CriarGrafico

Filtrar.filtrar_colunas()

st.set_page_config(
    page_title='Análise Temporal Notas do ENEM',
    layout='wide')

st.title('Análise Temporal Notas do ENEM')

progress_bar = st.empty()
status_text = st.empty()

anos = []
for ano in range(2009, 2025):
    anos.append(ano)

with st.sidebar:
    ano_de_foco = st.selectbox(
        label='Selecione o ano de foco',
        options=anos
    )

    ano_inicio, ano_fim = st.slider(label='Selecione o intervalo de anos desejados',
                                min_value=2009,
                                max_value=2024,
                                value=(2022, 2024))

    cidades_selecionadas = st.multiselect(label='Selecione os municípios que deseja visualizar',
                options=['Ceará-Mirim', 'Natal', 'Parnamirim', 'Extremoz', 'São Gonçalo do Amarante', 'Macaíba'],
                default=['Ceará-Mirim', 'Natal'])

st.subheader(f'Média das notas em cada disciplina em {ano_de_foco}')
dados_ano_selec = Dados.ler_ano(ano_de_foco)
estatistica_ano_selec = Dados.estatistica(dados_ano_selec)

colunas = st.columns(5)

with colunas[0]:
    st.metric(label='Média Linguagens e Códigos', value=estatistica_ano_selec['Linguagens e Códigos']['media'])
with colunas[1]:
    st.metric(label='Média Ciências Humanas', value=estatistica_ano_selec['Ciências Humanas']['media'])
with colunas[2]:
    st.metric(label='Média Matemática', value=estatistica_ano_selec['Matemática']['media'])
with colunas[3]:
    st.metric(label='Média Ciências da Natureza', value=estatistica_ano_selec['Ciências da Natureza']['media'])
with colunas[4]:
    st.metric(label='Média Redação', value=estatistica_ano_selec['Redação']['media'])

# Conforme o ano selecionado, os valores das notas mudam conforme o ano

st.header('Gráficos')

st.subheader('Exibição temporal')

anos_selecionados = list(range(ano_inicio, ano_fim + 1))


grafico_linha = CriarGrafico.linha(
    cidades=cidades_selecionadas,
    anos=anos_selecionados
)
st.plotly_chart(grafico_linha, width='stretch')

st.subheader('Exibição Focalizada')

grafic_radar = CriarGrafico.radar(
    cidades=cidades_selecionadas,
    ano=ano_de_foco
)
st.plotly_chart(grafic_radar, width='stretch')
