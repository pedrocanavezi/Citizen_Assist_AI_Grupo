"""Leitura, busca e apresentação das orientações. Apenas biblioteca padrão."""
import json
import re
import unicodedata
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

CAMINHO_BASE = Path(__file__).resolve().parents[1] / "data" / "base_conhecimento.json"
CAMPOS_TEXTO = ("id", "tema", "subtema", "pergunta", "orientacao", "fonte",
                "url", "verificacao", "aviso")
IGNORAR = set("""
a o os as um uma uns umas de do dos da das para pra por pelo pela pelos pelas
e em no na nos nas com ao aos à como qual quais que eu me meu minha meus minhas
se ta esta estao quero preciso queria gostaria posso consigo saber ver
onde fica faco faz poderia favor porfavor
""".split())


def palavras(texto):
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    texto = re.sub(r"\bgov(?:\s*\.\s*|\s+)br\b", "govbr", texto)
    return frozenset(re.findall(r"[a-z0-9]+", texto)) - IGNORAR


def validar_registro(r, numero):
    if not isinstance(r, dict):
        raise ValueError(f"Registro {numero}: era esperado um objeto.")
    for campo in CAMPOS_TEXTO:
        if not isinstance(r.get(campo), str) or not r[campo].strip():
            raise ValueError(f"Registro {numero}: campo '{campo}' ausente ou vazio.")
    if not re.fullmatch(r"[A-Z][A-Z0-9_-]+", r["id"]):
        raise ValueError(f"Registro {numero}: identificador inválido.")
    for campo in ("palavras_chave", "relacionados"):
        itens = r.get(campo)
        if not isinstance(itens, list) or not all(isinstance(i, str) and i.strip() for i in itens):
            raise ValueError(f"{r['id']}: revise a lista '{campo}'.")
    if not r["palavras_chave"] or any(not palavras(k) for k in r["palavras_chave"]):
        raise ValueError(f"{r['id']}: inclua expressões de busca com conteúdo.")
    url = urlsplit(r["url"])
    if url.scheme != "https" or not url.hostname or any(c.isspace() for c in r["url"]):
        raise ValueError(f"{r['id']}: referência HTTPS inválida.")
    try:
        date.fromisoformat(r["verificacao"])
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", r["verificacao"]):
            raise ValueError
    except ValueError:
        raise ValueError(f"{r['id']}: use uma data válida no formato AAAA-MM-DD.") from None


def carregar_base(caminho=CAMINHO_BASE):
    try:
        texto = Path(caminho).read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        raise ValueError("Base ausente. Confira o arquivo em data/.") from None
    except (OSError, UnicodeError):
        raise ValueError("Falha de leitura. Confira as permissões e a codificação UTF-8.") from None
    if not texto.strip():
        raise ValueError("O arquivo da base está vazio.")
    try:
        registros = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ValueError(f"JSON inválido na linha {erro.lineno}, coluna {erro.colno}.") from None
    if not isinstance(registros, list) or not registros:
        raise ValueError("A base precisa conter uma lista com pelo menos uma orientação.")
    por_id = {}
    arvore = {}
    indice = {}
    for numero, r in enumerate(registros, 1):
        validar_registro(r, numero)
        codigo = r["id"]
        if codigo in por_id:
            raise ValueError(f"ID repetido na base: {codigo}.")
        por_id[codigo] = r
        arvore.setdefault(r["tema"], {}).setdefault(r["subtema"], []).append(codigo)
        expressoes = [palavras(t) for t in [r["pergunta"], *r["palavras_chave"]]]
        vocabulario = set.union(set(), *expressoes, palavras(r["tema"]), palavras(r["subtema"]))
        indice[codigo] = (expressoes, vocabulario)
    for codigo, r in por_id.items():
        for destino in r["relacionados"]:
            if destino == codigo or destino not in por_id:
                raise ValueError(f"{codigo}: relação inválida com '{destino}'.")
    return {"por_id": por_id, "arvore": arvore, "indice": indice}


def classificar(base, texto):
    """Retorna (estado, IDs). O menu e os testes usam exatamente esta função."""
    consulta = palavras(texto)
    if not consulta:
        return ("invalida" if not re.search(r"\w", texto) else "sem_base"), []
    if texto.strip().upper() in base["por_id"]:
        return "resposta", [texto.strip().upper()]
    resultados = []
    sugestoes = []
    for codigo, (expressoes, vocabulario) in base["indice"].items():
        if not consulta <= vocabulario:
            continue  # Um termo sem cobertura pode mudar o serviço pedido.
        tamanhos = [len(expr) for expr in expressoes if expr and expr <= consulta]
        if tamanhos:
            resultados.append((max(tamanhos), codigo))
        elif any(consulta <= expr for expr in expressoes):
            sugestoes.append(codigo)
    if resultados:
        maior = max(pontos for pontos, _ in resultados)
        ids = [codigo for pontos, codigo in resultados if pontos == maior]
        return ("resposta" if len(ids) == 1 else "ambigua"), ids
    if len(sugestoes) > 1:
        return "ambigua", sugestoes
    return "sem_base", []


def buscar(base, texto):
    if not texto.strip() or not re.search(r"[\w]", texto):
        return "invalida", []
    # Se houver duas intenções completas, deixe a pessoa escolher entre elas.
    partes = re.split(r"\s+(?:e|ou)\s+", texto, flags=re.IGNORECASE)
    if len(partes) > 1:
        respostas = [classificar(base, p) for p in partes]
        if all(estado == "resposta" for estado, _ in respostas):
            ids = list(dict.fromkeys(ids[0] for _, ids in respostas))
            if len(ids) > 1:
                return "ambigua", ids
    return classificar(base, texto)


def formatar(r, modelo="B"):
    """A e B usam exclusivamente os campos da base; B destaca os limites."""
    ano, mes, dia = r["verificacao"].split("-")
    data_br = f"{dia}/{mes}/{ano}"
    if modelo == "A":
        return (f"{r['orientacao']} {r['aviso']}\n"
                f"Fonte: {r['fonte']} ({data_br})\n{r['url']}")
    if modelo != "B":
        raise ValueError("Escolha o modelo A ou B.")
    return (f"[{r['id']}] {r['pergunta']}\n"
            f"Orientação: {r['orientacao']}\n"
            f"Atenção: {r['aviso']}\n"
            f"Fonte: {r['fonte']} | Conferida em {data_br}\n{r['url']}")


def mensagem(estado, base, ids):
    if estado == "resposta":
        return formatar(base["por_id"][ids[0]])
    if estado == "ambigua":
        return "Sua pergunta pode ter mais de uma resposta. Escolha um dos assuntos abaixo."
    if estado == "invalida":
        return "Digite uma pergunta com palavras, ou escolha um número da lista."
    return "A base não tem orientação suficiente para essa pergunta. Tente outra formulação ou escolha um tema."
