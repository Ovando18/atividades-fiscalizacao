"""Base de dados embutida — Regiões de Fiscalização 2027 do Crea-MS (DFI)."""

# ---------------------------------------------------------------------------
# Microrregiões, agentes e municípios vinculados (Regiões Fiscalização 2027)
# ---------------------------------------------------------------------------
MICRORREGIOES_2027 = [
    {"numero": "01", "agente": "GUILHERME",
     "municipios": ["Angélica", "Ivinhema", "Glória de Dourados", "Deodápolis"]},
    {"numero": "02", "agente": "CELSO",
     "municipios": ["Terenos", "Dois Irmãos do Buriti", "Aquidauana", "Anastácio"]},
    {"numero": "03", "agente": "SHELLTON",
     "municipios": ["Bonito", "Bela Vista", "Porto Murtinho", "Caracol"]},
    {"numero": "04", "agente": "CÉSAR",
     "municipios": ["Corumbá", "Ladário", "Miranda", "Bodoquena"]},
    {"numero": "05", "agente": "DIOGO",
     "municipios": ["Chapadão do Sul", "Costa Rica", "Paraíso das Águas"]},
    {"numero": "06", "agente": "ANTONIO",
     "municipios": ["Coxim", "Sonora", "Pedro Gomes", "Alcinópolis"]},
    {"numero": "07", "agente": "ROGÉRIO",
     "municipios": ["Fátima do Sul", "Vicentina", "Jateí", "Itaporã", "Douradina"]},
    {"numero": "08", "agente": "MARCELINO",
     "municipios": ["São Gabriel do Oeste", "Rio Verde de Mato Grosso", "Camapuã", "Figueirão"]},
    {"numero": "09", "agente": "MÁRCIO",
     "municipios": ["Nova Andradina", "Batayporã", "Taquarussu", "Novo Horizonte do Sul"]},
    {"numero": "10", "agente": "ADALBERTO",
     "municipios": ["Ponta Porã", "Antônio João", "Aral Moreira", "Maracaju"]},
    {"numero": "11", "agente": "DAYANE",
     "municipios": ["Rio Brilhante", "Nova Alvorada do Sul", "Ribas do Rio Pardo", "Água Clara"]},
    {"numero": "12", "agente": "EDILBERTO",
     "municipios": ["Jaraguari", "Bandeirantes", "Rio Negro", "Corguinho", "Rochedo"]},
    {"numero": "13", "agente": "THARLEY",
     "municipios": ["Sidrolândia", "Nioaque", "Jardim", "Guia Lopes da Laguna"]},
    {"numero": "14", "agente": "JOSÉ EDUARDO",
     "municipios": ["Amambai", "Coronel Sapucaia", "Paranhos", "Sete Quedas", "Tacuru"]},
    {"numero": "15", "agente": "DERICK",
     "municipios": ["Iguatemi", "Itaquiraí", "Eldorado", "Mundo Novo", "Japorã"]},
    {"numero": "16", "agente": "ALISON",
     "municipios": ["Naviraí", "Laguna Carapã", "Caarapó", "Juti"]},
    {"numero": "17", "agente": "JUAREZ",
     "municipios": ["Aparecida do Taboado", "Selvíria", "Cassilândia", "Inocência"]},
    {"numero": "18", "agente": "LUIZ",
     "municipios": ["Brasilândia", "Santa Rita do Pardo", "Bataguassu", "Anaurilândia"]},
]

# Acesso rápido por nome do agente
AGENTES = {r["agente"]: r for r in MICRORREGIOES_2027}

# ---------------------------------------------------------------------------
# Os 79 municípios de Mato Grosso do Sul (ordem alfabética)
# ---------------------------------------------------------------------------
MUNICIPIOS_MS = [
    "Água Clara", "Alcinópolis", "Amambai", "Anastácio", "Anaurilândia",
    "Angélica", "Antônio João", "Aparecida do Taboado", "Aquidauana",
    "Aral Moreira", "Bandeirantes", "Bataguassu", "Batayporã", "Bela Vista",
    "Bodoquena", "Bonito", "Brasilândia", "Caarapó", "Camapuã",
    "Campo Grande", "Caracol", "Cassilândia", "Chapadão do Sul", "Corguinho",
    "Coronel Sapucaia", "Corumbá", "Costa Rica", "Coxim", "Deodápolis",
    "Dois Irmãos do Buriti", "Douradina", "Dourados", "Eldorado",
    "Fátima do Sul", "Figueirão", "Glória de Dourados", "Guia Lopes da Laguna",
    "Iguatemi", "Inocência", "Itaporã", "Itaquiraí", "Ivinhema", "Japorã",
    "Jaraguari", "Jardim", "Jateí", "Juti", "Ladário", "Laguna Carapã",
    "Maracaju", "Miranda", "Mundo Novo", "Naviraí", "Nioaque",
    "Nova Alvorada do Sul", "Nova Andradina", "Novo Horizonte do Sul",
    "Paraíso das Águas", "Paranaíba", "Paranhos", "Pedro Gomes", "Ponta Porã",
    "Porto Murtinho", "Ribas do Rio Pardo", "Rio Brilhante", "Rio Negro",
    "Rio Verde de Mato Grosso", "Rochedo", "Santa Rita do Pardo",
    "São Gabriel do Oeste", "Selvíria", "Sete Quedas", "Sidrolândia", "Sonora",
    "Tacuru", "Taquarussu", "Terenos", "Três Lagoas", "Vicentina",
]

# ---------------------------------------------------------------------------
# Atividades fiscalizáveis (ordem alfabética)
# ---------------------------------------------------------------------------
ATIVIDADES = [
    "Aeroporto",
    "Armazém",
    "Aterro Sanitário",
    "Aviação Agrícola",
    "Avicultura",
    "Banco Financeiro - Lotérica",
    "Cartório",
    "Casas de Show, Clubes, Boates",
    "Clínicas",
    "Concreteiras",
    "Condomínios",
    "Construtoras / Escritório de Engenharia",
    "Curtume",
    "Emissora de TV e Rádio",
    "Empresas de Alarme",
    "Empresas de Telecomunicação",
    "Estação de Tratamento de Água e Esgoto",
    "Estádio / Ginásio",
    "Eventos",
    "Frigoríficos",
    "Hospitais",
    "Hotel / Pousadas / Motel",
    "Igrejas e Templos",
    "Indústria",
    "Instituição de Ensino",
    "Laticínios",
    "Lavoura",
    "Lavoura Urbana",
    "Lojas (Comércio)",
    "Mecânicas",
    "Mineração",
    "Naval",
    "Obras Civis",
    "Piscicultura",
    "Posto de Combustível",
    "Prefeituras",
    "Revendas de Defensivos Agrícolas",
    "Shopping",
    "Silvicultura",
    "Sistemas de Geração de Energia Fotovoltaica",
    "Suinocultura",
    "Supermercados",
    "Usina de Álcool e Açúcar",
    "Usina Hidrelétrica",
]

# Atividades marcadas por padrão ao abrir / restaurar o formulário
ATIVIDADES_PADRAO = [
    "Eventos",
    "Obras Civis",
    "Prefeituras",
    "Sistemas de Geração de Energia Fotovoltaica",
]

assert len(MUNICIPIOS_MS) == 79, len(MUNICIPIOS_MS)
assert all(m in MUNICIPIOS_MS for r in MICRORREGIOES_2027 for m in r["municipios"])
assert all(a in ATIVIDADES for a in ATIVIDADES_PADRAO)
