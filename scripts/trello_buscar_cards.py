"""
Busca cards da lista 'Aguardando Validação' no Trello e salva em cards.json.
Após processar, aplica o label 'specs-gerados' para evitar reprocessamento.
"""

import json
import os
import sys
import requests

API_KEY = os.environ["TRELLO_API_KEY"]
TOKEN = os.environ["TRELLO_TOKEN"]
BOARD_ID = os.environ["TRELLO_BOARD_ID"]
LIST_NAME = os.environ.get("TRELLO_LIST_NAME", "Aguardando Validação")
LABEL_SKIP = "specs-gerados"
OUTPUT_FILE = "cards.json"

BASE = "https://api.trello.com/1"
AUTH = {"key": API_KEY, "token": TOKEN}


def get_lists():
    r = requests.get(f"{BASE}/boards/{BOARD_ID}/lists", params=AUTH)
    r.raise_for_status()
    return r.json()


def get_cards(list_id):
    r = requests.get(
        f"{BASE}/lists/{list_id}/cards",
        params={**AUTH, "fields": "id,name,desc,idLabels", "checklists": "all"},
    )
    r.raise_for_status()
    return r.json()


def get_labels():
    r = requests.get(f"{BASE}/boards/{BOARD_ID}/labels", params=AUTH)
    r.raise_for_status()
    return {lbl["name"]: lbl["id"] for lbl in r.json()}


def create_label_if_missing(labels: dict) -> str:
    if LABEL_SKIP not in labels:
        r = requests.post(
            f"{BASE}/boards/{BOARD_ID}/labels",
            params={**AUTH, "name": LABEL_SKIP, "color": "sky"},
        )
        r.raise_for_status()
        label_id = r.json()["id"]
        labels[LABEL_SKIP] = label_id
    return labels[LABEL_SKIP]


def apply_label(card_id: str, label_id: str):
    requests.post(
        f"{BASE}/cards/{card_id}/idLabels",
        params={**AUTH, "value": label_id},
    )


def main():
    lists = get_lists()
    target = next((l for l in lists if l["name"] == LIST_NAME), None)
    if not target:
        print(f"Lista '{LIST_NAME}' não encontrada no board.", file=sys.stderr)
        sys.exit(1)

    labels = get_labels()
    skip_label_id = labels.get(LABEL_SKIP)
    all_cards = get_cards(target["id"])

    # Filtra cards que já tiveram specs gerados
    cards_novos = [
        c for c in all_cards if skip_label_id not in (c.get("idLabels") or [])
    ]

    if not cards_novos:
        print("Nenhum card novo para processar.")
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return

    print(f"{len(cards_novos)} card(s) encontrado(s) para processar.")

    # Garante que o label existe antes de aplicar
    label_id = create_label_if_missing(labels)
    for card in cards_novos:
        apply_label(card["id"], label_id)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cards_novos, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
