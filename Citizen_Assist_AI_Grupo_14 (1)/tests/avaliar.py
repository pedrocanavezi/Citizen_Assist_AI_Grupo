"""Reproduz as consultas, a comparação de respostas e os roteiros de uso."""
import csv
import json
import os
import platform
import statistics
import subprocess
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter_ns

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from consulta import buscar, carregar_base, formatar, mensagem

DOCS = RAIZ / "docs"


def gravar_csv(nome, linhas):
    with (DOCS / nome).open("w", encoding="utf-8-sig", newline="") as arquivo:
        tabela = csv.DictWriter(arquivo, fieldnames=linhas[0], delimiter=";")
        tabela.writeheader()
        tabela.writerows(linhas)


def medir_consultas(base, casos):
    registros = []
    for caso in casos:
        inicio = perf_counter_ns()
        estado, ids = buscar(base, caso["entrada"])
        saida = mensagem(estado, base, ids)
        if estado == "ambigua":
            saida += "\n" + "\n".join(base["por_id"][i]["pergunta"] for i in ids)
        tempo_ms = (perf_counter_ns() - inicio) / 1_000_000
        ok = estado == caso["estado_esperado"] and set(ids) == set(caso["ids_esperados"])
        esperados = [base["por_id"][i]["pergunta"] for i in caso["ids_esperados"]]
        registros.append(dict(caso=caso["caso"], categoria=caso["categoria"],
                              entrada=caso["entrada"], esperado=caso["estado_esperado"],
                              ids_esperados=" ".join(caso["ids_esperados"]),
                              orientacao_esperada=" / ".join(esperados) or caso["estado_esperado"],
                              obtido=estado, ids_obtidos=" ".join(ids),
                              resposta_obtida=saida, acerto=int(ok), tempo_ms=round(tempo_ms, 6)))
    gravar_csv("resultados_testes.csv", registros)
    return registros


def comparar_modelos(base):
    consultas = ["Quero a segunda via do CPF.", "Perdi a senha do gov.br.", "Onde voto?"]
    linhas = []
    for pergunta in consultas:
        estado, ids = buscar(base, pergunta)
        if estado != "resposta":
            raise RuntimeError(f"A comparação precisa de uma orientação: {pergunta}")
        r = base["por_id"][ids[0]]
        for modelo in ("A", "B"):
            saida = formatar(r, modelo)
            linhas.append(dict(pergunta=pergunta, id=r["id"], modelo=modelo,
                               saida=saida, contem_orientacao=int(r["orientacao"] in saida),
                               contem_aviso=int(r["aviso"] in saida), contem_url=int(r["url"] in saida),
                               aviso_em_linha_propria=int("\nAtenção: " in saida),
                               mostra_id=int(f"[{r['id']}]" in saida)))
    gravar_csv("comparacao_modelos.csv", linhas)


# Cada marco precisa aparecer depois do anterior na saída real do programa.
ROTEIROS = [
    ("U1", "Localizar inscrição no CPF só pelo menu", ["1", "1", "1"],
     ["Documentação e CPF / Subtemas", "Escolha uma orientação", "[CPF01]", "https://www.gov.br/"],
     "Exige três escolhas. O texto de cada opção ajuda a identificar o serviço."),
    ("U2", "Consultar local de votação e seguir para situação e quitação", ["Onde voto?", "1", "2"],
     ["[ELE01]", "Assuntos relacionados", "[ELE02]", "Assuntos relacionados", "[ELE03]"],
     "Os números mudam ao abrir outro assunto. É preciso reler a lista de cada tela."),
    ("U3", "Esclarecer qual certidão emitir", ["Certidão eleitoral", "2"],
     ["mais de uma resposta", "Opções para esclarecer", "[ELE04]", "https://www.tse.jus.br/"],
     "A pergunta curta exige uma escolha extra entre duas certidões."),
    ("U4", "Recuperar-se de uma entrada vazia e de um número inválido", ["", "99", "Onde voto?"],
     ["Digite uma pergunta com palavras", "Opção inexistente", "[ELE01]"],
     "A opção inválida informa o intervalo aceito e permite tentar novamente."),
    ("U5", "Sair de uma pergunta fora do escopo e encontrar ajuda", ["Como pagar IPVA?", "2", "1", "2"],
     ["não tem orientação suficiente", "Temas disponíveis", "Conta gov.br / Subtemas", "[GOV02]"],
     "O limite traz os temas disponíveis. A primeira pergunta fica sem orientação."),
]


def roteiros_uso():
    resultados = []
    for numero, tarefa, entradas, marcos, dificuldade in ROTEIROS:
        processo = subprocess.run([sys.executable, str(RAIZ / "src" / "sistema.py")],
                                  input="\n".join([*entradas, "/sair", ""]),
                                  capture_output=True, encoding="utf-8", timeout=10,
                                  env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        restante = processo.stdout
        ok = processo.returncode == 0
        for marco in [*marcos, "Consulta encerrada"]:
            _, achou, restante = restante.partition(marco)
            ok = ok and bool(achou)
        resultados.append(dict(caso=numero, tarefa=tarefa, entradas=json.dumps(entradas, ensure_ascii=False),
                               acoes=len(entradas), concluida=int(ok),
                               evidencia=" → ".join(marcos), observacao=dificuldade))
    gravar_csv("roteiro_usabilidade.csv", resultados)
    return resultados


def main():
    base = carregar_base()
    casos = json.loads((RAIZ / "data" / "perguntas_teste.json").read_text(encoding="utf-8"))
    medidos = medir_consultas(base, casos)
    comparar_modelos(base)
    uso = roteiros_uso()
    acertos = sum(r["acerto"] for r in medidos)
    resumo = dict(consultas=len(medidos), acertos=acertos, taxa_percentual=round(100*acertos/len(medidos), 2),
                  tempo_medio_ms=round(statistics.mean(r["tempo_ms"] for r in medidos), 6),
                  tarefas=len(uso), tarefas_concluidas=sum(r["concluida"] for r in uso),
                  acoes_por_tarefa=statistics.mean(r["acoes"] for r in uso),
                  categorias=dict(Counter(r["categoria"] for r in medidos)),
                  python=platform.python_version(), sistema=platform.system())
    (DOCS / "indicadores.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print(json.dumps(resumo, indent=2, ensure_ascii=False))
    for r in medidos:
        if not r["acerto"]:
            print(r["caso"], r["entrada"], "=>", r["obtido"], r["ids_obtidos"])
    if resumo["tarefas_concluidas"] != len(uso):
        raise SystemExit("Falha no roteiro de navegação.")


if __name__ == "__main__":
    main()
