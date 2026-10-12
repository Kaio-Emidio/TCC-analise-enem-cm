# TCC - Análise de dados históricos do ENEM na Grande Natal
Aplicação web usando Streamlit para exibir um dashboard apresentando os dados analisados

## Exportação das tabelas
Ao iniciar o dashboard, o projeto cria `Tabelas_graficos/medias_enem_por_municipio.xlsx`
se o arquivo ainda não existir. A planilha contém uma aba para cada município e as
médias anuais de cada prova, além da média geral.

Para recriar a planilha, altere a chamada `criar_tabelas(recriar=False)` em `app.py`
para `criar_tabelas(recriar=True)`. Depois da recriação, volte o parâmetro para `False`
para que o arquivo existente seja reutilizado nas próximas inicializações.

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
