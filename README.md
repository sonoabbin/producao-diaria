# Produção diária

Registro datado do que eu produzo com IA, todo dia. Não é lista de tecnologias:
cada linha aponta para um artefato que existe — script, site, automação, análise.

## Por que isso existe

Trabalho com automação e agentes de IA em negócios próprios. O problema de quem
aprende construindo é que o trabalho desaparece: daqui a três meses ninguém
reconstrói o que foi feito, quando, nem por quê.

Este repositório resolve isso guardando o histórico em formato que dá para ler e
conferir. Serve como memória do projeto e como prova de constância — o que um
perfil diz, o histórico mostra.

## Como funciona

```
producao-diaria/
  registro.py        # CLI: add / index / stats
  ledger.jsonl       # uma linha JSON por item produzido (fonte da verdade)
  index.html         # painel gerado a partir do ledger
  2026-10-25.md      # diário narrativo do dia
  projeto.json       # configuração e instruções
```

Registrar um item:

```bash
python registro.py add \
  --titulo "Monitoramento semanal no ar" \
  --tipo projeto \
  --resumo "Pipeline com venv separado e cron semanal, sem intervenção manual." \
  --artefato "reports/monitoramento" \
  --tags "automacao,cron"
```

`--tipo` aceita `codigo`, `entrega`, `decisao`, `estudo`, `projeto` e `duvida`.

Regenerar o painel e ver os números:

```bash
python registro.py index
python registro.py stats
```

Sem dependência externa. Só Python 3 e a biblioteca padrão.

## Regra

Dia com trabalho real ganha pelo menos uma linha no ledger. Dia sem nada não
inventa registro — histórico inflado não é prova de nada.

## Painel

`index.html` é gerado pelo próprio `registro.py`: contagem por tipo, dias ativos,
tags e a linha do tempo agrupada por data.
