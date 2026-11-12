"""Interface textual do Citizen Assist AI. Execute: python src/sistema.py"""
import re
import sys
from consulta import buscar, carregar_base, mensagem


def temas(base):
    return "Temas disponíveis", [("tema", nome, nome) for nome in base["arvore"]]


def opcoes_registros(base, ids):
    return [("registro", codigo, base["por_id"][codigo]["pergunta"]) for codigo in ids]


def mostrar_menu(titulo, opcoes):
    print(f"\n{titulo}")
    for i, (_, _, rotulo) in enumerate(opcoes, 1):
        print(f"  {i}. {rotulo}")
    print("Digite um número ou uma pergunta. /temas volta ao início. /sair encerra.")


def sessao(base):
    print("Citizen Assist AI | Orientação cidadã")
    print("Protótipo acadêmico independente. Não digite CPF, senhas ou outros dados pessoais.")
    titulo, opcoes = temas(base)
    mostrar_menu(titulo, opcoes)
    while True:
        try:
            entrada = input("\nConsulta> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nConsulta encerrada.")
            return
        if entrada.casefold() in ("/sair", "sair"):
            print("Consulta encerrada.")
            return
        if entrada.casefold() in ("/temas", "menu"):
            titulo, opcoes = temas(base)
        elif re.fullmatch(r"[+-]?[0-9]+", entrada):
            if entrada not in {str(i) for i in range(1, len(opcoes) + 1)}:
                print(f"Opção inexistente. Escolha um número de 1 a {len(opcoes)}.")
                continue
            tipo, chave, _ = opcoes[int(entrada) - 1]
            if tipo == "tema":
                titulo = chave + " / Subtemas"
                opcoes = [("subtema", ids, nome) for nome, ids in base["arvore"][chave].items()]
            elif tipo == "subtema":
                titulo, opcoes = "Escolha uma orientação", opcoes_registros(base, chave)
            else:
                print("\n" + mensagem("resposta", base, [chave]))
                titulo = "Assuntos relacionados"
                opcoes = opcoes_registros(base, base["por_id"][chave]["relacionados"])
                if not opcoes:
                    titulo, opcoes = temas(base)
        else:
            estado, ids = buscar(base, entrada)
            print("\n" + mensagem(estado, base, ids))
            if estado == "invalida":
                pass  # Conserva as alternativas da tela em que ocorreu o erro.
            elif estado == "ambigua":
                titulo, opcoes = "Opções para esclarecer", opcoes_registros(base, ids)
            elif estado == "resposta" and base["por_id"][ids[0]]["relacionados"]:
                titulo = "Assuntos relacionados"
                opcoes = opcoes_registros(base, base["por_id"][ids[0]]["relacionados"])
            else:
                titulo, opcoes = temas(base)
        mostrar_menu(titulo, opcoes)


def main():
    try:
        base = carregar_base()
    except ValueError as erro:
        print(f"Não foi possível iniciar. {erro}", file=sys.stderr)
        return 1
    sessao(base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
