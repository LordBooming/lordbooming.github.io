#!/usr/bin/env python3
"""WorldForge RPG — gerador procedural de mundos de fantasia.

Requer Python 3.10+ e usa apenas a biblioteca padrão.
Exemplo:
  python worldforge_rpg.py --seed 2026 --reinos 3 --cidades 2 --npcs 3 --missoes 5 --saida mundo.json
"""
from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSAO = "1.2.0"

REINOS = [
    {"nome": "Aurelion", "governo": "monarquia", "bioma": "planícies douradas", "cultura": "cavaleiros juramentados", "recurso": "trigo e ouro", "conflito": "disputa pela sucessão do trono"},
    {"nome": "Névoa Alta", "governo": "conselho arcano", "bioma": "montanhas cobertas por névoa", "cultura": "magos e estudiosos", "recurso": "cristais arcanos", "conflito": "experimentos mágicos fora de controle"},
    {"nome": "Varkhûn", "governo": "clãs guerreiros", "bioma": "estepes frias", "cultura": "clãs nômades", "recurso": "ferro e cavalos", "conflito": "rivalidade entre chefes de clã"},
    {"nome": "Sylvaran", "governo": "círculo druídico", "bioma": "florestas antigas", "cultura": "guardiões da natureza", "recurso": "ervas raras e madeira viva", "conflito": "uma praga corrompe as raízes"},
    {"nome": "Thalássia", "governo": "liga mercante", "bioma": "ilhas e costas tropicais", "cultura": "navegadores e comerciantes", "recurso": "pérolas e especiarias", "conflito": "piratas bloqueiam as rotas marítimas"},
    {"nome": "Drakemarch", "governo": "principado militar", "bioma": "terras vulcânicas", "cultura": "artífices e caçadores de dragões", "recurso": "obsidiana e aço negro", "conflito": "sinais de um dragão ancestral"},
    {"nome": "Umbrafell", "governo": "dinastia secreta", "bioma": "pântanos sombrios", "cultura": "oráculos e contrabandistas", "recurso": "fungos medicinais", "conflito": "desaparecimentos nas aldeias"},
    {"nome": "Lúmenor", "governo": "teocracia", "bioma": "desertos de vidro", "cultura": "peregrinos e astrônomos", "recurso": "sal e vidro encantado", "conflito": "uma estrela caiu perto da capital"},
]

PREFIXOS_CIDADE = ["Val", "Eld", "Brum", "Cor", "Dour", "Ar", "Bel", "Mir", "Tor", "Vel", "Sol", "Raven", "Cal", "Nym", "Astra", "Ferro", "Luar", "Pedra"]
_SUFIXOS_CIDADE = ["gard", "mar", "dell", "vila", "bruma", "dora", "heim", "ária", "torre", "vale", "ponte", "lume", "forte", "ria", "mor"]

NOMES_NPC = ["Ariane", "Bram", "Cael", "Darian", "Elira", "Fenn", "Galen", "Helena", "Ilyan", "Jora", "Kaelen", "Liora", "Marek", "Neris", "Orin", "Petra", "Quinn", "Riven", "Sora", "Tavian", "Una", "Vesper", "Wylan", "Yara", "Zorin"]
SOBRENOMES = ["Pedraforte", "Folhalva", "Corvaneve", "Douraluz", "Ventor", "Cinzental", "Riosombra", "Ferrovale", "Luares", "Brumaclara", "Solferro", "Mornavento"]
PAPEIS = ["ferreiro", "curandeira", "batedor", "mercadora", "guarda", "erudito", "caçadora", "taverneiro", "mensageira", "cartógrafo", "sacerdotisa", "contrabandista"]
TRACOS = ["honrado", "ambicioso", "desconfiado", "curioso", "generoso", "reservado", "impulsivo", "calculista", "idealista", "supersticioso"]

MONSTROS = [
    {"nome": "Lobo de Cinza", "nivel": 1, "habitat": "florestas e estradas", "perigo": "baixo"},
    {"nome": "Goblin Saqueador", "nivel": 2, "habitat": "ruínas e cavernas", "perigo": "baixo"},
    {"nome": "Aranha de Cristal", "nivel": 3, "habitat": "minas antigas", "perigo": "moderado"},
    {"nome": "Cavaleiro Oco", "nivel": 5, "habitat": "criptas e campos de batalha", "perigo": "alto"},
    {"nome": "Draco Jovem", "nivel": 7, "habitat": "montanhas e vulcões", "perigo": "muito alto"},
    {"nome": "Espectro do Pântano", "nivel": 4, "habitat": "pântanos e ruínas", "perigo": "alto"},
    {"nome": "Ent de Raízes Negras", "nivel": 6, "habitat": "florestas corrompidas", "perigo": "alto"},
]

OBJETIVOS = ["recuperar", "proteger", "investigar", "escoltar", "derrotar", "entregar", "mapear", "resgatar"]
ALVOS = ["um artefato perdido", "uma caravana desaparecida", "um esconderijo de saqueadores", "um manuscrito antigo", "uma criatura perigosa", "um emissário real", "uma fonte de corrupção", "um relicário sagrado"]
RECOMPENSAS = ["ouro", "equipamento raro", "uma relíquia", "influência política", "informações secretas", "um favor da guilda"]

TIPOS_RELACAO = [
    ("amizade", "confiam um no outro"),
    ("rivalidade", "competem por influência"),
    ("parentesco", "são parentes distantes"),
    ("mentoria", "um ensinou uma habilidade ao outro"),
    ("dívida", "um deve um favor ao outro"),
    ("desconfiança", "escondem informações um do outro"),
]

MODELOS_EVENTO = [
    {"tipo": "político", "titulo": "Disputa por influência", "descricao": "Duas facções disputam o controle de decisões locais.", "impacto": "Aumenta a tensão política e pode alterar alianças."},
    {"tipo": "comercial", "titulo": "Interrupção das rotas comerciais", "descricao": "Uma rota importante ficou perigosa ou bloqueada.", "impacto": "Mercadorias ficam mais caras até a rota ser reaberta."},
    {"tipo": "ameaça", "titulo": "Sinais de atividade monstruosa", "descricao": "Habitantes relatam rastros e ataques incomuns nas proximidades.", "impacto": "Aumenta o risco nas viagens e cria oportunidades de caça."},
    {"tipo": "social", "titulo": "Festival inesperado", "descricao": "Uma celebração reúne viajantes, artistas e comerciantes.", "impacto": "Favorece contatos, rumores e recuperação do ânimo local."},
    {"tipo": "mágico", "titulo": "Anomalia arcana", "descricao": "Uma alteração mágica afeta uma área próxima.", "impacto": "Fenômenos estranhos podem revelar pistas ou perigos."},
    {"tipo": "ambiental", "titulo": "Clima extremo", "descricao": "Uma tempestade, nevasca ou onda de calor atinge a região.", "impacto": "Deslocamentos ficam mais lentos e suprimentos mais valiosos."},
    {"tipo": "criminal", "titulo": "Atividade de contrabandistas", "descricao": "Uma rede clandestina tenta expandir sua influência.", "impacto": "Mercados paralelos surgem e a segurança local é pressionada."},
]


def _slug(texto: str) -> str:
    """Converte um nome em identificador simples e estável."""
    substituicoes = {"á":"a", "à":"a", "ã":"a", "â":"a", "é":"e", "ê":"e", "í":"i", "ó":"o", "ô":"o", "õ":"o", "ú":"u", "ü":"u", "ç":"c", "Á":"a", "É":"e", "Í":"i", "Ó":"o", "Ú":"u"}
    texto = "".join(substituicoes.get(c, c) for c in texto.lower())
    return "".join(c if c.isalnum() else "-" for c in texto).strip("-")


def _nome_cidade(rng: random.Random, usados: set[str]) -> str:
    for _ in range(100):
        nome = rng.choice(PREFIXOS_CIDADE) + rng.choice(_SUFIXOS_CIDADE)
        if nome not in usados:
            usados.add(nome)
            return nome
    nome = f"Cidade-{len(usados) + 1}"
    usados.add(nome)
    return nome


def gerar_mundo(seed: int | None = None, quantidade_reinos: int = 4,
                cidades_por_reino: int = 3, npcs_por_cidade: int = 4,
                quantidade_missoes: int = 8, quantidade_eventos: int = 6) -> dict[str, Any]:
    """Gera um mundo reproduzível quando a mesma seed e parâmetros são usados."""
    if not 1 <= quantidade_reinos <= len(REINOS):
        raise ValueError(f"quantidade_reinos deve estar entre 1 e {len(REINOS)}")
    if not 1 <= cidades_por_reino <= 20:
        raise ValueError("cidades_por_reino deve estar entre 1 e 20")
    if not 0 <= npcs_por_cidade <= 50:
        raise ValueError("npcs_por_cidade deve estar entre 0 e 50")
    if not 0 <= quantidade_missoes <= 200:
        raise ValueError("quantidade_missoes deve estar entre 0 e 200")
    if not 0 <= quantidade_eventos <= 200:
        raise ValueError("quantidade_eventos deve estar entre 0 e 200")

    rng = random.Random(seed)
    modelos_reino = rng.sample(REINOS, quantidade_reinos)
    mundo: dict[str, Any] = {
        "metadata": {
            "nome": f"Crônicas de {rng.choice(['Eldoria', 'Aetherion', 'Valdora', 'Mystral', 'Ordem das Estrelas'])}",
            "versao_gerador": VERSAO,
            "seed": seed,
            "gerado_em_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "estado_mundo": {"turno": 1},
        "reinos": [], "cidades": [], "npcs": [], "monstros": [], "missoes": [],
        "relacoes": [], "eventos": [],
    }
    cidades_usadas: set[str] = set()
    npc_ids: list[str] = []

    for indice, modelo in enumerate(modelos_reino, start=1):
        reino_id = f"reino-{indice:02d}-{_slug(modelo['nome'])}"
        reino = {"id": reino_id, **modelo, "capital_id": None, "cidade_ids": []}
        mundo["reinos"].append(reino)
        for ordem_cidade in range(1, cidades_por_reino + 1):
            cidade_nome = _nome_cidade(rng, cidades_usadas)
            cidade_id = f"cidade-{len(mundo['cidades']) + 1:03d}-{_slug(cidade_nome)}"
            cidade = {
                "id": cidade_id,
                "nome": cidade_nome,
                "reino_id": reino_id,
                "tipo": "capital" if ordem_cidade == 1 else rng.choice(["porto", "vila", "fortaleza", "centro comercial", "cidade acadêmica"]),
                "populacao": rng.randint(800, 90000) if ordem_cidade > 1 else rng.randint(15000, 180000),
                "descricao": f"Assentamento em {modelo['bioma']}, conhecido por {modelo['recurso']}.",
                "npc_ids": [],
            }
            if ordem_cidade == 1:
                reino["capital_id"] = cidade_id
            reino["cidade_ids"].append(cidade_id)
            mundo["cidades"].append(cidade)
            for _ in range(npcs_por_cidade):
                nome_completo = f"{rng.choice(NOMES_NPC)} {rng.choice(SOBRENOMES)}"
                npc_id = f"npc-{len(mundo['npcs']) + 1:04d}"
                npc = {
                    "id": npc_id,
                    "nome": nome_completo,
                    "idade": rng.randint(18, 90),
                    "papel": rng.choice(PAPEIS),
                    "traco": rng.choice(TRACOS),
                    "cidade_id": cidade_id,
                    "reino_id": reino_id,
                    "objetivo_pessoal": rng.choice(["encontrar um parente", "quitar uma dívida", "ganhar prestígio", "descobrir a verdade", "proteger a comunidade", "abandonar o passado"]),
                }
                mundo["npcs"].append(npc)
                cidade["npc_ids"].append(npc_id)
                npc_ids.append(npc_id)

    mundo["monstros"] = [dict(monstro, id=f"monstro-{i:02d}") for i, monstro in enumerate(MONSTROS, start=1)]
    for i in range(1, quantidade_missoes + 1):
        cidade = rng.choice(mundo["cidades"])
        monstro = rng.choice(mundo["monstros"])
        mundo["missoes"].append({
            "id": f"missao-{i:03d}",
            "titulo": f"{rng.choice(['Ecos de', 'O segredo de', 'Perigo em', 'A última esperança de', 'Sombras sobre'])} {cidade['nome']}",
            "objetivo": f"{rng.choice(OBJETIVOS).capitalize()} {rng.choice(ALVOS)}",
            "cidade_origem_id": cidade["id"],
            "reino_id": cidade["reino_id"],
            "ameaca": monstro["nome"],
            "nivel_recomendado": max(1, monstro["nivel"] + rng.randint(-1, 2)),
            "recompensa": rng.choice(RECOMPENSAS),
            "estado": "disponível",
        })

    # Relações sociais: pares únicos, sem autorrelações e com referências válidas.
    if len(npc_ids) >= 2:
        max_relacoes = min(len(npc_ids), len(npc_ids) * (len(npc_ids) - 1) // 2)
        quantidade_relacoes = rng.randint(0, max_relacoes) if max_relacoes else 0
        pares_usados: set[frozenset[str]] = set()
        tentativas = 0
        while len(mundo["relacoes"]) < quantidade_relacoes and tentativas < quantidade_relacoes * 20 + 100:
            tentativas += 1
            npc_a, npc_b = rng.sample(npc_ids, 2)
            par = frozenset((npc_a, npc_b))
            if par in pares_usados:
                continue
            pares_usados.add(par)
            tipo, descricao = rng.choice(TIPOS_RELACAO)
            indice = len(mundo["relacoes"]) + 1
            mundo["relacoes"].append({
                "id": f"relacao-{indice:04d}",
                "npc_a_id": npc_a,
                "npc_b_id": npc_b,
                "tipo": tipo,
                "descricao": descricao,
                "intensidade": rng.randint(1, 5),
            })

    # Eventos iniciais do mundo, todos ligados a uma região existente.
    for indice in range(1, quantidade_eventos + 1):
        mundo["eventos"].append(_criar_evento(mundo, rng, f"evento-{indice:04d}", turno=1))

    validar_mundo(mundo)
    return mundo


def _criar_evento(mundo: dict[str, Any], rng: random.Random, evento_id: str, turno: int) -> dict[str, Any]:
    modelo = rng.choice(MODELOS_EVENTO)
    cidade = rng.choice(mundo["cidades"])
    cidade_npcs = [n for n in mundo["npcs"] if n["cidade_id"] == cidade["id"]]
    npc = rng.choice(cidade_npcs) if cidade_npcs and rng.random() < 0.45 else None
    duracao = rng.randint(2, 6)
    return {
        "id": evento_id,
        "tipo": modelo["tipo"],
        "titulo": f"{modelo['titulo']} — {cidade['nome']}",
        "descricao": modelo["descricao"],
        "impacto": modelo["impacto"],
        "cidade_id": cidade["id"],
        "reino_id": cidade["reino_id"],
        "npc_envolvido_id": npc["id"] if npc else None,
        "turno_inicio": turno,
        "duracao_turnos": duracao,
        "turno_fim": turno + duracao,
        "estado": "ativo",
    }


def avancar_tempo(mundo: dict[str, Any], turnos: int = 1, seed: int | None = None) -> list[dict[str, Any]]:
    """Avança o calendário, encerra eventos vencidos e pode criar novos eventos.

    Com uma seed inteira, a simulação é reproduzível. Retorna um registro por turno.
    """
    if type(turnos) is not int or not 0 <= turnos <= 1000:
        raise ValueError("turnos deve ser um inteiro entre 0 e 1000")
    validar_mundo(mundo)
    log: list[dict[str, Any]] = []
    base_seed = seed if seed is not None else mundo.get("metadata", {}).get("seed")

    for _ in range(turnos):
        mundo["estado_mundo"]["turno"] += 1
        turno_atual = mundo["estado_mundo"]["turno"]
        rng = random.Random(f"{base_seed}:{turno_atual}:worldforge-events") if base_seed is not None else random.Random()
        encerrados = []
        for evento in mundo["eventos"]:
            if evento["estado"] == "ativo" and turno_atual >= evento["turno_fim"]:
                evento["estado"] = "encerrado"
                encerrados.append(evento["id"])

        criados = []
        ativos = sum(1 for evento in mundo["eventos"] if evento["estado"] == "ativo")
        if ativos < 8 and rng.random() < 0.7:
            novo_numero = len(mundo["eventos"]) + 1
            novo_id = f"evento-{novo_numero:04d}"
            while any(e["id"] == novo_id for e in mundo["eventos"]):
                novo_numero += 1
                novo_id = f"evento-{novo_numero:04d}"
            novo_evento = _criar_evento(mundo, rng, novo_id, turno_atual)
            mundo["eventos"].append(novo_evento)
            criados.append(novo_id)
        log.append({"turno": turno_atual, "eventos_encerrados": encerrados, "eventos_criados": criados})

    validar_mundo(mundo)
    return log


def validar_mundo(mundo: dict[str, Any]) -> None:
    """Valida a estrutura do mundo e todas as referências entre entidades.

    Os erros de estrutura são apresentados como ValueError, em vez de deixar
    KeyError/TypeError pouco informativos escaparem para o usuário.
    """
    if not isinstance(mundo, dict):
        raise ValueError("O mundo precisa ser um objeto/dicionário.")

    colecoes = ("reinos", "cidades", "npcs", "monstros", "missoes", "relacoes", "eventos")
    itens_por_colecao: dict[str, list[dict[str, Any]]] = {}

    for nome in colecoes:
        itens = mundo.get(nome)
        if not isinstance(itens, list):
            raise ValueError(f"A coleção '{nome}' deve ser uma lista.")
        ids: set[str] = set()
        for indice, item in enumerate(itens):
            if not isinstance(item, dict):
                raise ValueError(f"Item {indice} da coleção '{nome}' deve ser um objeto.")
            identificador = item.get("id")
            if not isinstance(identificador, str) or not identificador.strip():
                raise ValueError(f"Item {indice} da coleção '{nome}' tem ID ausente ou inválido.")
            if identificador in ids:
                raise ValueError(f"IDs duplicados na coleção '{nome}': {identificador}")
            ids.add(identificador)
        itens_por_colecao[nome] = itens

    metadata = mundo.get("metadata")
    estado = mundo.get("estado_mundo")
    if not isinstance(metadata, dict):
        raise ValueError("'metadata' deve ser um objeto.")
    if not isinstance(estado, dict) or type(estado.get("turno")) is not int or estado["turno"] < 1:
        raise ValueError("'estado_mundo.turno' deve ser um inteiro maior ou igual a 1.")

    reinos = {item["id"]: item for item in itens_por_colecao["reinos"]}
    cidades = {item["id"]: item for item in itens_por_colecao["cidades"]}
    npcs = {item["id"]: item for item in itens_por_colecao["npcs"]}
    nomes_monstros: set[str] = set()
    for monstro in itens_por_colecao["monstros"]:
        nome = monstro.get("nome")
        if not isinstance(nome, str) or not nome.strip():
            raise ValueError(f"Monstro {monstro['id']} tem nome ausente ou inválido.")
        nomes_monstros.add(nome)

    # Reinos e cidades devem apontar uns para os outros de forma consistente.
    cidades_listadas: set[str] = set()
    for reino in reinos.values():
        reino_id = reino["id"]
        cidade_ids = reino.get("cidade_ids")
        if (not isinstance(cidade_ids, list)
                or any(not isinstance(cidade_id, str) for cidade_id in cidade_ids)
                or len(cidade_ids) != len(set(cidade_ids))):
            raise ValueError(f"'cidade_ids' inválido ou duplicado no reino {reino_id}.")
        capital_id = reino.get("capital_id")
        if not isinstance(capital_id, str) or capital_id not in cidades or capital_id not in cidade_ids:
            raise ValueError(f"Capital inválida no reino {reino_id}.")
        for cidade_id in cidade_ids:
            cidade = cidades.get(cidade_id)
            if cidade is None or cidade.get("reino_id") != reino_id:
                raise ValueError(f"Cidade {cidade_id} não pertence corretamente ao reino {reino_id}.")
            if cidade_id in cidades_listadas:
                raise ValueError(f"Cidade {cidade_id} está listada em mais de um reino.")
            cidades_listadas.add(cidade_id)
    if cidades_listadas != set(cidades):
        raise ValueError("Uma ou mais cidades não estão listadas em seu reino.")

    # A relação entre cidades e NPCs também precisa ser bidirecional.
    npcs_listados: set[str] = set()
    for cidade in cidades.values():
        cidade_id = cidade["id"]
        npc_ids = cidade.get("npc_ids")
        if (not isinstance(npc_ids, list)
                or any(not isinstance(npc_id, str) for npc_id in npc_ids)
                or len(npc_ids) != len(set(npc_ids))):
            raise ValueError(f"'npc_ids' inválido ou duplicado na cidade {cidade_id}.")
        for npc_id in npc_ids:
            npc = npcs.get(npc_id)
            if npc is None or npc.get("cidade_id") != cidade_id:
                raise ValueError(f"NPC {npc_id} não pertence corretamente à cidade {cidade_id}.")
            if npc_id in npcs_listados:
                raise ValueError(f"NPC {npc_id} está listado em mais de uma cidade.")
            npcs_listados.add(npc_id)
    if npcs_listados != set(npcs):
        raise ValueError("Um ou mais NPCs não estão listados em sua cidade.")
    for npc in npcs.values():
        cidade_id, reino_id = npc.get("cidade_id"), npc.get("reino_id")
        cidade = cidades.get(cidade_id) if isinstance(cidade_id, str) else None
        if (cidade is None or not isinstance(reino_id, str) or reino_id not in reinos
                or cidade.get("reino_id") != reino_id):
            raise ValueError(f"Referências de cidade/reino inválidas no NPC {npc['id']}.")

    for missao in itens_por_colecao["missoes"]:
        cidade_id, reino_id = missao.get("cidade_origem_id"), missao.get("reino_id")
        cidade = cidades.get(cidade_id) if isinstance(cidade_id, str) else None
        ameaca = missao.get("ameaca")
        if (cidade is None or not isinstance(reino_id, str) or reino_id not in reinos
                or cidade.get("reino_id") != reino_id
                or not isinstance(ameaca, str) or ameaca not in nomes_monstros):
            raise ValueError(f"Referência inválida na missão {missao['id']}.")

    pares_relacao: set[frozenset[str]] = set()
    for relacao in itens_por_colecao["relacoes"]:
        a, b = relacao.get("npc_a_id"), relacao.get("npc_b_id")
        if (not isinstance(a, str) or not isinstance(b, str)
                or a not in npcs or b not in npcs or a == b):
            raise ValueError(f"Referência inválida na relação {relacao['id']}.")
        par = frozenset((a, b))
        if par in pares_relacao:
            raise ValueError(f"Par duplicado na relação {relacao['id']}.")
        pares_relacao.add(par)
        if type(relacao.get("intensidade")) is not int or not 1 <= relacao["intensidade"] <= 5:
            raise ValueError(f"Intensidade inválida na relação {relacao['id']}.")

    turno_atual = estado["turno"]
    for evento in itens_por_colecao["eventos"]:
        cidade_id, reino_id = evento.get("cidade_id"), evento.get("reino_id")
        cidade = cidades.get(cidade_id) if isinstance(cidade_id, str) else None
        if (cidade is None or not isinstance(reino_id, str) or reino_id not in reinos
                or cidade.get("reino_id") != reino_id):
            raise ValueError(f"Referência de local inválida no evento {evento['id']}.")
        npc_id = evento.get("npc_envolvido_id")
        if npc_id is not None and (not isinstance(npc_id, str) or npc_id not in npcs):
            raise ValueError(f"Referência de NPC inválida no evento {evento['id']}.")
        if not isinstance(evento.get("estado"), str) or evento["estado"] not in {"ativo", "encerrado"}:
            raise ValueError(f"Estado inválido no evento {evento['id']}.")
        inicio, duracao, fim = evento.get("turno_inicio"), evento.get("duracao_turnos"), evento.get("turno_fim")
        if (type(inicio) is not int or inicio < 1 or type(duracao) is not int or duracao < 1
                or type(fim) is not int or fim != inicio + duracao):
            raise ValueError(f"Calendário inválido no evento {evento['id']}.")
        if evento["estado"] == "ativo" and turno_atual >= fim:
            raise ValueError(f"Evento {evento['id']} deveria estar encerrado no turno atual.")
        if evento["estado"] == "encerrado" and turno_atual < fim:
            raise ValueError(f"Evento {evento['id']} foi encerrado antes do fim previsto.")


def exportar_json(mundo: dict[str, Any], caminho: str | Path) -> Path:
    """Valida e exporta o mundo como JSON UTF-8."""
    validar_mundo(mundo)
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(mundo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destino


def executar_testes() -> None:
    """Executa testes de integridade e regressão sem dependências externas."""
    import copy
    import tempfile

    argumentos = dict(seed=2026, quantidade_reinos=3, cidades_por_reino=2,
                      npcs_por_cidade=3, quantidade_missoes=5, quantidade_eventos=4)
    mundo = gerar_mundo(**argumentos)
    assert len(mundo["reinos"]) == 3
    assert len(mundo["cidades"]) == 6
    assert len(mundo["npcs"]) == 18
    assert len(mundo["missoes"]) == 5
    assert len(mundo["eventos"]) == 4
    validar_mundo(mundo)

    # Compara conteúdo, ignorando o timestamp de parede, que varia por execução.
    mundo2 = gerar_mundo(**argumentos)
    comparacao_a, comparacao_b = copy.deepcopy(mundo), copy.deepcopy(mundo2)
    comparacao_a["metadata"].pop("gerado_em_utc", None)
    comparacao_b["metadata"].pop("gerado_em_utc", None)
    assert comparacao_a == comparacao_b, "A mesma seed deve gerar o mesmo conteúdo."

    for relacao in mundo["relacoes"]:
        assert relacao["npc_a_id"] != relacao["npc_b_id"]
    pares = [frozenset((r["npc_a_id"], r["npc_b_id"])) for r in mundo["relacoes"]]
    assert len(pares) == len(set(pares)), "Não deve haver pares de relação duplicados."

    simulacao_a, simulacao_b = gerar_mundo(**argumentos), gerar_mundo(**argumentos)
    log_a = avancar_tempo(simulacao_a, turnos=8, seed=2026)
    log_b = avancar_tempo(simulacao_b, turnos=8, seed=2026)
    assert log_a == log_b, "O avanço de tempo deve ser reproduzível com seed."
    assert simulacao_a["estado_mundo"]["turno"] == 9
    sim_a_cmp, sim_b_cmp = copy.deepcopy(simulacao_a), copy.deepcopy(simulacao_b)
    sim_a_cmp["metadata"].pop("gerado_em_utc", None)
    sim_b_cmp["metadata"].pop("gerado_em_utc", None)
    assert sim_a_cmp == sim_b_cmp, "Simulações iguais devem produzir o mesmo estado."
    assert any(e["estado"] == "encerrado" for e in simulacao_a["eventos"])
    assert len(simulacao_a["eventos"]) >= argumentos["quantidade_eventos"]
    validar_mundo(simulacao_a)

    pequeno = gerar_mundo(seed=1, quantidade_reinos=1, cidades_por_reino=1,
                          npcs_por_cidade=0, quantidade_missoes=0, quantidade_eventos=0)
    assert pequeno["relacoes"] == [] and pequeno["eventos"] == []
    validar_mundo(pequeno)

    # Exportação UTF-8 e leitura de volta.
    with tempfile.TemporaryDirectory() as pasta_temp:
        caminho = Path(pasta_temp) / "subpasta" / "mundo.json"
        exportar_json(mundo, caminho)
        carregado = json.loads(caminho.read_text(encoding="utf-8"))
        validar_mundo(carregado)
        assert carregado["metadata"]["nome"] == mundo["metadata"]["nome"]

    # O validador deve apontar referências quebradas, não falhar silenciosamente.
    quebrado = copy.deepcopy(mundo)
    quebrado["npcs"][0]["cidade_id"] = "cidade-inexistente"
    try:
        validar_mundo(quebrado)
    except ValueError:
        pass
    else:
        raise AssertionError("Referência quebrada deveria ser rejeitada.")

    for chamada in (
        lambda: gerar_mundo(quantidade_reinos=0),
        lambda: avancar_tempo(gerar_mundo(seed=2), turnos=-1),
        lambda: avancar_tempo(gerar_mundo(seed=2), turnos=True),
    ):
        try:
            chamada()
        except ValueError:
            pass
        else:
            raise AssertionError("Parâmetro inválido deveria gerar ValueError.")

    print("OK: geração, exportação JSON, integridade referencial, seed, relações, eventos e parâmetros.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera um mundo procedural para RPG de fantasia.")
    parser.add_argument("--seed", type=int, default=None, help="Seed para geração reproduzível.")
    parser.add_argument("--reinos", type=int, default=4, help="Quantidade de reinos (1-8).")
    parser.add_argument("--cidades", type=int, default=3, help="Cidades por reino (1-20).")
    parser.add_argument("--npcs", type=int, default=4, help="NPCs por cidade (0-50).")
    parser.add_argument("--missoes", type=int, default=8, help="Quantidade de missões (0-200).")
    parser.add_argument("--eventos", type=int, default=6, help="Quantidade de eventos iniciais (0-200).")
    parser.add_argument("--avancar-turnos", type=int, default=0, help="Quantidade de turnos para simular antes de exportar (0-1000).")
    parser.add_argument("--saida", default="mundo.json", help="Caminho do JSON de saída.")
    parser.add_argument("--testar", action="store_true", help="Executa os testes rápidos e encerra.")
    args = parser.parse_args()

    if args.testar:
        executar_testes()
        return
    if args.avancar_turnos < 0 or args.avancar_turnos > 1000:
        parser.error("--avancar-turnos deve estar entre 0 e 1000")
    try:
        mundo = gerar_mundo(args.seed, args.reinos, args.cidades, args.npcs, args.missoes, args.eventos)
        if args.avancar_turnos:
            avancar_tempo(mundo, args.avancar_turnos, seed=args.seed)
        destino = exportar_json(mundo, args.saida)
    except (OSError, ValueError) as erro:
        parser.error(str(erro))
    print(f"Mundo criado: {mundo['metadata']['nome']}")
    print(f"Reinos: {len(mundo['reinos'])} | Cidades: {len(mundo['cidades'])} | NPCs: {len(mundo['npcs'])} | Missões: {len(mundo['missoes'])}")
    print(f"Relações: {len(mundo['relacoes'])} | Eventos: {len(mundo['eventos'])} (ativos: {sum(1 for e in mundo['eventos'] if e['estado'] == 'ativo')}) | Turno: {mundo['estado_mundo']['turno']}")
    print(f"Arquivo: {destino.resolve()}")


if __name__ == "__main__":
    main()
