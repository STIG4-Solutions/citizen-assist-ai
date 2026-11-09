"""
Citizen Assist AI - Assistente Digital de Orientação ao Cidadão
GS 2026.2 - Pensamento Computacional e Automação com Python (1CC)

Formato da entrega: TRIO
Integrantes:
  - Gabriel Freitas - RM572943
  - Giovanni Merlotti - RM573721
  - Sergio Augusto Amaral - RM570184

Público: jovens (16 a 24 anos) em busca do primeiro emprego.
Como executar: python main.py
"""

import os

from base_conhecimento import BaseConhecimento
from assistente import Assistente, ler_opcao

# Caminhos montados a partir da pasta deste arquivo: funciona de qualquer lugar
PASTA_PROJETO = os.path.dirname(os.path.abspath(__file__))
CAMINHO_BASE = os.path.join(PASTA_PROJETO, "data", "base_conhecimento.json")
CAMINHO_HISTORICO = os.path.join(PASTA_PROJETO, "data", "historico.json")
CAMINHO_CSV = os.path.join(PASTA_PROJETO, "data", "atendimentos.csv")


def mostrar_menu(nome):
    print(f"\n========== {nome} ==========")
    print("Orientação para jovens em busca do primeiro emprego")
    print("1 - Fazer uma pergunta")
    print("2 - Navegar por categorias")
    print("3 - Ver indicadores")
    print("4 - Exportar atendimentos para CSV")
    print("5 - Ver como a pontuação é calculada")
    print("0 - Sair")


def main():
    base = BaseConhecimento(CAMINHO_BASE)
    if base.carregar():
        print(f"Base carregada: {len(base.orientacoes)} orientações em "
              f"{len(base.categorias())} categorias.")
    else:
        print("O assistente vai abrir, mas sem orientações para responder.")

    assistente = Assistente("Citizen Assist AI", base, CAMINHO_HISTORICO)
    print("\nOlá! Eu respondo dúvidas com base em informações de fontes oficiais.")
    print("Eu NÃO peço e NÃO guardo nome, CPF, telefone ou e-mail.")
    print("Aviso: este assistente NÃO é um canal oficial.")

    try:
        while True:
            mostrar_menu(assistente.nome)
            opcao = ler_opcao("Escolha uma opção: ", 0, 5)
            if opcao == 1:
                assistente.perguntar()
            elif opcao == 2:
                assistente.navegar()
            elif opcao == 3:
                assistente.indicadores()
            elif opcao == 4:
                assistente.exportar_csv(CAMINHO_CSV)
            elif opcao == 5:
                assistente.explicar_pontuacao()
            else:
                assistente.avaliar_facilidade()
                assistente.exportar_csv(CAMINHO_CSV)
                print("Até logo!")
                break
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C ou fim da entrada: encerra sem mostrar erro
        print("\nPrograma encerrado. O histórico já estava salvo.")


if __name__ == "__main__":
    main()
