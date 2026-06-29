from django.shortcuts import render
from datetime import datetime, timedelta
import json
from core.services.ana import buscar_dados_painel, ESTACOES, ESTACOES_POR_REGIAO


def home(request):
    codigo = request.GET.get("estacao", "15630000")
    if codigo not in ESTACOES:
        codigo = "15630000"

    hoje = datetime.now()
    data_fim_default    = hoje.strftime("%Y-%m-%d")
    data_inicio_default = (hoje - timedelta(days=30)).strftime("%Y-%m-%d")

    data_inicio_input = request.GET.get("data_inicio", data_inicio_default)
    data_fim_input    = request.GET.get("data_fim",    data_fim_default)

    try:
        di = datetime.strptime(data_inicio_input, "%Y-%m-%d").strftime("%d/%m/%Y")
        df = datetime.strptime(data_fim_input,    "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        di = (hoje - timedelta(days=30)).strftime("%d/%m/%Y")
        df = hoje.strftime("%d/%m/%Y")
        data_inicio_input = (hoje - timedelta(days=30)).strftime("%Y-%m-%d")
        data_fim_input    = hoje.strftime("%Y-%m-%d")

    dados = buscar_dados_painel(codigo, di, df)

    chart_labels = json.dumps([d["data"] for d in dados.get("diarios", [])])
    chart_atual  = json.dumps([d["nivel_medio"] for d in dados.get("diarios", [])])
    chart_ant    = json.dumps([d["nivel_medio"] for d in dados.get("diarios_ant", [])])

    # Atalhos de período calculados aqui, sem depender de filtros do template
    fim = hoje.strftime("%Y-%m-%d")
    atalhos = [
        {"label": "7 dias",  "inicio": (hoje - timedelta(days=7)).strftime("%Y-%m-%d"),  "fim": fim},
        {"label": "15 dias", "inicio": (hoje - timedelta(days=15)).strftime("%Y-%m-%d"), "fim": fim},
        {"label": "30 dias", "inicio": (hoje - timedelta(days=30)).strftime("%Y-%m-%d"), "fim": fim},
        {"label": "60 dias", "inicio": (hoje - timedelta(days=60)).strftime("%Y-%m-%d"), "fim": fim},
        {"label": "90 dias", "inicio": (hoje - timedelta(days=90)).strftime("%Y-%m-%d"), "fim": fim},
    ]

    return render(request, "home.html", {
        "dados":               dados,
        "estacoes_por_regiao": ESTACOES_POR_REGIAO,
        "selecionada":         codigo,
        "data_inicio":         data_inicio_input,
        "data_fim":            data_fim_input,
        "chart_labels":        chart_labels,
        "chart_atual":         chart_atual,
        "chart_ant":           chart_ant,
        "atalhos":             atalhos,
    })