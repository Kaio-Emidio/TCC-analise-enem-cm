import pandas as pd
from config import Config

class Filtrar:
    def filtrar_colunas():
        arquivos = list(Config.PASTA_ENTRADA.glob("*.csv"))

        if not arquivos:
            print(f"Nenhum arquivo CSV encontrado em: '{Config.PASTA_ENTRADA}'")

        for arquivo in arquivos:
            # Define o caminho de saída trocando a extensão .csv por .parquet
            caminho_final = Config.PASTA_SAIDA / f"{arquivo.stem}.parquet"

            if caminho_final.exists():
                print(f"Ignorando '{arquivo.name}' (já processado como parquet).\n")
                continue

            print(f"Processando '{arquivo.name}'...")

            # Leitura otimizada e renomeação
            tabela_filtrada = pd.read_csv(
                arquivo,
                encoding="latin-1",
                delimiter=";",
                usecols=Config.COLUNAS_DE_INTERESSE,
            ).rename(columns=Config.NOVOS_NOMES)

            # Exportação para Parquet com compressão snappy (padrão do pandas, super rápida)
            tabela_filtrada.to_parquet(caminho_final, index=False)

            # Impressão das colunas do arquivo recém-salvo
            colunas_finais = list(tabela_filtrada.columns)
            print(f"✓ Concluído: '{caminho_final.name}'")
            print(f"  Colunas do arquivo final: {colunas_finais}\n")

    def filtrar_cidade(cidades: list, df: pd.DataFrame):
        codigos_municipios = [Config.CODIGOS_MUNICIPIOS[cidade] for cidade in cidades]
        df_filtrado = df[df['Município da Prova'].isin(codigos_municipios)].copy()
        df_filtrado = df_filtrado.dropna()
        return df_filtrado

    def codigo_para_municipio():
        return {
            codigo: cidade
            for cidade, codigo in Config.CODIGOS_MUNICIPIOS.items()
        }