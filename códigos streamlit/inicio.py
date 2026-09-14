import streamlit as st

st.set_page_config(
    page_title='Análise Temporal Notas do ENEM',
    layout='wide')

st.title('Análise Temporal Notas do ENEM')
st.subheader('Média das notas em cada disciplina por ano')

colunas = st.columns(5)

with colunas[0]:
    st.metric(label='Média LC', value="85,50")
with colunas[1]:
    st.metric(label='Média CH', value="91,20")
with colunas[2]:
    st.metric(label='Média MT', value="89,52")
with colunas[3]:
    st.metric(label='Média CN', value="85,74")
with colunas[4]:
    st.metric(label='Média REDAÇÃO', value="65,74")

# Conforme o ano selecionado, os valores das notas mudam conforme o ano

st.header('Gráficos')

ano_selecionado = st.slider('Selecione o ano de interesse', 2009, 2025, (2010, 2024))

st.multiselect(label='Selecione as áreas que deseja visualizar',
               options=['LC', 'CH', 'MT', 'CN', 'Redação'])

st.multiselect(label='Selecione os municípios que deseja visualizar',
               options=['Ceará-Mirim', 'Natal', 'Parnamirim', 'Extremoz', 'São Gonçalo do Amarante', 'Macaíba'],
               default=['Ceará-Mirim', 'Natal'])