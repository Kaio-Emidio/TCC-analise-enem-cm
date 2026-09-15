# --- Importar as bibliotecas --- #
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# --- Dataframe exemplo apenas para teste --- #
dados_medias = {
    'Ano': ['2022', '2023', '2024'],
    'Linguagens e Códigos': [510.2, 520.5, 515.0],
    'Ciências Humanas': [530.4, 545.1, 535.5],
    'Ciências da Natureza': [495.5, 505.8, 500.2],
    'Matemática': [560.0, 580.3, 575.6],
    'Redação': [606.4, 624.3, 618.0]
}
df_medias = pd.DataFrame(dados_medias)

# Dados Simulados (Para o Gráfico de Violino)
np.random.seed(42)
amostra_alunos = []
colunas_materias = ['Linguagens e Códigos', 'Ciências Humanas', 'Ciências da Natureza', 'Matemática', 'Redação']

for ano in ['2022', '2023', '2024']:
    for i in range(500):
        aluno = {'Ano': ano}
        for mat in colunas_materias:
            media_ano = df_medias.loc[df_medias['Ano'] == ano, mat].values[0]
            nota = np.random.normal(loc=media_ano, scale=85)
            aluno[mat] = max(0, min(1000, nota))
        amostra_alunos.append(aluno)

df_amostra = pd.DataFrame(amostra_alunos)

# --- Utilizando o Streamlit para criar a página --- #
st.title('Teste dos gráficos')

# Filtro dos Gráficos
st.markdown("### Filtros de Visualização")
materias_selecionadas = st.multiselect(
    'Selecione as Áreas de Conhecimento:',
    options=colunas_materias,
    default=colunas_materias
    )

if not materias_selecionadas:
    st.warning('Por favor, selecione pelo menos uma área de conhecimento para visualizar os gráficos.')
else:
    # --- Prepara os dados --- #
    df_medias_long = df_medias.melt(id_vars=['Ano'], value_vars=materias_selecionadas, 
                                    var_name='Matéria', value_name='Média Geral')

    # --- Gráfico 1: Linha --- #
    st.subheader("Gráfico de linha")
    fig_linha = px.line(
        df_medias_long,
        x='Ano',
        y='Média Geral',
        color='Matéria',
        markers=True,
        title="Evolução das Áreas de Conhecimento"
    )

    st.plotly_chart(fig_linha, use_container_width=True)

    # --- Gráfico 2: Radar --- #
    st.subheader("Gráfico Radar")
    
    # Verifica se tem pelo menos três matérias selecionadas
    if len(materias_selecionadas) < 3:
        st.info("⚠️ **Aviso:** Selecione **pelo menos 3 áreas de conhecimento** no filtro acima para gerar o polígono do Gráfico de Radar.")
    else:
        fig_radar = px.line_polar(
            df_medias_long,
            r='Média Geral',
            theta='Matéria', 
            color='Ano',     
            line_close=True,
            title="Comparativo das Áreas de Conhecimento"
        )

        st.plotly_chart(fig_radar, use_container_width=True)
        
    # --- Gráfico Violino --- #
    st.subheader("Gráfico Violino")
    
    df_amostra_long = df_amostra.melt(id_vars=['Ano'], value_vars=materias_selecionadas, 
                                      var_name='Matéria', value_name='Nota')
    
    fig_violino = px.violin(
        df_amostra_long,
        x='Matéria',
        y='Nota',
        color='Ano',
        box=True, 
        title="Dispersão de Notas por Edição do ENEM"
    )
    min_amostra = df_amostra_long['Nota'].min()
    max_amostra = df_amostra_long['Nota'].max()
    fig_violino.update_yaxes(range=[max(0, min_amostra - 50), min(1050, max_amostra + 50)])
    
    st.plotly_chart(fig_violino, use_container_width=True)