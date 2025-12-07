# Apontamento de Horas

Script CLI para coletar rápida­mente horas trabalhadas e salvá-las em `apontamentos.csv`.

## Começando rápido

```bash
chmod +x apontamento_horas.py
./apontamento_horas.py
```

Sempre informe:

1. **Atividade** – breve descrição (obrigatório)
2. **Tempo** – use `Xm`, `Yh` ou combinações (`1h30m`, `45m`, `2h15m`)
   - Durações maiores que 5h pedem confirmação extra

Antes de gravar, o script mostra uma pré-visualização e só salva se você confirmar. Depois de salvo, ele atualiza os totais de horas/valores pendentes (não pagos).

### Colunas do CSV

| Coluna       | Descrição                              |
|--------------|----------------------------------------|
| n            | ID sequencial                          |
| tempo_total  | Texto do tempo informado               |
| atividade    | Descrição digitada                     |
| data_inicio  | Término − duração                      |
| data_fim     | Horário do lançamento                  |
| valor        | `(minutos / 60) * VALOR_HORA`          |
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
