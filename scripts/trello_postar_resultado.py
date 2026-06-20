"""
Lê results/output.xml, extrai resultados por tag trello-<id>,
e posta comentário + ajusta label/lista no card correspondente.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
import requests

API_KEY = os.environ["TRELLO_API_KEY"]
TOKEN = os.environ["TRELLO_TOKEN"]
ALLURE_URL = os.environ.get("ALLURE_URL", "")
OUTPUT_XML = "results/output.xml"
LISTA_TESTADO = os.environ.get("TRELLO_LIST_TESTADO", "Testado")
BOARD_ID = os.environ["TRELLO_BOARD_ID"] if "TRELLO_BOARD_ID" in os.environ else None

BASE = "https://api.trello.com/1"
AUTH = {"key": API_KEY, "token": TOKEN}


def parse_resultados(xml_path: str) -> dict[str, dict]:
    """Retorna {card_id: {passed, failed, total}} a partir do output.xml."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    resultados: dict[str, dict] = {}

    for test in root.iter("test"):
        status_el = test.find("status")
        status = status_el.attrib.get("status", "UNKNOWN") if status_el is not None else "UNKNOWN"

        for tag_el in test.iter("tag"):
            tag = tag_el.text or ""
            m = re.match(r"trello-(.+)", tag)
            if not m:
                continue
            card_id = m.group(1)
            if card_id not in resultados:
                resultados[card_id] = {"passed": 0, "failed": 0, "total": 0}
            resultados[card_id]["total"] += 1
            if status == "PASS":
                resultados[card_id]["passed"] += 1
            else:
                resultados[card_id]["failed"] += 1

    return resultados


def get_listas_board(board_id: str) -> dict[str, str]:
    r = requests.get(f"{BASE}/boards/{board_id}/lists", params=AUTH)
    r.raise_for_status()
    return {lst["name"]: lst["id"] for lst in r.json()}


def postar_comentario(card_id: str, texto: str):
    requests.post(
        f"{BASE}/cards/{card_id}/actions/comments",
        params={**AUTH, "text": texto},
    )


def mover_para_lista(card_id: str, list_id: str):
    requests.put(
        f"{BASE}/cards/{card_id}",
        params={**AUTH, "idList": list_id},
    )


def montar_comentario(card_id: str, res: dict) -> str:
    icone = "✅" if res["failed"] == 0 else "❌"
    linhas = [
        f"{icone} **Resultado da execução automatizada**",
        f"- Total: {res['total']}",
        f"- Passaram: {res['passed']}",
        f"- Falharam: {res['failed']}",
    ]
    if ALLURE_URL:
        linhas.append(f"- Relatório completo: {ALLURE_URL}")
    return "\n".join(linhas)


def main():
    if not os.path.exists(OUTPUT_XML):
        print(f"{OUTPUT_XML} não encontrado.", file=sys.stderr)
        sys.exit(1)

    resultados = parse_resultados(OUTPUT_XML)
    if not resultados:
        print("Nenhuma tag trello-<id> encontrada nos resultados.")
        return

    listas = {}
    if BOARD_ID:
        listas = get_listas_board(BOARD_ID)

    list_testado_id = listas.get(LISTA_TESTADO)

    for card_id, res in resultados.items():
        comentario = montar_comentario(card_id, res)
        postar_comentario(card_id, comentario)
        print(f"Card {card_id}: {res['passed']}/{res['total']} passaram.")

        if list_testado_id:
            mover_para_lista(card_id, list_testado_id)
            print(f"  -> Movido para '{LISTA_TESTADO}'")


if __name__ == "__main__":
    main()
