# Citizen Assist AI — Primeiro Emprego

Assistente de terminal, feito em Python, que tira dúvidas de **jovens em busca do primeiro emprego** usando apenas informações de fontes oficiais. Toda resposta mostra a fonte, a data de verificação e o aviso de que o assistente não é um canal oficial. Ele não pede nem guarda dados pessoais.

GS 2026.2 — Pensamento Computacional e Automação com Python (1CC)

## Integrantes

| Nome | RM |
|------|----|
| Gabriel Freitas | RM572943 |
| Giovanni Merlotti | RM573721 |
| Sergio Augusto Amaral | RM570184 |

**Vídeo técnico (YouTube, não listado):** COLE_O_LINK_AQUI

## Público e problema

**Público:** jovens de 16 a 24 anos procurando o primeiro emprego, estágio ou vaga de aprendiz.

**Problema:** para começar a trabalhar, o jovem precisa de vários documentos (CPF, identidade, Carteira de Trabalho Digital, título de eleitor, alistamento militar) e precisa entender coisas como estágio, Jovem Aprendiz e direitos da carteira assinada. A informação existe, mas está espalhada em vários sites, usa linguagem técnica e aparece misturada com páginas falsas e golpes de "vaga paga". O assistente junta essas orientações em linguagem simples e sempre aponta a fonte oficial.

## ODS relacionados

- **ODS 4 — Educação de qualidade:** orientações sobre Encceja e cursos gratuitos.
- **ODS 8 — Trabalho decente e crescimento econômico:** primeiro emprego, direitos trabalhistas, estágio e aprendizagem.
- **ODS 10 — Redução das desigualdades:** informação clara e gratuita para quem tem menos acesso.
- **ODS 16 — Paz, justiça e instituições eficazes:** acesso à informação pública confiável.

## Como executar

Requisito: Python 3.10 ou mais novo. Não usa bibliotecas externas.

```bash
git clone https://github.com/STIG4-Solutions/citizen-assist-ai.git
cd citizen-assist-ai
python main.py
```

Menu:

| Opção | O que faz |
|-------|-----------|
| 1 | Fazer uma pergunta em texto livre |
| 2 | Navegar por categorias (0 volta em todas as telas) |
| 3 | Ver indicadores |
| 4 | Exportar atendimentos para `data/atendimentos.csv` |
| 5 | Ver o cálculo da pontuação de uma pergunta (não é registrado) |
| 0 | Sair: pede a nota de facilidade de 1 a 5 e exporta o CSV |

## Estrutura

```
citizen-assist-ai/
├── README.md
├── main.py                  # menu e ligação entre as classes
├── orientacao.py            # classe Orientacao
├── base_conhecimento.py     # classe BaseConhecimento + normalizar()
├── assistente.py            # classe Assistente
└── data/
    ├── base_conhecimento.json   # 14 orientações, 3 categorias
    ├── historico.json           # atendimentos registrados
    └── atendimentos.csv         # exportação com csv.DictWriter
```

### Classes (composição)

```
Assistente
 └── base: BaseConhecimento
       └── orientacoes: [Orientacao, Orientacao, ...]
```

| Classe | Atributos | Métodos |
|--------|-----------|---------|
| `Orientacao` | id, categoria, titulo, palavras_chave, resposta, documentos, onde, fonte, verificado_em | `exibir()`, `resumo()` |
| `BaseConhecimento` | caminho, orientacoes | `carregar()`, `categorias()`, `por_categoria()`, `pontuar()`, `buscar()` |
| `Assistente` | nome, base, historico, caminho_historico, sessao | `perguntar()`, `atender()`, `navegar()`, `registrar()`, `indicadores()`, `exportar_csv()`, `avaliar_facilidade()`, `explicar_pontuacao()` |

## Regra de pontuação

A pergunta, as palavras-chave e o título são normalizados com `normalizar()`: minúsculas, sem acentos e sem pontuação. Além dos sinais do enunciado, também trocamos `- / " '` por espaço, para que "seguro-desemprego" e "seguro desemprego" sejam iguais.

| Regra | Pontos |
|-------|--------|
| Palavra-chave da orientação aparece na pergunta | +3 |
| Palavra da pergunta (4 letras ou mais) aparece no título (cada palavra conta uma vez) | +1 |
| Melhor orientação com 6 pontos ou mais | Confiança **ALTA** |
| Melhor orientação com 3 a 5 pontos | Confiança **MÉDIA** |
| Nenhuma com 3 pontos | "Não encontrei": pede outras palavras e mostra as categorias |

`buscar()` devolve uma lista de tuplas `(pontos, orientacao)` em ordem decrescente. O assistente mostra a melhor e até 2 alternativas. Se a melhor não ajudou, a pessoa pode abrir uma alternativa.

**Exemplo:** "Quero vaga de estágio ou jovem aprendiz"
- Orientação 7 (Ser Jovem Aprendiz): +3 "jovem aprendiz", +3 "aprendiz", +1 "jovem" no título, +1 "aprendiz" no título = **8 pontos, ALTA**
- Orientação 8 (Regras do estágio): +3 "estagio" e +1 "estagio" no título = 4 pontos (alternativa)
- Orientação 9 (Vagas no Sine): +3 "vaga" = 3 pontos (alternativa)

### Regras de atendimento

- **Dados pessoais:** pergunta com 8 ou mais dígitos, ou com `@`, é recusada e **não** é registrada.
- **Entradas inválidas:** letras, número fora da faixa, resposta vazia ou s/n inválido repetem a pergunta e nunca encerram o programa.
- **Arquivos:** se `base_conhecimento.json` não existir ou estiver corrompido, o programa avisa e continua aberto. Se `historico.json` estiver corrompido, ele é renomeado para `historico.json.corrompido` e o assistente começa um histórico novo.
- **Tentativas:** cada nova forma de escrever a mesma dúvida, ou cada alternativa aberta, conta mais uma tentativa no mesmo atendimento.
- **Tempo:** medido com `time.time()` desde o momento em que a pessoa começa a digitar a pergunta até a resposta aparecer na tela.

### Indicadores

| Indicador | Cálculo |
|-----------|---------|
| Resposta encontrada (%) | atendimentos com `encontrou = true` ÷ total |
| Taxa de acerto (%) | atendimentos com `ajudou = true` ÷ total |
| Tempo médio para encontrar | média de `tempo_segundos` dos atendimentos encontrados |
| Tentativas por atendimento | média de `tentativas` |
| Facilidade de uso | média das notas de 1 a 5 (uma por sessão) |
| Dúvidas sem solução | perguntas com `ajudou = false` |

## Integrações com outras disciplinas

Não houve integração com outras disciplinas nesta versão. A busca por pontuação por regras é o núcleo do assistente.

## Fontes consultadas

Cada orientação do JSON tem seu link e sua data de verificação. Todos os links foram abertos e conferidos em 09/11/2026.

| Id | Orientação | Fonte |
|----|------------|-------|
| 1 | CPF | https://www.gov.br/pt-br/servicos/inscrever-no-cpf |
| 2 | Carteira de Identidade Nacional | https://www.gov.br/governodigital/pt-br/identidade/cin |
| 3 | Carteira de Trabalho Digital | https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/carteira-de-trabalho |
| 4 | Conta gov.br | https://www.gov.br/governodigital/pt-br/conta-gov-br |
| 5 | Título de eleitor | https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/titulo-eleitoral-faq |
| 6 | Alistamento militar | https://alistamento.eb.mil.br |
| 7 | Jovem Aprendiz | https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/aprendizagem-profissional |
| 8 | Estágio (Lei 11.788/2008) | https://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/lei/l11788.htm |
| 9 | Sine | https://www.gov.br/pt-br/servicos/buscar-emprego-no-sistema-nacional-de-emprego-sine |
| 10 | Direitos CLT | https://www.planalto.gov.br/ccivil_03/decreto-lei/del5452.htm |
| 11 | Seguro-desemprego | https://www.gov.br/trabalho-e-emprego/pt-br/servicos/trabalhador/seguro-desemprego/seguro-desemprego-formal |
| 12 | MEI | https://www.gov.br/empresas-e-negocios/pt-br/empreendedor |
| 13 | Encceja | https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/encceja |
| 14 | Escola Virtual de Governo | https://www.escolavirtual.gov.br |

## Resultado do teste com usuários

PREENCHER depois do teste: no mínimo 3 pessoas de fora da equipe e 10 atendimentos. Não registrar nomes nem dados dessas pessoas.

- Pessoas testadas: X (ex.: "3 pessoas: uma estudante do ensino médio, um jovem de 19 anos e uma mãe de adolescente")
- Total de atendimentos: X

| Indicador | Resultado |
|-----------|-----------|
| Resposta encontrada | X% |
| Taxa de acerto (ajudou) | X% |
| Tempo médio para encontrar | X s |
| Tentativas por atendimento | X |
| Facilidade de uso (1 a 5) | X |

**Dúvidas sem solução:**
- PREENCHER (copiar da opção 3 do menu)

**Melhoria feita a partir do teste:**
- PREENCHER (ex.: "a pergunta 'como faço minha carteira de trabalho no celular' não era encontrada; adicionamos a palavra-chave 'carteira no celular' na orientação 3 e ela passou a ser encontrada com confiança ALTA")

## Limitações

- A busca é por regras (palavras iguais). O assistente não entende sinônimos que não estão nas palavras-chave nem erros de digitação (ex.: "cartera").
- Palavras comuns que aparecem em vários títulos podem dar pontos a orientações erradas.
- As informações mudam (prazos, valores, sites). A base precisa ser conferida de novo de tempos em tempos, por isso cada orientação mostra a data de verificação.
- O assistente não é canal oficial e não substitui o atendimento do órgão responsável.
- Ele atende só os temas da base (14 orientações). Fora disso, responde "não encontrei".
- O bloqueio de dados pessoais é por regra simples (8 dígitos ou @). Um nome digitado na pergunta, por exemplo, não é detectado.
