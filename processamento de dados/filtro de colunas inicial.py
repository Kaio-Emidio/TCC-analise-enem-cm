from pathlib import Path
import pandas as pd

pasta_entrada = Path("microdados_brutos")
pasta_saida = Path("microdados_filtrados")

pasta_saida.mkdir(parents=True, exist_ok=True)

colunas_de_interesse = [
    "CO_MUNICIPIO_PROVA",
    "NU_NOTA_CN",
    "NU_NOTA_CH",
    "NU_NOTA_LC",
    "NU_NOTA_MT",
    "NU_NOTA_REDACAO",
]

novos_nomes = {
    "CO_MUNICIPIO_PROVA": "Município da Prova",
    "NU_NOTA_CN": "Ciências da Natureza",
    "NU_NOTA_CH": "Ciências Humanas",
    "NU_NOTA_LC": "Linguagens e Códigos",
    "NU_NOTA_MT": "Matemática",
    "NU_NOTA_REDACAO": "Redação",
}

for arquivo in pasta_entrada.glob("*.csv"):
    caminho_final = pasta_saida / arquivo.name

    if caminho_final.exists():
        print(f"Ignorando '{arquivo.name}' (já processado).\n")
        continue

    print(f"Processando '{arquivo.name}'...")

    # Leitura otimizada e renomeação
    tabela_filtrada = pd.read_csv(
        arquivo,
        encoding="latin-1",
        delimiter=";",
        usecols=colunas_de_interesse,
    ).rename(columns=novos_nomes)

    # Exportação
    tabela_filtrada.to_csv(
        caminho_final, sep=";", index=False, encoding="utf-8-sig"
    )

    # Impressão das colunas do arquivo recém-salvo
    colunas_finais = list(tabela_filtrada.columns)
    print(f"✓ Concluído: '{arquivo.name}'")
    print(f"  Colunas do arquivo final: {colunas_finais}\n")