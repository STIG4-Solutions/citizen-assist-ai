"""
Citizen Assist AI - classe Assistente

O Assistente é quem conversa com o cidadão.
Responsabilidade: fazer o atendimento, guardar o histórico e calcular os
indicadores. Ele TEM uma BaseConhecimento (composição).
"""

import csv
import json
import os
import time
from datetime import datetime

from base_conhecimento import normalizar, nivel_confianca, LIMITE_MEDIA

CAMPOS_CSV = ["sessao", "data", "origem", "pergunta", "id_orientacao",
              "encontrou", "ajudou", "tentativas", "tempo_segundos",
              "nota_facilidade"]


# ---------------------------------------------------------------------------
# Funções de apoio: leitura segura do teclado e bloqueio de dados pessoais
# ---------------------------------------------------------------------------
def ler_opcao(mensagem, minimo, maximo):
    """Pede um número entre minimo e maximo. Repete até ser válido."""
    while True:
        entrada = input(mensagem).strip()
        if entrada == "":
            print("Resposta vazia. Digite um número.")
        elif not entrada.isdigit():
            print("Entrada inválida. Digite apenas números.")
        elif not minimo <= int(entrada) <= maximo:
            print(f"Opção fora da faixa. Digite um número de {minimo} a {maximo}.")
        else:
            return int(entrada)


def ler_sim_nao(mensagem):
    """Pede s/n (aceita sim/não). Repete até ser válido."""
    while True:
        resposta = normalizar(input(mensagem)).strip()
        if resposta in ("s", "sim"):
            return True
        if resposta in ("n", "nao"):
            return False
        print("Resposta inválida. Digite s (sim) ou n (não).")


def contem_dado_pessoal(texto):
    """True se o texto tem 8 ou mais dígitos (CPF, telefone...) ou @ (e-mail)."""
    digitos = 0
    for caractere in texto:
        if caractere.isdigit():
            digitos += 1
    return digitos >= 8 or "@" in texto


MSG_DADO_PESSOAL = "Atenção: não digite CPF, telefone ou e-mail. Reescreva."


class Assistente:
    def __init__(self, nome, base, caminho_historico="data/historico.json"):
        self.nome = nome
        self.base = base                      # objeto BaseConhecimento
        self.caminho_historico = caminho_historico
        self.historico = self.carregar_historico()  # lista de dicionários
        # Identifica a execução atual (para a nota de facilidade)
        self.sessao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------
    # Arquivo de histórico
    # ------------------------------------------------------------------
    def carregar_historico(self):
        try:
            with open(self.caminho_historico, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
            print("[AVISO] historico.json não é uma lista. Começando histórico vazio.")
        except FileNotFoundError:
            return []
        except (json.JSONDecodeError, OSError):
            print("[AVISO] historico.json está corrompido. Começando histórico vazio.")
        # Guarda uma cópia do arquivo com problema para não perder nada
        try:
            os.replace(self.caminho_historico, self.caminho_historico + ".corrompido")
        except OSError:
            pass
        return []

    def salvar_historico(self):
        try:
            pasta = os.path.dirname(self.caminho_historico)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(self.caminho_historico, "w", encoding="utf-8") as arquivo:
                json.dump(self.historico, arquivo, ensure_ascii=False, indent=2)
        except OSError:
            print("[ERRO] Não foi possível salvar o histórico.")

    def registrar(self, origem, pergunta, id_orientacao, encontrou, ajudou,
                  tentativas, tempo):
        """Guarda um atendimento no histórico (e no arquivo JSON)."""
        atendimento = {
            "sessao": self.sessao,
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "origem": origem,                  # "pergunta" ou "categoria"
            "pergunta": pergunta,
            "id_orientacao": id_orientacao,    # None se não encontrou
            "encontrou": encontrou,
            "ajudou": ajudou,
            "tentativas": tentativas,
            "tempo_segundos": tempo,
            "nota_facilidade": None,           # preenchida ao sair
        }
        self.historico.append(atendimento)
        self.salvar_historico()

    # ------------------------------------------------------------------
    # Atendimento por pergunta em texto livre
    # ------------------------------------------------------------------
    def perguntar(self):
        if not self.base.orientacoes:
            print("A base de conhecimento está vazia. Não é possível responder.")
            return
        print("\nEscreva sua dúvida com suas palavras. Ex.: 'como tiro a carteira de trabalho?'")
        print("Não digite nome, CPF, telefone ou e-mail.")
        while True:
            inicio = time.time()  # o tempo conta desde que a pessoa começa a digitar
            pergunta = input("\nDigite sua dúvida (0 para voltar): ").strip()
            if pergunta == "0":
                return
            if pergunta == "":
                print("Você não digitou nada. Escreva sua dúvida ou 0 para voltar.")
                continue
            if contem_dado_pessoal(pergunta):
                print(MSG_DADO_PESSOAL)  # recusada e NÃO registrada
                continue
            self.atender(pergunta, inicio)

    def atender(self, pergunta, inicio):
        """Um atendimento: pode ter várias tentativas até achar a resposta."""
        tentativas = 1
        perguntas_feitas = [pergunta]

        while True:
            resultados = self.base.buscar(pergunta)   # lista de tuplas
            if resultados and resultados[0][0] >= LIMITE_MEDIA:
                break  # encontrou com confiança suficiente
            print("\nNão encontrei uma orientação para essa dúvida.")
            print("Tente usar outras palavras (ex.: 'cpf', 'estágio', 'jovem aprendiz')")
            print("ou volte ao menu e navegue pelas categorias:", ", ".join(self.base.categorias()))
            nova = input("Reescreva sua dúvida (0 para desistir): ").strip()
            while nova == "" or (nova != "0" and contem_dado_pessoal(nova)):
                if nova == "":
                    print("Você não digitou nada.")
                else:
                    print(MSG_DADO_PESSOAL)
                nova = input("Reescreva sua dúvida (0 para desistir): ").strip()
            if nova == "0":
                tempo = round(time.time() - inicio, 1)
                self.registrar("pergunta", " | ".join(perguntas_feitas), None,
                               False, False, tentativas, tempo)
                print("Tudo bem. Sua dúvida foi anotada para melhorarmos o assistente.")
                return
            tentativas += 1
            perguntas_feitas.append(nova)
            pergunta = nova

        pontos, melhor = resultados[0]
        tempo = round(time.time() - inicio, 1)
        print(f"\nConfiança da resposta: {nivel_confianca(pontos)} ({pontos} pontos)")
        melhor.exibir()

        # Até duas alternativas (as próximas da lista de tuplas)
        alternativas = resultados[1:3]
        if alternativas:
            print("\nOutras orientações que podem ajudar:")
            for numero, (pts, orientacao) in enumerate(alternativas, start=1):
                print(f"  {numero} - {orientacao.resumo()} ({pts} pontos)")

        ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
        escolhida = melhor

        if not ajudou and alternativas:
            escolha = ler_opcao("Quer ver uma alternativa? Digite o número (0 para não): ",
                                0, len(alternativas))
            if escolha != 0:
                escolhida = alternativas[escolha - 1][1]
                tentativas += 1
                tempo = round(time.time() - inicio, 1)
                escolhida.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")

        if not ajudou:
            print("Que pena! Sua dúvida foi anotada. Procure também o órgão oficial indicado na fonte.")

        self.registrar("pergunta", " | ".join(perguntas_feitas), escolhida.id,
                       True, ajudou, tentativas, tempo)

    # ------------------------------------------------------------------
    # Atendimento por navegação nas categorias
    # ------------------------------------------------------------------
    def navegar(self):
        categorias = self.base.categorias()
        if not categorias:
            print("A base de conhecimento está vazia.")
            return
        inicio = time.time()
        while True:
            print("\n--- Categorias ---")
            for numero, categoria in enumerate(categorias, start=1):
                print(f"{numero} - {categoria}")
            print("0 - Voltar")
            opcao = ler_opcao("Escolha uma categoria: ", 0, len(categorias))
            if opcao == 0:
                return
            categoria = categorias[opcao - 1]

            while True:
                lista = self.base.por_categoria(categoria)
                print(f"\n--- {categoria} ---")
                for numero, orientacao in enumerate(lista, start=1):
                    print(f"{numero} - {orientacao.titulo}")
                print("0 - Voltar")
                escolha = ler_opcao("Escolha uma orientação: ", 0, len(lista))
                if escolha == 0:
                    break
                orientacao = lista[escolha - 1]
                tempo = round(time.time() - inicio, 1)
                orientacao.exibir()
                ajudou = ler_sim_nao("\nEssa orientação respondeu sua dúvida? (s/n): ")
                self.registrar("categoria", f"Navegação: {categoria} > {orientacao.titulo}",
                               orientacao.id, True, ajudou, 1, tempo)
                inicio = time.time()  # próximo atendimento começa agora

    # ------------------------------------------------------------------
    # Modo explicação: mostra o cálculo da pontuação (útil no vídeo)
    # ------------------------------------------------------------------
    def explicar_pontuacao(self):
        pergunta = input("\nDigite uma pergunta para ver o cálculo (0 para voltar): ").strip()
        if pergunta in ("", "0"):
            return
        if contem_dado_pessoal(pergunta):
            print(MSG_DADO_PESSOAL)
            return
        print(f"Pergunta normalizada: '{normalizar(pergunta)}'")
        resultados = self.base.buscar(pergunta)
        if not resultados:
            print("Nenhuma orientação recebeu pontos.")
            return
        for pontos, orientacao in resultados[:3]:
            print(f"\n[{orientacao.id}] {orientacao.titulo}")
            self.base.pontuar(pergunta, orientacao, mostrar_calculo=True)
            print(f"   = {pontos} pontos -> confiança {nivel_confianca(pontos)}")
        print("\n(Este modo não é registrado no histórico.)")

    # ------------------------------------------------------------------
    # Nota de facilidade, indicadores e CSV
    # ------------------------------------------------------------------
    def avaliar_facilidade(self):
        """Ao sair: pede uma nota de 1 a 5 e grava nos atendimentos desta sessão."""
        da_sessao = [a for a in self.historico if a.get("sessao") == self.sessao]
        if not da_sessao:
            return
        nota = ler_opcao("\nDe 1 a 5, quão fácil foi usar o assistente? ", 1, 5)
        for atendimento in da_sessao:
            atendimento["nota_facilidade"] = nota
        self.salvar_historico()
        print("Obrigado pela avaliação!")

    def indicadores(self):
        total = len(self.historico)
        if total == 0:
            print("\nAinda não há atendimentos registrados.")
            return {}

        encontrados = [a for a in self.historico if a.get("encontrou")]
        ajudaram = [a for a in self.historico if a.get("ajudou")]
        tempos = [a.get("tempo_segundos", 0) for a in encontrados]
        tentativas = [a.get("tentativas", 1) for a in self.historico]

        # Uma nota por sessão (cada pessoa que usou e saiu avaliando)
        notas_por_sessao = {}
        for a in self.historico:
            if a.get("nota_facilidade") is not None:
                notas_por_sessao[a.get("sessao")] = a["nota_facilidade"]
        notas = list(notas_por_sessao.values())

        sem_solucao = []
        for a in self.historico:
            if not a.get("ajudou") and a.get("pergunta") not in sem_solucao:
                sem_solucao.append(a.get("pergunta"))

        resultado = {
            "total": total,
            "encontrada_pct": len(encontrados) / total * 100,
            "acerto_pct": len(ajudaram) / total * 100,
            "tempo_medio": sum(tempos) / len(tempos) if tempos else 0,
            "tentativas_media": sum(tentativas) / total,
            "facilidade": sum(notas) / len(notas) if notas else None,
            "sem_solucao": sem_solucao,
        }

        print("\n========== INDICADORES ==========")
        print(f"Total de atendimentos ........: {resultado['total']}")
        print(f"Resposta encontrada ..........: {resultado['encontrada_pct']:.1f}%")
        print(f"Taxa de acerto (ajudou) ......: {resultado['acerto_pct']:.1f}%")
        print(f"Tempo médio para encontrar ...: {resultado['tempo_medio']:.1f} s")
        print(f"Tentativas por atendimento ...: {resultado['tentativas_media']:.2f}")
        if resultado["facilidade"] is None:
            print("Facilidade de uso (1 a 5) ....: sem avaliações ainda")
        else:
            print(f"Facilidade de uso (1 a 5) ....: {resultado['facilidade']:.1f} "
                  f"({len(notas)} avaliações)")
        print("Dúvidas sem solução:")
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f"  - {pergunta}")
        else:
            print("  (nenhuma)")
        print("=================================")
        return resultado

    def exportar_csv(self, caminho="data/atendimentos.csv"):
        try:
            pasta = os.path.dirname(caminho)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            # utf-8-sig: o Excel abre os acentos corretamente
            with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS_CSV,
                                          extrasaction="ignore")
                escritor.writeheader()
                for atendimento in self.historico:
                    escritor.writerow(atendimento)
            print(f"{len(self.historico)} atendimento(s) exportado(s) para {caminho}")
        except OSError:
            print("[ERRO] Não foi possível exportar o CSV (o arquivo está aberto em outro programa?).")
