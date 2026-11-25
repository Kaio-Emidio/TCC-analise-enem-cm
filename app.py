import streamlit as st
from processamento_de_dados.CriarGrafico import CriarGrafico
from processamento_de_dados.Dados import Dados
from processamento_de_dados.Exportar import criar_tabelas
from processamento_de_dados.Filtrar import Filtrar
from config import Config

st.set_page_config(page_title='Análise Temporal Notas do ENEM', layout='wide')

anos = list(range(2009, 2026))
try:
    with st.spinner('Verificando e preparando os microdados do ENEM...'):
        status_dados = Filtrar.filtrar_colunas(anos)
except (FileNotFoundError, ValueError) as erro:
    st.error(str(erro))
    st.stop()

anos_sem_dependencia = status_dados["anos_sem_dependencia"]
anos_sem_dados = status_dados["anos_sem_dados"]

if anos_sem_dados:
    st.warning(
        'Microdados ausentes para os anos '
        f'{", ".join(map(str, anos_sem_dados))}. Esses anos serão ignorados. '
        'Para incluí-los, coloque os CSVs correspondentes em microdados_brutos.'
    )

if anos_sem_dependencia:
    st.warning(
        'Contagens por rede escolar indisponíveis para os anos '
        f'{", ".join(map(str, anos_sem_dependencia))}. '
        'Disponibilize os CSVs originais para reprocessar esses dados.'
    )

criar_tabelas(recriar=bool(status_dados["anos_processados"]))

def carregar_css(caminho):
    with open(caminho) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carrega o estilo do arquivo externo
carregar_css('style.css')

st.title('Análise Temporal Notas do ENEM')

progress_bar = st.empty()
status_text = st.empty()

TELAS = {
    'temporal': 'Exibição temporal',
    'focalizada': 'Exibição focalizada',
    'distribuicao': 'Distribuição das notas',
}

if 'tela_ativa' not in st.session_state:
    st.session_state['tela_ativa'] = 'temporal'

FILTROS_PADRAO = {
    'filtro_intervalo_anos': (2009, 2025),
    'filtro_ano_foco': 2025,
    'filtro_cidades': [],
    'filtro_disciplina': 'Geral',
}

for chave, valor_padrao in FILTROS_PADRAO.items():
    chave_salva = f'{chave}_salvo'
    if chave_salva not in st.session_state:
        st.session_state[chave_salva] = valor_padrao
    if chave not in st.session_state:
        st.session_state[chave] = st.session_state[chave_salva]

if not st.session_state.get('_filtros_incluem_2025', False):
    st.session_state['filtro_intervalo_anos'] = (2009, 2025)
    st.session_state['filtro_intervalo_anos_salvo'] = (2009, 2025)
    st.session_state['filtro_ano_foco'] = 2025
    st.session_state['filtro_ano_foco_salvo'] = 2025
    st.session_state['_filtros_incluem_2025'] = True


def salvar_filtros():
    for chave in FILTROS_PADRAO:
        if chave in st.session_state:
            st.session_state[f'{chave}_salvo'] = st.session_state[chave]


with st.sidebar.form(key='filtros_enem'):
    if st.session_state['tela_ativa'] == 'temporal':
        ano_inicio, ano_fim = st.slider(
            label='Selecione o intervalo de anos desejados',
            min_value=2009,
            max_value=2025,
            key='filtro_intervalo_anos',
        )

    if st.session_state['tela_ativa'] in ('focalizada', 'distribuicao'):
        ano_de_foco = st.selectbox(
            label='Selecione o ano de foco',
            options=anos,
            key='filtro_ano_foco',
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
        key='filtro_cidades',
    )

    if st.session_state['tela_ativa'] in ('temporal', 'distribuicao'):
        disciplina_selecionada = st.selectbox(
            label='Selecione a disciplina que deseja visualizar',
            options=[
                'Geral',
                'Ciências da Natureza',
                'Ciências Humanas',
                'Linguagens e Códigos',
                'Matemática',
                'Redação',
            ],
            key='filtro_disciplina',
        )
    st.form_submit_button(
        label='Aplicar Filtros',
        type='primary',
        on_click=salvar_filtros,
    )

@st.dialog("Dashboard ENEM", width="large")
def abrir_tutorial():
    st.markdown("""
    Esse dashboard foi desenvolvido para analisar o desempenho dos alunos de alguns dos municípios que fazem parte da Grande Natal no ENEM ao longo do tempo, 
    permitindo comparações entre diferentes municípios e disciplinas. 
    Esse projeto é desenvolvido por alunos do curso tecnico em informática do IFRN como projeto de conclusão de curso.
    Os filtros da barra lateral variam de acordo com a tela selecionada.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 1. Sidebar (Filtros)")
        st.markdown("""
        * **Ano de Foco:** Define o ano analisado nos gráficos de **Radar**, **Violino** e nas **Métricas**;
        * **Intervalo de Anos:** Define o período temporal do gráfico de Linha;
        * **Municípios:** Escolher as cidades para comparar;
        * **Disciplina:** Alterne entre disciplinas específicas ou a média **Geral**.
        * *Lembre-se de clicar em **Aplicar Filtros** para atualizar!*
        """)
        
    with col2:
        st.markdown("### 2. Gráficos Interativos")
        st.markdown("""
        * **Gráfico de Linha:** Acompanhe o crescimento ou queda das médias ao longo do tempo.
        * **Radar:** Compare o desempenho relativo em cada área de conhecimento em um ano específico.
        * **Violino:** Analise a dispersão e concentração das notas dos alunos em um ano específico.
        """)

    if st.button("Fechar", type="primary"):
        st.rerun()

with st.sidebar:
    if st.button("Tutorial", use_container_width=True):
        abrir_tutorial()

def selecionar_tela(chave):
    st.session_state['tela_ativa'] = chave


st.header('Gráficos')

colunas_botoes = st.columns(len(TELAS))
for coluna, (chave, rotulo) in zip(colunas_botoes, TELAS.items()):
    ativa = st.session_state['tela_ativa'] == chave
    coluna.button(
        rotulo,
        key=f'btn_{chave}',
        use_container_width=True,
        type='primary' if ativa else 'secondary',
        on_click=selecionar_tela,
        args=(chave,),
    )

st.divider()

def tela_temporal():
    st.subheader('Exibição temporal')
    anos_selecionados = list(range(ano_inicio, ano_fim + 1))

    grafico_linha = CriarGrafico.linha(
        cidades=cidades_selecionadas,
        anos=anos_selecionados,
        materia=disciplina_selecionada,
    )
    st.plotly_chart(grafico_linha, use_container_width=True)


def tela_focalizada():
    st.subheader('Exibição Focalizada')

    disciplinas_provas = [
        'Ciências da Natureza',
        'Ciências Humanas',
        'Linguagens e Códigos',
        'Matemática',
        'Redação',
        'Município da Prova',
    ]
    dados_ano_selec = Dados.ler_ano(
        ano_de_foco,
        columns=disciplinas_provas,
    )
    estatistica_ano_selec = Dados.estatistica(dados_ano_selec)

    medias_municipais = Dados.medias_por_municipio(
        cidades=cidades_selecionadas,
        ano=ano_de_foco,
    )

    col_metricas, col_radar = st.columns([1, 3])

    with col_metricas:
        for nome in [
            'Linguagens e Códigos',
            'Ciências Humanas',
            'Matemática',
            'Ciências da Natureza',
            'Redação',
        ]:
            st.metric(
                label=f'Média {nome}',
                value=estatistica_ano_selec[nome]['media'],
            )

    with col_radar:
        grafico_radar = CriarGrafico.radar(
            medias_por_municipio=medias_municipais,
            ano=ano_de_foco,
        )
        grafico_radar.update_layout(
            margin=dict(l=40, r=40, t=40, b=40),
            height=550,
        )
        st.plotly_chart(grafico_radar, use_container_width=True)


def tela_distribuicao():
    st.subheader('Distribuição das Notas')

    grafico_violino = CriarGrafico.violino(
        cidades=cidades_selecionadas,
        ano=ano_de_foco,
        disciplina=disciplina_selecionada,
    )
    st.plotly_chart(grafico_violino, use_container_width=True)


RENDERIZADORES = {
    'temporal': tela_temporal,
    'focalizada': tela_focalizada,
    'distribuicao': tela_distribuicao,
}

RENDERIZADORES[st.session_state['tela_ativa']]()