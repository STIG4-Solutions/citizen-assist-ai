"""
Citizen Assist AI - classe BaseConhecimento

A BaseConhecimento é o conjunto de todas as orientações.
Responsabilidade: ler o JSON, listar as categorias e buscar a melhor orientação.
Ela TEM uma lista de objetos Orientacao (composição).
"""

import json

from orientacao import Orientacao

# ---------------------------------------------------------------------------
# Normalização (seção 6.1 do enunciado)
# ---------------------------------------------------------------------------
ACENTOS = {"á": "a", "à": "a", "ã": "a", "â": "a", "é": "e", "ê": "e",
           "í": "i", "ó": "o", "õ": "o", "ô": "o", "ú": "u", "ü": "u",
           "ç": "c"}

# Além dos sinais do enunciado, tratamos hífen, barra e aspas como espaço
# (ex.: "seguro-desemprego" vira "seguro desemprego").
SINAIS = "?!.,;:()-/\"'"


def normalizar(texto):
    """Minúsculas, sem acentos, sem pontuação e com espaço nas pontas."""
    texto = texto.lower().strip()
    for letra, troca in ACENTOS.items():
        texto = texto.replace(letra, troca)
    for sinal in SINAIS:
        texto = texto.replace(sinal, " ")
    # Os espaços nas pontas permitem procurar " palavra " inteira
    return " " + " ".join(texto.split()) + " "


# ---------------------------------------------------------------------------
# Regras de pontuação (seção 6.2 do enunciado)
# ---------------------------------------------------------------------------
PONTOS_PALAVRA_CHAVE = 3   # palavra-chave da orientação aparece na pergunta
PONTOS_TITULO = 1          # palavra da pergunta aparece no título
MIN_LETRAS_TITULO = 4      # só contam palavras com 4 letras ou mais
LIMITE_ALTA = 6            # 6 pontos ou mais = confiança ALTA
LIMITE_MEDIA = 3           # 3 a 5 pontos = confiança MÉDIA

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "palavras_chave",
                       "resposta", "documentos", "onde", "fonte",
                       "verificado_em")


def nivel_confianca(pontos):
    if pontos >= LIMITE_ALTA:
        return "ALTA"
    if pontos >= LIMITE_MEDIA:
        return "MÉDIA"
    return "BAIXA"


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = caminho
        self.orientacoes = []  # lista de objetos Orientacao

    def carregar(self):
        """Lê o JSON e cria os objetos Orientacao. Nunca trava o programa."""
        self.orientacoes = []
        try:
            with open(self.caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
        except FileNotFoundError:
            print(f"[ERRO] Arquivo '{self.caminho}' não encontrado.")
            return False
        except json.JSONDecodeError:
            print(f"[ERRO] O arquivo '{self.caminho}' está corrompido (JSON inválido).")
            return False
        except OSError:
            print(f"[ERRO] Não foi possível abrir '{self.caminho}'.")
            return False

        if not isinstance(dados, list):
            print("[ERRO] A base de conhecimento deve ser uma LISTA de orientações.")
            return False

        for registro in dados:
            # Cada registro é um dicionário; conferimos se tem todos os campos
            if not isinstance(registro, dict):
                print("[AVISO] Um registro da base não é um dicionário e foi ignorado.")
                continue
            faltando = [campo for campo in CAMPOS_OBRIGATORIOS if campo not in registro]
            if faltando:
                print(f"[AVISO] Orientação {registro.get('id', '?')} ignorada. "
                      f"Faltam os campos: {', '.join(faltando)}")
                continue
            orientacao = Orientacao(
                registro["id"], registro["categoria"], registro["titulo"],
                registro["palavras_chave"], registro["resposta"],
                registro["documentos"], registro["onde"], registro["fonte"],
                registro["verificado_em"])
            self.orientacoes.append(orientacao)

        return len(self.orientacoes) > 0

    def categorias(self):
        """Lista de categorias, sem repetição, em ordem alfabética."""
        lista = []
        for orientacao in self.orientacoes:
            if orientacao.categoria not in lista:
                lista.append(orientacao.categoria)
        return sorted(lista)

    def por_categoria(self, categoria):
        """Todas as orientações de uma categoria."""
        return [o for o in self.orientacoes if o.categoria == categoria]

    def pontuar(self, pergunta, orientacao, mostrar_calculo=False):
        """Calcula os pontos de UMA orientação para a pergunta.
        Com mostrar_calculo=True imprime cada ponto ganho (usado no vídeo)."""
        pergunta_norm = normalizar(pergunta)
        titulo_norm = normalizar(orientacao.titulo)
        pontos = 0

        # Regra 1: +3 para cada palavra-chave que aparece na pergunta
        for chave in orientacao.palavras_chave:
            if normalizar(chave) in pergunta_norm:
                pontos += PONTOS_PALAVRA_CHAVE
                if mostrar_calculo:
                    print(f"   +{PONTOS_PALAVRA_CHAVE}  palavra-chave '{chave}' está na pergunta")

        # Regra 2: +1 para cada palavra da pergunta (4+ letras) que está no título
        ja_contadas = []
        for palavra in pergunta_norm.split():
            if len(palavra) >= MIN_LETRAS_TITULO and palavra not in ja_contadas:
                ja_contadas.append(palavra)
                if f" {palavra} " in titulo_norm:
                    pontos += PONTOS_TITULO
                    if mostrar_calculo:
                        print(f"   +{PONTOS_TITULO}  '{palavra}' está no título")

        return pontos

    def buscar(self, pergunta):
        """Devolve uma lista de tuplas (pontos, orientacao), da maior para a
        menor pontuação. Orientações com 0 pontos ficam de fora."""
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda tupla: tupla[0], reverse=True)
        return resultados
