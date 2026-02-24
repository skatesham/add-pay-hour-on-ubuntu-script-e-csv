# Apontamento de Horas + Pagamentos

CLI simples para registrar horas por projeto em CSV e controlar pagamentos (inclui parcial).

## O que resolve

- Um CSV por cliente/projeto.
- Registra apontamentos com valor-hora e valor calculado.
- Mostra saldo pendente.
- Baixa pagamentos em ordem sequencial (com suporte a pagamento parcial e histórico com data/descrição).

## Scripts

### 1) Apontar horas
Arquivo: `apontamento_horas.py`

Operação: cria/seleciona projeto e grava **1** apontamento por execução.

```bash
chmod +x apontamento_horas.py
./apontamento_horas.py
````

### 2) Consultar saldo

Arquivo: `pagamentos.py`

Menu → `1. Consultar saldo`

```bash
chmod +x pagamentos.py
./pagamentos.py
```

### 3) Efetivar pagamento

Arquivo: `pagamentos.py`

Menu → `2. Efetivar pagamento`

* Pede **data** (default agora) e **descrição** (ex: Pix, NF, referência).
* Aplica o valor nos itens **não pagos**, na ordem do CSV.
* Se não cobrir o próximo item, marca como **Parcial** e mantém `valor_pendente` para o próximo pagamento.

## Estrutura do CSV (por projeto)

Colunas principais (apontamentos):

* `n` (id)
* `tempo_total`
* `atividade`
* `data_inicio`
* `data_fim`
* `valor_hora`
* `valor`

Controle de pagamento:

* `pago`: `Não` | `Parcial` | `Sim`
* `valor_pago`: quanto já foi aplicado naquele item
* `valor_pendente`: quanto falta (quando estiver `Parcial`)
* `data_pagamento`: histórico de datas (quando recebeu valor)
* `descricao_pagamento`: histórico com data/descrição/valor aplicado

Obs: os scripts sincronizam o layout do CSV automaticamente (adicionam colunas faltantes).

## Alias opcional (zsh)

```bash
alias addhoras="$HOME/add-pay-hour-on-ubuntu-script-e-csv/apontamento_horas.py"
alias paghoras="$HOME/add-pay-hour-on-ubuntu-script-e-csv/pagamentos.py"
```

Depois:

```bash
source ~/.zshrc
addhoras
paghoras
```

## Créditos

* Sham Vinicius Fiorin
