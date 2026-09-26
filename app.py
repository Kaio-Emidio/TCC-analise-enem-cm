import pandas as pd
import plotly.express as px
import streamlit as st
from processamento_de_dados.CriarGrafico import CriarGrafico
from processamento_de_dados.Dados import Dados
from processamento_de_dados.Filtrar import Filtrar


def carregar_css(caminho):
    with open(caminho) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carrega o estilo do arquivo externo
carregar_css('style.css')
Filtrar.filtrar_colunas()

st.set_page_config(page_title='Análise Temporal Notas do ENEM', layout='wide')

st.title('Análise Temporal Notas do ENEM')

progress_bar = st.empty()
status_text = st.empty()

anos = list(range(2009, 2025))

with st.sidebar.form(key='filtros_enem'):
    ano_de_foco = st.selectbox(
        label='Selecione o ano de foco',
        options=anos,
        index=anos.index(2022) if 2022 in anos else 0,
    )

    ano_inicio, ano_fim = st.slider(
        label='Selecione o intervalo de anos desejados',
        min_value=2009,
        max_value=2024,
        value=(2009, 2024),
    )

    cidades_selecionadas = st.multiselect(
        label='Selecione os municípios que deseja visualizar',
        options=[
            'Ceará-Mirim',
            'Natal',
            'Parnamirim',
            'Extremoz',
            'São Gonçalo do Amarante',
            'Macaíba',
            'Geral',
        ],
        default=[],
    )

    disciplina_selecionada = st.selectbox(
        label='Selecione a disciplina que deseja visualizar',
        options=[
            'Geral',  # <--- Adicionado 'Geral' nas opções
            'Ciências da Natureza',
            'Ciências Humanas',
            'Linguagens e Códigos',
            'Matemática',
            'Redação',
        ],
        index=0
    )
    st.form_submit_button(label='Aplicar Filtros', type='primary')

st.subheader(f'Média das notas em cada disciplina em {ano_de_foco}')
dados_ano_selec = Dados.ler_ano(ano_de_foco)
estatistica_ano_selec = Dados.estatistica(dados_ano_selec)

st.header('Gráficos')

st.subheader('Exibição temporal')
anos_selecionados = list(range(ano_inicio, ano_fim + 1))

grafico_linha = CriarGrafico.linha(
    cidades=cidades_selecionadas, 
    anos=anos_selecionados,
    materia=disciplina_selecionada
)
st.plotly_chart(grafico_linha, use_container_width=True)

st.subheader('Exibição Focalizada')

col_metricas, col_radar = st.columns([1, 3])

with col_metricas:
    st.metric(
        label='Média Linguagens e Códigos',
        value=estatistica_ano_selec['Linguagens e Códigos']['media'],
    )
    st.metric(
        label='Média Ciências Humanas',
        value=estatistica_ano_selec['Ciências Humanas']['media'],
    )
    st.metric(
        label='Média Matemática',
        value=estatistica_ano_selec['Matemática']['media'],
    )
    st.metric(
        label='Média Ciências da Natureza',
        value=estatistica_ano_selec['Ciências da Natureza']['media'],
    )
    st.metric(
        label='Média Redação',
        value=estatistica_ano_selec['Redação']['media'],
    )

with col_radar:
    grafico_radar = CriarGrafico.radar(
        cidades=cidades_selecionadas, ano=ano_de_foco
    )
    
    grafico_radar.update_layout(
        margin=dict(l=40, r=40, t=40, b=40),
        height=550
    )
    st.plotly_chart(grafico_radar, use_container_width=True)
    
st.subheader('Distribuição das Notas')

disciplina_violino = disciplina_selecionada

grafico_violino = CriarGrafico.violino(
    cidades=cidades_selecionadas,
    ano=ano_de_foco,
    disciplina=disciplina_violino,
)
st.plotly_chart(grafico_violino, use_container_width=True)