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
    'tendencia': 'Kendall e Sen',
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
    if st.session_state['tela_ativa'] in ('temporal', 'tendencia'):
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
        * **Intervalo de Anos:** Define o período temporal do gráfico de Linha e da tabela de Kendall e Sen;
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
        * **Kendall e Sen:** Tabela que mostra se a nota de cada município tende a subir ou cair ao longo dos anos.
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

PROPORCAO_COLUNAS = [5, 2]  # conteúdo | texto explicativo (lado oposto ao da sidebar)

DISCIPLINAS_TENDENCIA = [
    'Geral',
    'Ciências da Natureza',
    'Ciências Humanas',
    'Linguagens e Códigos',
    'Matemática',
    'Redação',
]

TEXTOS_EXPLICATIVOS = {
    'temporal': (
        'O que esta análise mostra',
        """
Mostra como a **nota média** dos participantes de cada município mudou ao longo dos anos.

Cada linha é um município: linhas que **sobem** indicam melhora no desempenho e linhas que **descem** indicam queda.

Use o filtro de disciplina para ver a média **Geral** ou de uma prova específica, e o intervalo de anos para ampliar ou reduzir o período.
""",
    ),
    'focalizada': (
        'O que esta análise mostra',
        """
Compara os municípios em **um único ano** (o ano de foco).

No **radar**, cada ponta é uma área do conhecimento: quanto mais longe do centro, maior a nota média do município nela.

As **métricas** à esquerda trazem a média de cada prova no ano de foco, calculada sobre todos os participantes dos microdados, e não só sobre os municípios selecionados.
""",
    ),
    'distribuicao': (
        'O que esta análise mostra',
        """
Mostra como as notas se **espalham** entre os participantes de cada município no ano de foco.

A largura do "violino" indica onde há **mais participantes** concentrados. A caixa interna marca a **mediana** e os quartis.

Formas mais alongadas indicam notas mais dispersas, ou seja, maior diferença entre os melhores e os piores resultados.
""",
    ),

    'tendencia': (
        'Como ler a tabela',
        """
    Cada linha resume a série de médias anuais de um município em uma disciplina, a mesma do gráfico de linha.

    * **Kendall (τ):** vai de -1 a 1 e indica se as notas tendem a subir ou descer ao longo dos anos. Perto de 1, sobem quase todo ano; perto de -1, caem; perto de 0, não há direção clara.

    * **p-valor:** abaixo de 0,05, a tendência é considerada estatisticamente significativa (teste de Mann-Kendall).

    * **Inclinação de Sen:** variação típica da nota por ano. É a mediana das inclinações entre todos os pares de anos, por isso é pouco afetada por anos atípicos.

    * **Ângulo de Sen:** a inclinação convertida em graus (arco tangente). Positivo indica tendência de alta; negativo, de queda.

    ### Como o intervalo de anos influencia os resultados?

    Os cálculos consideram somente os anos selecionados no filtro de intervalo. Ao ampliar ou reduzir esse período, os indicadores são recalculados e seus valores podem mudar.

    Isso ocorre porque a tendência é analisada com base nas médias anuais do período escolhido. Assim, um município pode apresentar crescimento em determinado intervalo e uma tendência diferente quando analisado em um período mais amplo.

    **Exemplo:** a tendência entre 2015 e 2018 pode ser diferente daquela observada entre 2015 e 2021.
    """
    ),

}


def painel_explicativo(chave):
    titulo, texto = TEXTOS_EXPLICATIVOS[chave]
    with st.container(border=True):
        st.markdown(f'**{titulo}**')
        st.markdown(texto)


def tela_temporal():
    st.subheader('Exibição temporal')
    col_principal, col_explicacao = st.columns(PROPORCAO_COLUNAS, gap='large')

    with col_principal:
        anos_selecionados = list(range(ano_inicio, ano_fim + 1))

        grafico_linha = CriarGrafico.linha(
            cidades=cidades_selecionadas,
            anos=anos_selecionados,
            materia=disciplina_selecionada,
        )
        st.plotly_chart(grafico_linha, use_container_width=True)

    with col_explicacao:
        painel_explicativo('temporal')


def tela_focalizada():
    st.subheader('Exibição Focalizada')
    col_principal, col_explicacao = st.columns(PROPORCAO_COLUNAS, gap='large')

    with col_principal:
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

    with col_explicacao:
        painel_explicativo('focalizada')


def tela_distribuicao():
    st.subheader('Distribuição das Notas')
    col_principal, col_explicacao = st.columns(PROPORCAO_COLUNAS, gap='large')

    with col_principal:
        grafico_violino = CriarGrafico.violino(
            cidades=cidades_selecionadas,
            ano=ano_de_foco,
            disciplina=disciplina_selecionada,
        )
        st.plotly_chart(grafico_violino, use_container_width=True)

    with col_explicacao:
        painel_explicativo('distribuicao')


def tela_tendencia():
    st.subheader('Tendência das notas: Kendall e Sen')
    col_principal, col_explicacao = st.columns(PROPORCAO_COLUNAS, gap='large')

    with col_principal:
        anos_selecionados = list(range(ano_inicio, ano_fim + 1))
        medias = Dados.media_materias_por_cidade_ano(
            cidades=cidades_selecionadas,
            anos=anos_selecionados,
        )

        if medias.empty:
            st.info('Nenhum dado encontrado para os filtros selecionados.')
        else:
            linhas = []
            for municipio, grupo in medias.groupby('Município'):
                anos_do_municipio = grupo['Ano'].astype(int)
                for disciplina in DISCIPLINAS_TENDENCIA:
                    notas = grupo[disciplina]
                    tau, p_valor = Dados.kendall(anos_do_municipio, notas)
                    linhas.append({
                        'Município': municipio,
                        'Disciplina': disciplina,
                        'Kendall (τ)': tau,
                        'p-valor': p_valor,
                        'Inclinação de Sen (pts/ano)': Dados.inclinacao_sen(
                            anos_do_municipio, notas
                        ),
                        'Ângulo de Sen (°)': Dados.angulo_sen(
                            anos_do_municipio, notas
                        ),
                    })

            st.dataframe(
                linhas,
                use_container_width=True,
                hide_index=True,
                column_config={
                    'Kendall (τ)': st.column_config.NumberColumn(format='%.3f'),
                    'p-valor': st.column_config.NumberColumn(format='%.4f'),
                    'Inclinação de Sen (pts/ano)': st.column_config.NumberColumn(
                        format='%.2f'
                    ),
                    'Ângulo de Sen (°)': st.column_config.NumberColumn(
                        format='%.2f'
                    ),
                },
            )

    with col_explicacao:
        painel_explicativo('tendencia')


RENDERIZADORES = {
    'temporal': tela_temporal,
    'focalizada': tela_focalizada,
    'distribuicao': tela_distribuicao,
    'tendencia': tela_tendencia,
}

RENDERIZADORES[st.session_state['tela_ativa']]()