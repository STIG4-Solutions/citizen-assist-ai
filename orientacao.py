"""
Citizen Assist AI - classe Orientacao

Uma Orientacao representa UM registro da base de conhecimento
(um dicionário do arquivo data/base_conhecimento.json).
Responsabilidade: guardar os dados de uma orientação e exibi-la na tela.
"""

AVISO = "Aviso: este assistente NÃO é um canal oficial. Confirme sempre na fonte."


class Orientacao:
    def __init__(self, id, categoria, titulo, palavras_chave, resposta,
                 documentos, onde, fonte, verificado_em):
        # Atributos: cada campo do JSON vira um atributo do objeto (self)
        self.id = id
        self.categoria = categoria
        self.titulo = titulo
        self.palavras_chave = palavras_chave  # lista de strings
        self.resposta = resposta
        self.documentos = documentos          # lista de strings
        self.onde = onde
        self.fonte = fonte
        self.verificado_em = verificado_em

    def exibir(self):
        """Mostra a orientação completa, sempre com fonte, data e aviso."""
        print()
        print(f">> {self.titulo}  [{self.categoria}]")
        print(self.resposta)
        if self.documentos:
            print("Documentos necessários:")
            for documento in self.documentos:
                print(f"  - {documento}")
        else:
            print("Documentos necessários: nenhum documento específico.")
        print(f"Onde: {self.onde}")
        print(f"Fonte: {self.fonte} (verificado em {self.verificado_em})")
        print(AVISO)

    def resumo(self):
        """Texto curto usado nas listas numeradas e nas alternativas."""
        return f"{self.titulo} [{self.categoria}]"
