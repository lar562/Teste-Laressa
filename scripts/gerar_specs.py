"""
Lê cards.json e gera arquivos .robot em tests/specs/.
Cada cenário Given/When/Then da descrição do card vira um test case.
"""

import json
import re
import unicodedata
from pathlib import Path

CARDS_FILE = Path("cards.json")
SPECS_DIR = Path("tests/specs")
SPECS_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s-]+", "_", text)


def parse_scenarios(descricao: str) -> list[dict]:
    """
    Extrai blocos de cenário a partir de texto em formato BDD.
    Suporta múltiplos cenários por card, separados por linha em branco ou 'Scenario:'.
    """
    scenarios = []
    # Divide por "Scenario:" ou "Cenário:" opcionalmente
    blocos = re.split(r"(?i)(?:scenario|cen[aá]rio)\s*[:\-]?\s*", descricao)

    for bloco in blocos:
        bloco = bloco.strip()
        if not bloco:
            continue

        linhas = bloco.splitlines()
        titulo = linhas[0].strip() if linhas else "Sem título"
        passos = []

        for linha in linhas[1:]:
            linha = linha.strip()
            if re.match(r"(?i)^(given|when|then|and|but|dado|quando|então|e)\b", linha):
                passos.append(linha)

        if passos:
            scenarios.append({"titulo": titulo, "passos": passos})

    return scenarios


def passo_para_keyword(passo: str) -> str:
    """Converte uma linha BDD em chamada de keyword Robot Framework."""
    # Remove o prefixo (Given/When/Then/And etc.) e converte para Title Case como keyword
    sem_prefixo = re.sub(
        r"(?i)^(given|when|then|and|but|dado|quando|então|e)\s+", "", passo
    ).strip()
    return sem_prefixo.capitalize()


def gerar_robot(card: dict) -> str:
    card_id = card["id"]
    nome_card = card["name"]
    descricao = card.get("desc", "")

    scenarios = parse_scenarios(descricao)

    if not scenarios:
        return ""

    linhas = [
        "*** Settings ***",
        "Library    Browser",
        "",
        "*** Test Cases ***",
    ]

    for sc in scenarios:
        linhas.append(sc["titulo"])
        linhas.append(f"    [Tags]    trello-{card_id}")
        for passo in sc["passos"]:
            keyword = passo_para_keyword(passo)
            linhas.append(f"    {keyword}")
        linhas.append("")

    linhas += [
        "*** Keywords ***",
        "# Implemente aqui as keywords referenciadas nos test cases acima.",
        "",
    ]

    return "\n".join(linhas)


def main():
    if not CARDS_FILE.exists():
        print("cards.json não encontrado. Execute trello_buscar_cards.py primeiro.")
        return

    cards = json.loads(CARDS_FILE.read_text(encoding="utf-8"))
    if not cards:
        print("Nenhum card para processar.")
        return

    gerados = 0
    for card in cards:
        conteudo = gerar_robot(card)
        if not conteudo:
            print(f"Card '{card['name']}' sem cenários reconhecíveis — ignorado.")
            continue

        nome_arquivo = f"{slugify(card['name'])}.robot"
        caminho = SPECS_DIR / nome_arquivo
        caminho.write_text(conteudo, encoding="utf-8")
        print(f"Gerado: {caminho}")
        gerados += 1

    print(f"\n{gerados} spec(s) gerado(s) em {SPECS_DIR}/")


if __name__ == "__main__":
    main()
