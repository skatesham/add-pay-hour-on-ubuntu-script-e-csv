# Apontamento de Horas

CLI simples para registrar horas por projeto diretamente em CSV.

## Por que usar?

- **Problema**: acompanhar horas em múltiplos clientes vira bagunça entre planilhas e anotações soltas.
- **Solução**: um fluxo único no terminal que cria projetos, solicita valor-hora e gera lançamentos organizados.

## Funcionalidades

- Seleção/ criação rápida de projetos (um CSV por projeto).
- Valor-hora dinâmico armazenado no próprio arquivo.
- Validação de tempo (inclui alerta para jornadas muito longas).
- Pré-visualização antes de gravar.
- Resumo das pendências (horas/valores não pagos).

## Como funciona

1. Ao iniciar, todos os `.csv` da pasta são listados (cada um é um projeto).
2. Você pode escolher um existente ou criar outro; ao criar, informe o valor-hora padrão daquele cliente.
3. Para cada apontamento basta preencher:
   - **Atividade** (texto livre)
   - **Tempo** usando `Xm`, `Yh` ou combinações (`1h30m`, `45m`)
4. O script valida jornadas longas, mostra uma prévia, grava no CSV escolhido e atualiza o resumo de pendências.

## Começando rápido

```bash
chmod +x apontamento_horas.py
./apontamento_horas.py
```

### Colunas do CSV

| Coluna       | Descrição                              |
|--------------|----------------------------------------|
| n            | ID sequencial                          |
| tempo_total  | Texto do tempo informado               |
| atividade    | Descrição digitada                     |
| data_inicio  | Término − duração                      |
| data_fim     | Horário do lançamento                  |
| valor_hora   | Valor-hora definido para o projeto     |
| valor        | `(minutos / 60) * valor_hora`          |
| pago         | Sempre `"Não"` (atualize manualmente)  |

Cada execução grava apenas **um** apontamento.

## Alias no shell

Adicione ao `~/.zshrc` para rodar como `addhoras`:

```bash
alias addhoras="$HOME/CascadeProjects/apontamento-horas/apontamento_horas.py"
```

Depois rode `source ~/.zshrc` (ou abra um novo terminal) e use:

```bash
addhoras
```

# Exemplo de execução
```bash
➜ addhoras

=== Projetos disponíveis ===
1. ecocria_aponta.csv
2. Criar novo projeto
Selecione uma opção: 1

=== Novo Apontamento de Horas (ecocria_aponta.csv) ===
Atividade: 123
Tempo (ex: 30m, 1h30m, 2h): 1h

Pré-visualização do registro:
----------------------------------------
ID (n)      : 1
Atividade   : 123
Tempo total : 1h
Início      : 2025-12-07 18:31:59
Fim         : 2025-12-07 19:31:59
Valor (R$)  : R$ 113,63
----------------------------------------
Confirmar gravação? (s/n): s

✅ Apontamento salvo em ecocria_aponta.csv

Pendências:
----------------------------------------
Projeto            : ecocria_aponta.csv
Total horas não pagas: 1h
Total não pago      : R$ 113,63
----------------------------------------
```

## Contribuições e Créditos

- Sham Vinicius Fiorin
