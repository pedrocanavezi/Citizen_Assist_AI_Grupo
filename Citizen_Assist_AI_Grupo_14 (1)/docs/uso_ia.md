# Uso de inteligência artificial

O ChatGPT/Codex apoiou a estruturação do projeto, a implementação em Python, a redação de orientações e modelos de resposta, a elaboração dos casos de teste e a preparação da demonstração. A participação da ferramenta abrangeu a geração de código e de documentação. A aplicação entregue opera localmente com algoritmos e modelos de texto determinísticos.

## Validação crítica realizada durante a preparação

- As orientações foram confrontadas com páginas públicas da Receita Federal, do Governo Digital e do Tribunal Superior Eleitoral. Cada registro guarda o título da referência, a URL e a data da conferência. A inscrição no CPF e a consulta da situação cadastral foram mantidas como procedimentos distintos.
- A revisão da página da Receita mostrou que mudanças de endereço e de dados de identificação podem ter canais diferentes para quem já possui a CIN. O registro CPF04 aborda somente a mudança de endereço.
- Nos registros do TSE, a certidão de crimes eleitorais e a certidão de quitação receberam IDs separados. A pergunta genérica “certidão eleitoral” foi exercitada no terminal e exigiu escolha.
- Os modelos A e B foram executados sobre os mesmos três registros. As seis saídas estão no CSV de comparação. Ambos citam a fonte; o modelo B permite localizar o aviso em linha própria.
- O avaliador executou perguntas fictícias, comparou os estados e IDs com o gabarito e usou o relógio de alta resolução do Python. O resultado inclui uma reformulação que o sistema deixou sem resposta. Também foram executados roteiros de navegação e testes de falhas da base.
- A avaliação de facilidade de uso foi feita por roteiro automatizado, sem participantes humanos. A demonstração em vídeo usa trechos da saída do Python e os resultados registrados na avaliação.

A data de revisão representa a conferência das páginas na preparação. O programa não acompanha alterações nos portais nem valida a situação de uma pessoa. A equipe pode repetir os comandos do README e revisar registros antes de apresentar o trabalho.
