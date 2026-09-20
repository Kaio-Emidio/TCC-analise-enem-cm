import streamlit as st
import pandas as pd
import plotly.express as px
from processamento_de_dados.Dados import Dados
from processamento_de_dados.Filtrar import Filtrar
from processamento_de_dados.CriarGrafico import CriarGrafico

# Filtrar.filtrar_colunas()

st.set_page_config(
    page_title='Análise Temporal Notas do ENEM',
    layout='wide')

st.title('Análise Temporal Notas do ENEM')
st.subheader('Média das notas em cada disciplina por ano')

anos = []
for ano in range(2009, 2025):
    anos.append(ano)

with st.sidebar:
    ano_selecionado = st.selectbox(
        label='Selecione o ano de interesse',
        options=anos
    )

dados_ano_selec = Dados.ler_ano(ano_selecionado)
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

colunas = st.columns(2)

with colunas[1]:
    cidades_selecionadas = st.multiselect(label='Selecione os municípios que deseja visualizar',
                options=['Ceará-Mirim', 'Natal', 'Parnamirim', 'Extremoz', 'São Gonçalo do Amarante', 'Macaíba'],
                default=['Ceará-Mirim', 'Natal'])

    ano_inicio, ano_fim = st.slider(label='Selecione o ano de interesse',
                                min_value=2009,
                                max_value=2024,
                                value=(2009, 2024))
    anos_selecionados = list(range(ano_inicio, ano_fim + 1))
with colunas[0]:
    medias_gerais = Dados.media_geral_por_cidade_ano(
        cidades=cidades_selecionadas,
        anos=anos_selecionados
    )
    figura_linha = CriarGrafico.linha(
        df=medias_gerais,
        cidades=cidades_selecionadas,
        anos=anos_selecionados
    )
    st.plotly_chart(figura_linha, use_container_width=True)

st.multiselect(label='Selecione as áreas que deseja visualizar',
               options=['Linguagens e Códigos', 'Ciências Humanas', 'Matemática', 'Ciências da Natureza', 'Redação'])
