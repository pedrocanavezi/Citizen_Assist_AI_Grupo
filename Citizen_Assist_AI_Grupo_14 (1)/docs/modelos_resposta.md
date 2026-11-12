# Modelos de instrução e comparação

O papel do assistente é ajudar a localizar o próximo passo em um serviço público. A busca escolhe o registro antes da formatação. Os modelos abaixo orientam a função `formatar` e funcionam sem chamadas a modelos de linguagem.

## Instrução A · resposta corrida

“Use a orientação do registro e acrescente seu aviso no mesmo parágrafo. Em seguida, informe a fonte, a data da conferência e a URL. Preserve os requisitos e a linguagem da orientação.”

## Instrução B · resposta por campos

“Identifique o serviço por código e pergunta. Mostre a orientação e o aviso em linhas separadas. Nomeie o órgão e a página, indique quando a fonte foi conferida e forneça a URL completa. Use somente o conteúdo do registro selecionado.”

## Instrução comum aos dois modelos

Se a seleção for ambígua, ofereça as perguntas correspondentes e aguarde a escolha. Para entrada vazia, solicite uma pergunta ou um número. Para informação insuficiente, explique o limite e apresente os temas. Não produza prazos, custos, documentos ou resultados para um cidadão específico a partir de conhecimento externo.

## Experimento

O avaliador usa “Quero a segunda via do CPF”, “Perdi a senha do gov.br” e “Onde voto?”. Recupera cada orientação uma vez e aplica os dois formatos ao mesmo registro. Isso controla a seleção da informação enquanto se compara a apresentação. A planilha CSV guarda exatamente os textos produzidos e cinco indicadores binários. [Saídas completas](comparacao_modelos.csv)

| Critério observado nas três perguntas | Modelo A | Modelo B |
|---|---:|---:|
| Reproduz a orientação da base | 3/3 | 3/3 |
| Inclui o aviso específico | 3/3 | 3/3 |
| Preserva a URL oficial | 3/3 | 3/3 |
| O aviso começa em linha própria, identificado como “Atenção” | 0/3 | 3/3 |
| Exibe o identificador do registro | 0/3 | 3/3 |

O modelo A ocupa menos linhas. No caso da senha, a frase sobre os métodos disponíveis fica colada à ação. O modelo B separa essa condição e mostra qual serviço foi localizado, o que facilita conferir o resultado. Por isso foi escolhido para o terminal. O ensaio verifica consistência de conteúdo e organização visual; preferência e compreensão pelos leitores ainda precisam ser medidas com participantes.
