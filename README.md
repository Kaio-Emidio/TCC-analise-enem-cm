# TCC - Análise de dados históricos do ENEM na Grande Natal
Aplicação web usando Streamlit para exibir um dashboard apresentando os dados analisados

## Exportação das tabelas
Ao iniciar o dashboard, o projeto cria `Tabelas_graficos/medias_enem_por_municipio.xlsx`
se o arquivo ainda não existir ou estiver sem as colunas de contagem. A planilha contém
uma aba para cada município, as médias anuais de cada prova, a média geral e a
quantidade de participantes do ENEM por dependência administrativa (federal, estadual,
municipal e privada). Essa contagem considera o município onde o participante fez a
prova e a dependência da escola informada no microdado; não representa o total de alunos
matriculados no município.

Para recriar a planilha, altere a chamada `criar_tabelas(recriar=False)` em `app.py`
para `criar_tabelas(recriar=True)`. Depois da recriação, volte o parâmetro para `False`
para que o arquivo existente seja reutilizado nas próximas inicializações.
Os arquivos Parquet antigos são reprocessados automaticamente quando não contêm a nova
coluna, desde que o CSV original esteja em `microdados_brutos`. O processamento lê os CSVs
em blocos para reduzir o consumo de memória. Anos sem CSV e sem Parquet são ignorados e
indicados no dashboard. Se um ano não possuir `TP_DEPENDENCIA_ADM_ESC`, as contagens por
rede ficam indisponíveis e serão exibidas em branco.

## Pré-requisitos
- Python 3.12 ou superior;
- Git (opcional, caso o projeto seja obtido de um repositório);

## Instalação
### 1. Obtenha o projeto
Clone o repositório ou copie os arquivos para a máquina e entre na pasta do projeto:

```bash
git clone [<URL_DO_REPOSITORIO>](https://github.com/Kaio-Emidio/TCC-analise-enem-cm.git)
cd info4v-prog-int
```
