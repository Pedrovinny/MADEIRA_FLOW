from zeep import Client, Settings
from zeep.plugins import HistoryPlugin
from datetime import datetime, timedelta
from collections import defaultdict

WSDL = "https://telemetriaws1.ana.gov.br/ServiceANA.asmx?WSDL"

ESTACOES_POR_REGIAO = {
    "Rio Madeira — Rondônia": {
        "15020000": "Guajará-Mirim",
        "15320000": "Abunã",
        "15400000": "Porto Velho",
    },
    "Rio Madeira — Amazonas": {
        "15600000": "Manicoré",
        "15630000": "Humaitá",
        "15800000": "Borba",
        "15870000": "Nova Olinda do Norte",
    },
    "Rio Amazonas": {
        "11400000": "Óbidos",
        "11650000": "Itacoatiara",
        "11800000": "Parintins",
    },
    "Rio Purus": {
        "12900000": "Lábrea",
        "13100000": "Boca do Acre",
    },
    "Rio Juruá": {
        "13900000": "Juruá",
    },
}

ESTACOES = {
    codigo: nome
    for regiao in ESTACOES_POR_REGIAO.values()
    for codigo, nome in regiao.items()
}


def _chamar_api(codigo, data_inicio, data_fim):
    history = HistoryPlugin()
    try:
        cliente = Client(WSDL, settings=Settings(strict=False), plugins=[history])
        cliente.service.DadosHidrometeorologicos(codigo, data_inicio, data_fim)
    except Exception:
        pass
    return history.last_received.get("envelope")


def _extrair_medicoes(envelope):
    if envelope is None:
        return []

    error_el = next(
        (el for el in envelope.iter() if el.tag.split("}")[-1] == "Error"), None
    )
    if error_el is not None and error_el.text:
        return []

    registros = [
        el for el in envelope.iter()
        if el.tag.split("}")[-1] == "DadosHidrometereologicos"
    ]

    def campo(el, tag):
        c = next((c for c in el if c.tag.split("}")[-1] == tag), None)
        return c.text.strip() if c is not None and c.text else None

    medicoes = []
    for reg in registros:
        data_str = campo(reg, "DataHora")
        nivel_str = campo(reg, "Nivel")
        if not data_str or not nivel_str:
            continue
        try:
            vazao_str = campo(reg, "Vazao")
            chuva_str = campo(reg, "Chuva")
            medicoes.append({
                "data_hora": data_str,
                "nivel": float(nivel_str),
                "vazao": float(vazao_str) if vazao_str else None,
                "chuva": float(chuva_str) if chuva_str else None,
            })
        except ValueError:
            pass

    medicoes.sort(key=lambda x: x["data_hora"])
    return medicoes


def _agregar_diario(medicoes):
    por_dia = defaultdict(list)
    for m in medicoes:
        por_dia[m["data_hora"][:10]].append(m["nivel"])
    return [
        {"data": dia, "nivel_medio": round(sum(v) / len(v), 2)}
        for dia, v in sorted(por_dia.items())
    ]


def _ano_anterior(dt):
    try:
        return dt.replace(year=dt.year - 1)
    except ValueError:  # 29 de fev em ano não bissexto
        return dt.replace(year=dt.year - 1, day=28)


def buscar_dados_painel(codigo, data_inicio_str, data_fim_str):
    fmt = "%d/%m/%Y"

    # Período atual
    envelope = _chamar_api(codigo, data_inicio_str, data_fim_str)
    medicoes = _extrair_medicoes(envelope)

    if not medicoes:
        return {"erro": "Nenhum dado encontrado para o período selecionado."}

    diarios = _agregar_diario(medicoes)
    niveis = [m["nivel"] for m in medicoes]
    mais_recente = medicoes[-1]

    # Mesmo período no ano anterior
    di_dt = datetime.strptime(data_inicio_str, fmt)
    df_dt = datetime.strptime(data_fim_str, fmt)
    di_ant = _ano_anterior(di_dt).strftime(fmt)
    df_ant = _ano_anterior(df_dt).strftime(fmt)

    envelope_ant = _chamar_api(codigo, di_ant, df_ant)
    medicoes_ant = _extrair_medicoes(envelope_ant)
    diarios_ant = _agregar_diario(medicoes_ant)

    nivel_ano_ant = medicoes_ant[-1]["nivel"] if medicoes_ant else None
    variacao = (
        round(mais_recente["nivel"] - nivel_ano_ant, 2)
        if nivel_ano_ant else None
    )

    # Tabela comparativa (mais recente primeiro, alinhada por posição)
    tabela = []
    for i, d in enumerate(reversed(diarios)):
        j = len(diarios_ant) - 1 - i
        nivel_ant = diarios_ant[j]["nivel_medio"] if 0 <= j < len(diarios_ant) else None
        diff = round(d["nivel_medio"] - nivel_ant, 2) if nivel_ant is not None else None
        tabela.append({
            "data": d["data"],
            "nivel_atual": d["nivel_medio"],
            "nivel_ant": nivel_ant,
            "diff": diff,
        })

    return {
        "estacao": ESTACOES.get(codigo, f"Estação {codigo}"),
        "codigo": codigo,
        "nivel_atual": mais_recente["nivel"],
        "data_atual": mais_recente["data_hora"],
        "nivel_max": max(niveis),
        "nivel_min": min(niveis),
        "nivel_medio": round(sum(niveis) / len(niveis), 2),
        "amplitude": round(max(niveis) - min(niveis), 2),
        "nivel_ano_ant": nivel_ano_ant,
        "variacao_anual": variacao,
        "ano_atual": df_dt.year,
        "ano_anterior": df_dt.year - 1,
        "diarios": diarios,
        "diarios_ant": diarios_ant,
        "tabela": tabela,
        "total_medicoes": len(medicoes),
    }