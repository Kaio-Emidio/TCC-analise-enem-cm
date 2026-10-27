from uuid import uuid4

import pandas as pd
from fastparquet import ParquetFile, write
from config import Config

class Filtrar:
    @staticmethod
    def filtrar_colunas(anos: list[int] | None = None):
        if anos is None:
            arquivos = sorted(Config.PASTA_ENTRADA.glob("*.csv"))
        else:
            arquivos = [
                Config.PASTA_ENTRADA / f"MICRODADOS_ENEM_{ano}.csv"
                for ano in anos
            ]

        if not arquivos:
            print(f"Nenhum arquivo CSV encontrado em: '{Config.PASTA_ENTRADA}'")

        arquivos_para_processar = []
        anos_sem_dependencia = []
        anos_sem_dados = []
        anos_processados = []
        colunas_requeridas = set(Config.NOVOS_NOMES.values())

        for arquivo in arquivos:
            caminho_final = Config.PASTA_SAIDA / f"{arquivo.stem}.parquet"

            if caminho_final.exists():
                colunas_parquet = set(ParquetFile(str(caminho_final)).columns)
                if colunas_requeridas.issubset(colunas_parquet):
                    print(f"Ignorando '{arquivo.name}' (já processado como parquet).\n")
                    continue
                if not arquivo.exists():
                    ano = int(arquivo.stem.rsplit("_", 1)[1])
                    anos_sem_dependencia.append(ano)
                    print(
                        f"Aviso: '{arquivo.name}' não está disponível para atualizar "
                        f"o Parquet; contagens por rede de {ano} ficarão indisponíveis."
                    )
                    continue
                print(f"Atualizando '{caminho_final.name}' para incluir novas colunas...")
            elif not arquivo.exists():
                ano = int(arquivo.stem.rsplit("_", 1)[1])
                anos_sem_dados.append(ano)
                print(
                    f"Aviso: '{arquivo.name}' e o Parquet correspondente não "
                    "estão disponíveis; esse ano será ignorado."
                )
                continue

            arquivos_para_processar.append(arquivo)

        for arquivo in arquivos_para_processar:
            print(f"Processando '{arquivo.name}'...")
            ano = int(arquivo.stem.rsplit("_", 1)[1])
            caminho_final = Config.PASTA_SAIDA / f"{arquivo.stem}.parquet"

            colunas_csv = pd.read_csv(
                arquivo,
                encoding="latin-1",
                delimiter=";",
                nrows=0,
            ).columns
            colunas_disponiveis = [
                coluna
                for coluna in Config.COLUNAS_DE_INTERESSE
                if coluna in colunas_csv
            ]
            colunas_obrigatorias = [
                coluna
                for coluna in Config.COLUNAS_DE_INTERESSE
                if coluna != "TP_DEPENDENCIA_ADM_ESC"
            ]
            colunas_ausentes = [
                coluna for coluna in colunas_obrigatorias
                if coluna not in colunas_csv
            ]
            if colunas_ausentes:
                raise ValueError(
                    f"Colunas obrigatórias ausentes em '{arquivo.name}': "
                    f"{', '.join(colunas_ausentes)}"
                )

            if "TP_DEPENDENCIA_ADM_ESC" not in colunas_csv:
                anos_sem_dependencia.append(ano)
                print(
                    f"Aviso: '{arquivo.name}' não contém TP_DEPENDENCIA_ADM_ESC; "
                    "as contagens por rede ficarão indisponíveis neste ano."
                )

            temporary_path = (
                Config.PASTA_SAIDA
                / f"{arquivo.stem}.{uuid4().hex}.tmp.parquet"
            )

            tipos_colunas = {coluna: "float64" for coluna in colunas_disponiveis}
            primeiro_bloco = True
            colunas_finais = [
                Config.NOVOS_NOMES[coluna] for coluna in colunas_disponiveis
            ]
            if "TP_DEPENDENCIA_ADM_ESC" not in colunas_disponiveis:
                colunas_finais.append("Dependência administrativa")

            try:
                blocos = pd.read_csv(
                    arquivo,
                    encoding="latin-1",
                    delimiter=";",
                    usecols=colunas_disponiveis,
                    dtype=tipos_colunas,
                    chunksize=100_000,
                )
                for bloco in blocos:
                    bloco = bloco.rename(columns=Config.NOVOS_NOMES)
                    if "Dependência administrativa" not in bloco.columns:
                        bloco["Dependência administrativa"] = float("nan")

                    write(
                        str(temporary_path),
                        bloco,
                        write_index=False,
                        append=not primeiro_bloco,
                    )
                    primeiro_bloco = False

                if primeiro_bloco:
                    write(
                        str(temporary_path),
                        pd.DataFrame(columns=colunas_finais),
                        write_index=False,
                    )

                temporary_path.replace(caminho_final)
            finally:
                if temporary_path.exists():
                    temporary_path.unlink()

            anos_processados.append(ano)
            print(f"Concluído: '{caminho_final.name}'")
            print(f"  Colunas do arquivo final: {colunas_finais}\n")

        return {
            "anos_sem_dependencia": sorted(set(anos_sem_dependencia)),
            "anos_sem_dados": sorted(set(anos_sem_dados)),
            "anos_processados": sorted(set(anos_processados)),
        }

    @staticmethod
    def filtrar_cidade(cidades: list, df: pd.DataFrame):
        if df.empty or not cidades:
            return df.copy()

        codigos_municipios = []
        for c in cidades:
            # Se for nome de cidade, pega do dicionário. Se já for o código ou não achar, mantém o valor original.
            codigo = Config.CODIGOS_MUNICIPIOS.get(c, c)
            codigos_municipios.append(codigo)
            
            # Adiciona também a versão em string/int para evitar inconsistência de tipos
            try:
                codigos_municipios.append(int(codigo))
            except (ValueError, TypeError):
                pass

        # Garante tipo compatível na coluna antes da busca
        df_filtrado = df[df['Município da Prova'].isin(codigos_municipios)].copy()
        
        return df_filtrado

    @staticmethod
    def codigo_para_municipio():
        dict_codigos = {}
        for cidade, codigo in Config.CODIGOS_MUNICIPIOS.items():
            # Mapeia tanto a chave de número inteiro quanto texto (ex: 240260 e '240260')
            dict_codigos[codigo] = cidade
            try:
                dict_codigos[int(codigo)] = cidade
            except (ValueError, TypeError):
                pass
        return dict_codigos