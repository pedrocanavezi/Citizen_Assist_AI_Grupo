# Citizen Assist AI

Global Solution 2026.2 · Ciência da Computação · FIAP  
**Grupo 14** · Pedro Henrique Canavezi · RM 570298  
**Vídeo no YouTube** · [Assistir à apresentação](https://youtu.be/p24nqW-YJvo)

## O que o assistente resolve

“Preciso de uma certidão eleitoral” pode significar quitação ou crimes eleitorais. O assistente apresenta as duas opções e deixa a pessoa decidir antes de mostrar um procedimento. Uma pergunta mais específica, como “Onde voto?”, leva direto à orientação e à página oficial que a sustenta.

O projeto atende pessoas que precisam encontrar um serviço público brasileiro e ainda desconhecem o nome usado pelo órgão. As 15 orientações cobrem três temas.

| Tema | O que consultar |
|---|---|
| Documentação e CPF | Primeira inscrição, situação cadastral, comprovante de inscrição, alteração de endereço e validação de comprovante de situação cadastral |
| Conta gov.br | Criação da conta, recuperação de senha, aumento de nível, verificação em duas etapas e dispositivos autorizados |
| Serviços eleitorais | Local de votação, situação do título, certidões de quitação e de crimes eleitorais e primeiro título |

## Como executar

Extraia os arquivos e abra o terminal na pasta que contém este README. Use Python 3.10 ou mais recente. O projeto usa apenas a biblioteca padrão e funciona offline. A internet só é necessária para abrir a página de um órgão.

```bash
python src/sistema.py
```

No Windows, se a instalação usar o comando `py`, execute `py src/sistema.py`. Digite uma pergunta, um número do menu ou um identificador como `ELE01`. Use `/temas` para voltar ao início e `/sair` para encerrar.

## Exemplos de uso

| Digite | Resultado no terminal |
|---|---|
| `Onde voto?` | ELE01 indica abrir o e-Título e escolher “Onde Votar”. A tela identifica o TSE, mostra a data da conferência e oferece assuntos relacionados. [Fonte do TSE](https://www.tse.jus.br/servicos-eleitorais/e-titulo-perguntas-frequentes) |
| `Esqueci a senha do gov.br` | GOV02 indica a opção “Esqueci minha senha” e explica que os métodos de recuperação dependem do cadastro. [Fonte do Governo Digital](https://www.gov.br/governodigital/pt-br/acessibilidade-e-usuario/atendimento-gov.br/duvidas-na-conta-gov.br/recuperar-senha-da-conta-gov.br/recuperar-senha-da-conta-gov.br/) |
| `Certidão eleitoral` | O programa oferece duas perguntas e aguarda a seleção entre quitação e crimes eleitorais. |
| `Como renovar a CNH?` | A base informa que tem cobertura insuficiente e oferece os três temas. |
| Pressionar Enter ou digitar `99` | A entrada vazia reapresenta a lista. O número inexistente informa o intervalo válido da tela. |

Para experimentar a navegação entre três orientações, digite `Onde voto?`, depois `1` para situação do título e `2` para certidão de quitação. Os números se referem à lista exibida em cada tela.

## Base, hierarquia e busca

O arquivo [base_conhecimento.json](data/base_conhecimento.json) traz uma lista de registros revisáveis. Cada registro inclui `id`, `tema`, `subtema`, `pergunta`, `palavras_chave`, `orientacao`, `aviso`, `fonte`, `url`, `verificacao` e `relacionados`. A data usa AAAA-MM-DD. O texto resume a página oficial em português. A lista de IDs relacionados liga serviços que podem ser o próximo passo da mesma consulta.

Na carga, um dicionário permite recuperar um registro pelo ID. Outro organiza **tema → subtema → lista de IDs**. Por exemplo, “Serviços eleitorais” contém “Certidões eleitorais”, com ELE03 e ELE04. A lista de relacionados forma um grafo dirigido, inclusive entre temas. Quem consulta o primeiro CPF pode continuar para a criação da conta gov.br.

1. A busca recebe o texto, uniformiza maiúsculas, acentos e grafias como “gov.br” e “gov br”, e descarta palavras frequentes.
2. Para cada registro, verifica se o vocabulário indexado cobre os termos relevantes da consulta. Depois procura expressões cadastradas inteiras, comparando conjuntos de palavras, em qualquer ordem.
3. Entre registros compatíveis, prevalece a expressão encontrada com mais termos. Empates geram opções. Uma pergunta parcial que combina com várias expressões também pede esclarecimento. Duas intenções completas ligadas por “e” ou “ou” podem gerar duas opções.
4. Se a evidência for insuficiente, o assistente oferece os temas. A seleção pelo menu ou ID acessa diretamente a orientação. A busca textual percorre os registros; isso simplifica a inspeção e é suficiente para esta base pequena.

**Manutenção.** Edite o JSON, confira a página do órgão, atualize a data e execute os testes. Para criar um registro, use um ID único, preencha os campos e aponte as relações para IDs existentes. Um novo tema ou subtema aparece automaticamente no menu. O carregador rejeita arquivos ausentes ou vazios, JSON malformado, registros incompletos, IDs repetidos, datas inválidas e relações quebradas.

## Modelos de resposta

O modelo A reúne a orientação e o aviso em um parágrafo, seguido da referência. O modelo B exibe a pergunta identificada, a ação, o aviso, a fonte, a data e a URL em blocos reconhecíveis. Ambos recebem o mesmo registro da busca e só reproduzem o conteúdo cadastrado. O modo B é o padrão do terminal. A decisão e os seis exemplos reproduzíveis estão em [Modelos de resposta](docs/modelos_resposta.md).

## Avaliação

```bash
python tests/avaliar.py
python -m unittest discover -s tests -v
```

O primeiro comando regenera os CSVs e os indicadores em `docs/`. O segundo testa falhas de arquivo, dados inconsistentes, expansão da base e ambiguidade. A tabela registra a execução de referência.

| Indicador | Resultado | Como foi medido |
|---|---:|---|
| Acerto de consulta | 34/35 (97,14%) | Estado e conjunto exato de IDs comparados à expectativa definida para a pergunta |
| Reformulações | 8/9 | Uma descrição coloquial da quitação eleitoral ficou sem resposta |
| Consultas fora do escopo | 5/5 | O sistema reconheceu a insuficiência da base nos cinco casos |
| Tempo médio | 0,019 ms | Busca e montagem da resposta com a base já carregada; relógio de alta resolução em Python 3.12.14/Linux |
| Tarefas concluídas | 5/5 (100%) | Roteiros automatizados executados pelo terminal, em média 3 entradas por tarefa, excluindo o comando de saída |

Os 35 casos incluem 15 perguntas diretas, nove reformulações, cinco fora do escopo, duas entradas inválidas, três ambiguidades e uma consulta por ID. O registro individual traz texto obtido, orientação esperada, classificação e duração. Os tempos variam entre execuções e excluem inicialização, digitação, impressão no terminal e abertura da fonte.

As 15 perguntas diretas repetem enunciados cadastrados e facilitam o resultado global. A maior dificuldade apareceu em “Queria o papel que mostra que estou em dia com as urnas”. A resposta esperada era ELE03; o vocabulário atual levou à recusa. Os cinco roteiros confirmam que é possível concluir o fluxo e recuperar-se de erros. Compreensão por uma pessoa e uso com leitor de tela ainda precisam de avaliação prática.

## Acessibilidade, privacidade e limites

A interação usa apenas teclado, rótulos de texto e opções numeradas. A pessoa pode repetir a navegação sem limite de tempo. O conteúdo fica no computador; o programa não solicita identificação, salva histórico de perguntas nem envia texto para terceiros. As únicas gravações dos testes contêm entradas fictícias. Quem precisar inserir dados em um serviço deve usar o canal oficial indicado na fonte.

Este é um projeto acadêmico independente. O programa orienta sobre o caminho de consulta. A decisão sobre um cadastro, documento ou pedido pertence ao órgão responsável. Cada orientação traz um aviso específico e a data da conferência. As fontes podem mudar após essa data.

## Conclusões e próximos passos

A navegação por menu resolveu as tarefas mesmo quando a pessoa precisava esclarecer qual documento procurava. A busca por palavras teve dificuldade com descrições distantes do vocabulário cadastrado. Duas melhorias prioritárias são colher perguntas espontâneas, separar um novo conjunto de avaliação e incluir sinônimos validados; e testar com pessoas usando teclado e leitor de tela para ajustar o comprimento das respostas e a navegação entre listas. Uma terceira melhoria é rever periodicamente os links e a atualidade das instruções.

## Organização do repositório

| Arquivo ou pasta | Conteúdo |
|---|---|
| `src/sistema.py`, `src/consulta.py` | Interface, validação, índices, busca e modelos A/B |
| [data/](data/) | Orientações e gabarito das consultas simuladas |
| [tests/](tests/) | Avaliação reproduzível e testes de confiabilidade |
| [Resultados de consulta](docs/resultados_testes.csv) e [indicadores](docs/indicadores.json) | Resposta esperada e obtida, tempos e métricas agregadas |
| [Roteiros de uso](docs/roteiro_usabilidade.csv) | Tarefas, sequência de entradas, marcos observados e dificuldades |
| [Comparação A/B](docs/comparacao_modelos.csv) | Seis respostas completas e critérios de apresentação |
| [Uso de IA](docs/uso_ia.md) | Escopo da assistência e validações realizadas |

Estrutura adaptada de `GLOBAL-SOLUTION-2` do [modelo de portfólio da FIAP](https://github.com/equipe1ccon/FIAP-PORTFOLIO-1CCON/tree/master). O modelo original é atribuído à FIAP sob [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
