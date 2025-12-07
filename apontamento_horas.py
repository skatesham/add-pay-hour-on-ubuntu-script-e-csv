#!/usr/bin/env python3

import csv
import os
import re
from datetime import datetime, timedelta

# Valor-hora configurável (R$ por hora trabalhada)
VALOR_HORA_PADRAO = 113.63  # usado como sugestão ao criar novos projetos

LIMITE_ALERTA_MINUTOS = 5 * 60

FIELDNAMES = [
    "n",
    "tempo_total",
    "atividade",
    "data_inicio",
    "data_fim",
    "valor_hora",
    "valor",
    "pago",
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def listar_projetos() -> list[str]:
    projetos = []
    for nome in os.listdir(BASE_DIR):
        caminho = os.path.join(BASE_DIR, nome)
        if os.path.isfile(caminho) and nome.lower().endswith(".csv"):
            projetos.append(nome)
    return sorted(projetos)


def normalizar_nome_projeto(nome: str) -> str | None:
    nome = nome.strip().lower()
    if not nome:
        return None
    slug = re.sub(r"[^\w\-]+", "_", nome)
    slug = re.sub(r"_+", "_", slug).strip("_")
    if not slug:
        return None
    if not slug.endswith(".csv"):
        slug = f"{slug}.csv"
    return slug


def solicitar_valor_hora(valor_sugerido: float | None = None) -> float:
    while True:
        if valor_sugerido is None:
            prompt = "Valor-hora (R$): "
        else:
            prompt = f"Valor-hora (R$) [{valor_sugerido:.2f}]: "

        resposta = input(prompt).strip()
        if not resposta:
            if valor_sugerido is not None:
                return round(valor_sugerido, 2)
            print("Informe um valor maior que zero.")
            continue

        resposta_normalizada = resposta.replace(",", ".")
        try:
            valor = float(resposta_normalizada)
        except ValueError:
            print("Valor inválido. Digite apenas números.")
            continue

        if valor <= 0:
            print("O valor deve ser maior que zero.")
            continue

        return round(valor, 2)


def ler_valor_hora_no_arquivo(filename: str) -> float | None:
    if not os.path.isfile(filename):
        return None

    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        if not reader.fieldnames:
            return None
        if "valor_hora" not in reader.fieldnames:
            return None

        for row in reader:
            bruto = row.get("valor_hora")
            if not bruto:
                continue
            try:
                return float(str(bruto).replace(",", "."))
            except ValueError:
                continue
    return None


def sincronizar_layout_csv(filename: str, valor_hora_padrao: float | None = None):
    if not os.path.isfile(filename):
        return

    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        registros = list(reader)
        cabecalho = reader.fieldnames or []

    precisa_coluna = "valor_hora" not in cabecalho or cabecalho != FIELDNAMES
    precisa_completar = any(
        not str(reg.get("valor_hora", "")).strip() for reg in registros
    )

    if not precisa_coluna and not (precisa_completar and valor_hora_padrao is not None):
        return

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in registros:
            valor_atual = str(row.get("valor_hora", "") or "").strip()
            if not valor_atual and valor_hora_padrao is not None:
                valor_atual = f"{valor_hora_padrao:.2f}"

            writer.writerow(
                {
                    "n": row.get("n", ""),
                    "tempo_total": row.get("tempo_total", ""),
                    "atividade": row.get("atividade", ""),
                    "data_inicio": row.get("data_inicio", ""),
                    "data_fim": row.get("data_fim", ""),
                    "valor_hora": valor_atual,
                    "valor": row.get("valor", ""),
                    "pago": row.get("pago", ""),
                }
            )


def obter_valor_hora_projeto(filename: str) -> float:
    valor_existente = ler_valor_hora_no_arquivo(filename)
    if valor_existente is not None:
        sincronizar_layout_csv(filename, valor_existente)
        return valor_existente

    print(
        "\nEste projeto ainda não possui um valor-hora definido. "
        "Informe o valor que será usado para todos os lançamentos."
    )
    valor = solicitar_valor_hora(VALOR_HORA_PADRAO)
    sincronizar_layout_csv(filename, valor)
    return valor


def criar_novo_projeto() -> tuple[str, float]:
    print("\n--- Criar novo projeto ---")
    while True:
        nome_digitado = input("Nome do projeto: ").strip()
        arquivo = normalizar_nome_projeto(nome_digitado)
        if not arquivo:
            print("Nome inválido. Use letras, números, '-' ou '_'.")
            continue

        caminho = os.path.join(BASE_DIR, arquivo)
        if os.path.exists(caminho):
            print("Já existe um projeto com esse nome. Escolha outro.")
            continue

        valor_hora = solicitar_valor_hora(VALOR_HORA_PADRAO)

        with open(caminho, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
            writer.writeheader()

        print(f"Projeto criado: {arquivo}")
        return caminho, valor_hora


def selecionar_ou_criar_projeto() -> tuple[str, float]:
    while True:
        projetos = listar_projetos()
        if projetos:
            print("\n=== Projetos disponíveis ===")
            for idx, nome in enumerate(projetos, start=1):
                print(f"{idx}. {nome}")
            print(f"{len(projetos) + 1}. Criar novo projeto")

            escolha = input("Selecione uma opção: ").strip()
            if not escolha.isdigit():
                print("Informe o número da opção.")
                continue

            indice = int(escolha)
            if 1 <= indice <= len(projetos):
                arquivo = projetos[indice - 1]
                caminho = os.path.join(BASE_DIR, arquivo)
                print(f"\nProjeto selecionado: {arquivo}")
                valor_hora = obter_valor_hora_projeto(caminho)
                return caminho, valor_hora
            if indice == len(projetos) + 1:
                return criar_novo_projeto()

            print("Opção inválida. Tente novamente.")
        else:
            print("\nNenhum projeto encontrado. Vamos criar o primeiro agora.")
            return criar_novo_projeto()

COMPONENTE_TEMPO_REGEX = re.compile(r"(\d+(?:[.,]\d+)?)([hm])", re.IGNORECASE)


def converter_para_minutos(valor: str | None) -> int | None:
    if not valor:
        return None

    compactado = valor.strip().lower().replace(" ", "")
    posicao = 0
    total_minutos = 0.0

    for match in COMPONENTE_TEMPO_REGEX.finditer(compactado):
        if match.start() != posicao:
            return None  # caractere inesperado entre componentes

        numero_bruto, unidade = match.groups()
        numero_normalizado = numero_bruto.replace(",", ".")

        try:
            quantidade = float(numero_normalizado)
        except ValueError:
            return None

        if unidade.lower() == "h":
            total_minutos += quantidade * 60
        else:
            total_minutos += quantidade

        posicao = match.end()

    if posicao != len(compactado):
        return None  # sobrou caractere não reconhecido

    minutos_inteiros = int(round(total_minutos))
    return minutos_inteiros if minutos_inteiros > 0 else None


def formatar_tempo(minutos: int) -> str:
    horas, resto = divmod(minutos, 60)
    partes = []
    if horas:
        partes.append(f"{horas}h")
    if resto:
        partes.append(f"{resto}m")
    if not partes:
        partes.append("0m")
    return "".join(partes)


def formatar_reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "_").replace(".", ",").replace("_", ".")
    return f"R$ {texto}"


def solicitar_confirmacao_alerta(minutos: int) -> bool:
    horas = minutos / 60
    print(f"\n⚠️  Alerta: tempo informado equivale a {horas:.2f}h (> 5h).")
    resposta = input("Confirmar mesmo assim? (s/n): ").strip().lower()
    return resposta == "s"


def solicitar_tempo():
    while True:
        tempo_digitado = input("Tempo (ex: 30m, 1h30m, 2h): ").strip()
        minutos = converter_para_minutos(tempo_digitado)
        if minutos is None:
            print("Tempo inválido. Use combinações como '1h30m', '45m' ou '2h'.")
            continue

        if minutos > LIMITE_ALERTA_MINUTOS and not solicitar_confirmacao_alerta(minutos):
            print("Tempo descartado. Informe novamente.")
            continue

        return formatar_tempo(minutos), minutos

def proximo_id(filename: str) -> int:
    if not os.path.isfile(filename):
        return 1

    try:
        with open(filename, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            ultimo = 0
            for row in reader:
                try:
                    ultimo = max(ultimo, int(row.get("n", 0)))
                except (TypeError, ValueError):
                    continue
            return ultimo + 1
    except FileNotFoundError:
        return 1


def imprimir_resumo(registro: dict, titulo: str = "Registro salvo", mostrar_pago: bool = True):
    print(f"\n{titulo}:")
    print("-" * 40)
    print(f"ID (n)      : {registro['n']}")
    print(f"Atividade   : {registro['atividade']}")
    print(f"Tempo total : {registro['tempo_total']}")
    print(f"Início      : {registro['data_inicio']}")
    print(f"Fim         : {registro['data_fim']}")
    print(f"Valor (R$)  : {formatar_reais(float(registro['valor']))}")
    if mostrar_pago:
        print(f"Pago        : {registro['pago']}")
    print("-" * 40)


def calcular_totais_nao_pagos(filename: str) -> tuple[int, float]:
    if not os.path.isfile(filename):
        return 0, 0.0

    total_minutos = 0
    total_valor = 0.0

    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if str(row.get("pago", "")).strip().lower() == "sim":
                continue

            tempo = row.get("tempo_total")
            minutos = converter_para_minutos(tempo)
            if minutos:
                total_minutos += minutos

            try:
                valor = float(str(row.get("valor", "0")).replace(",", "."))
            except ValueError:
                valor = 0.0
            total_valor += valor

    return total_minutos, total_valor


def mostrar_totais_nao_pagos(filename: str):
    total_minutos, total_valor = calcular_totais_nao_pagos(filename)
    print("\nPendências:")
    print("-" * 40)
    print(f"Projeto            : {os.path.basename(filename)}")
    print(f"Total horas não pagas: {formatar_tempo(total_minutos)}")
    print(f"Total não pago      : {formatar_reais(total_valor)}")
    print("-" * 40)


def confirmar_registro(registro: dict) -> bool:
    imprimir_resumo(registro, "Pré-visualização do registro", mostrar_pago=False)
    resposta = input("Confirmar gravação? (s/n): ").strip().lower()
    return resposta == "s"


def add_to_csv(filename: str | None = None, valor_hora: float | None = None):
    if filename is None:
        filename = os.path.join(BASE_DIR, "apontamentos.csv")
    filename = os.path.abspath(filename)
    if valor_hora is None:
        valor_hora = obter_valor_hora_projeto(filename)
    nome_projeto = os.path.basename(filename)

    print(f"\n=== Novo Apontamento de Horas ({nome_projeto}) ===")
    atividade = input("Atividade: ").strip()
    if not atividade:
        print("Descrição obrigatória. Operação cancelada.")
        return
    tempo_label, minutos = solicitar_tempo()

    fim = datetime.now()
    inicio = fim - timedelta(minutes=minutos)
    valor_calculado = (minutos / 60) * valor_hora
    registro = {
        "n": str(proximo_id(filename)),
        "tempo_total": tempo_label,
        "atividade": atividade,
        "data_inicio": inicio.strftime("%Y-%m-%d %H:%M:%S"),
        "data_fim": fim.strftime("%Y-%m-%d %H:%M:%S"),
        "valor_hora": f"{valor_hora:.2f}",
        "valor": f"{valor_calculado:.2f}",
        "pago": "Não",
    }
    if not confirmar_registro(registro):
        print("Operação cancelada. Nenhum dado foi salvo.")
        return
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(registro)

    print(f"\n✅ Apontamento salvo em {nome_projeto}")
    mostrar_totais_nao_pagos(filename)


if __name__ == "__main__":
    arquivo_projeto, valor_hora_projeto = selecionar_ou_criar_projeto()
    add_to_csv(arquivo_projeto, valor_hora_projeto)
