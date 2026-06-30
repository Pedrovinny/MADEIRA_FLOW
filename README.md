# MADEIRA FLOW

Sistema web de monitoramento hidrométrico do Rio Madeira e bacias adjacentes, com dados em tempo real fornecidos pela **ANA** (Agência Nacional de Águas e Saneamento Básico).

---

## Visão geral

O MADEIRA FLOW consulta o serviço SOAP de telemetria da ANA (`telemetriaws1.ana.gov.br`) e exibe, em uma única página, indicadores de nível d'água para estações selecionadas, incluindo comparativo com o mesmo período do ano anterior.

---

## Funcionalidades

- Seleção de estação por região (Rio Madeira — RO/AM, Rio Amazonas, Rio Purus, Rio Juruá)
- Filtro de período com atalhos rápidos: 7, 15, 30, 60 e 90 dias
- Cards KPI: nível atual, variação anual, máxima/mínima/amplitude e média do período
- Gráfico de linha (Chart.js) com médias diárias — ano atual vs. ano anterior
- Tabela comparativa diária com badge de tendência (Normal / Acima / Muito acima / Abaixo / Muito abaixo)

---

## Estações monitoradas

| Região | Código | Cidade |
|---|---|---|
| Rio Madeira — Rondônia | 15020000 | Guajará-Mirim |
| Rio Madeira — Rondônia | 15320000 | Abunã |
| Rio Madeira — Rondônia | 15400000 | Porto Velho |
| Rio Madeira — Amazonas | 15600000 | Manicoré |
| Rio Madeira — Amazonas | 15630000 | Humaitá *(padrão)* |
| Rio Madeira — Amazonas | 15800000 | Borba |
| Rio Madeira — Amazonas | 15870000 | Nova Olinda do Norte |
| Rio Amazonas | 11400000 | Óbidos |
| Rio Amazonas | 11650000 | Itacoatiara |
| Rio Amazonas | 11800000 | Parintins |
| Rio Purus | 12900000 | Lábrea |
| Rio Purus | 13100000 | Boca do Acre |
| Rio Juruá | 13900000 | Juruá |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Django 6.0 |
| SOAP client | zeep 4.3 + lxml 6.1 |
| Banco de dados | SQLite (modelos definidos, dados servidos via API) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons 1.11 |
| Gráficos | Chart.js 4.4 |

---

## Estrutura do projeto

```
MADEIRA_FLOW/
├── core/
│   ├── models.py          # Modelos Estacao e Medicao
│   ├── views.py           # View principal (home)
│   └── services/
│       └── ana.py         # Integração com a API SOAP da ANA
├── templates/
│   ├── base.html          # Layout base (navbar, Bootstrap, Chart.js)
│   └── home.html          # Página principal (filtros, KPIs, gráfico, tabela)
├── teste/                 # Configurações do projeto Django
│   ├── settings.py
│   └── urls.py
├── manage.py
└── requirements.txt
```

---

## Modelos

### `Estacao`
Representa uma estação hidrométrica cadastrada.

| Campo | Tipo | Descrição |
|---|---|---|
| `codigo_ana` | CharField (único) | Código da estação na ANA |
| `nome` | CharField | Nome da cidade/estação |
| `municipio` | CharField | Município |
| `estado` | CharField (2) | UF |
| `rio` | CharField | Nome do rio |
| `latitude` / `longitude` | FloatField | Coordenadas geográficas |
| `cota_atencao` | FloatField | Nível de atenção (cm) |
| `cota_alerta` | FloatField | Nível de alerta (cm) |
| `cota_inundacao` | FloatField | Nível de inundação (cm) |
| `ativo` | BooleanField | Se a estação está ativa |

### `Medicao`
Registro de uma leitura hidrométrica vinculada a uma estação.

| Campo | Tipo | Descrição |
|---|---|---|
| `estacao` | ForeignKey | Estação relacionada |
| `data_hora` | DateTimeField | Data e hora da medição |
| `nivel` | FloatField | Nível do rio (cm) |
| `vazao` | FloatField (opcional) | Vazão (m³/s) |
| `chuva` | FloatField (opcional) | Precipitação (mm) |

---

## Fluxo de dados (`core/services/ana.py`)

```
buscar_dados_painel(codigo, data_inicio, data_fim)
    │
    ├── _chamar_api()          → requisição SOAP à ANA
    ├── _extrair_medicoes()    → parse do XML de resposta
    ├── _agregar_diario()      → média diária dos níveis
    │
    ├── (mesmo período, ano anterior) → _chamar_api() + _extrair_medicoes() + _agregar_diario()
    │
    └── retorna dict com:
        nivel_atual, nivel_max, nivel_min, nivel_medio, amplitude,
        variacao_anual, diarios, diarios_ant, tabela comparativa
```

---

## Instalação e execução

```powershell
# 1. Criar e ativar ambiente virtual
py -m venv venv
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\venv\Scripts\Activate.ps1

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Aplicar migrações
python manage.py migrate

# 4. Iniciar servidor
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

---

## Parâmetros de URL

A view `home` aceita os seguintes query parameters via GET:

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `estacao` | `15630000` | Código ANA da estação |
| `data_inicio` | hoje − 30 dias | Data inicial (`YYYY-MM-DD`) |
| `data_fim` | hoje | Data final (`YYYY-MM-DD`) |

Exemplo: `/?estacao=15400000&data_inicio=2026-01-01&data_fim=2026-06-30`

---

## Dependências principais

```
Django==6.0.6
zeep==4.3.3
lxml==6.1.1
requests==2.34.2
```

Lista completa em [requirements.txt](requirements.txt).
