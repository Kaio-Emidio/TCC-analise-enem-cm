from pathlib import Path

class Config:
    PASTA_PROJETO = Path(__file__).resolve().parent
    PASTA_ENTRADA = PASTA_PROJETO / "microdados_brutos"
    PASTA_SAIDA = PASTA_PROJETO / "microdados_filtrados"

    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

    COLUNAS_DE_INTERESSE = [
        "CO_MUNICIPIO_PROVA",
        "NU_NOTA_CN",
        "NU_NOTA_CH",
        "NU_NOTA_LC",
        "NU_NOTA_MT",
        "NU_NOTA_REDACAO",
    ]

    NOVOS_NOMES = {
        "CO_MUNICIPIO_PROVA": "Município da Prova",
        "NU_NOTA_CN": "Ciências da Natureza",
        "NU_NOTA_CH": "Ciências Humanas",
        "NU_NOTA_LC": "Linguagens e Códigos",
        "NU_NOTA_MT": "Matemática",
        "NU_NOTA_REDACAO": "Redação",
    }

    CODIGOS_MUNICIPIOS = {
        "Ceará-Mirim": 2402600,
        "Natal": 2408102,
        "Parnamirim": 2403251,
        "Extremoz": 2403608,
        "São Gonçalo do Amarante": 2412005,
        "Macaíba": 2407104,
    }