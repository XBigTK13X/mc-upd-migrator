import generate

OLD_LIST="./lists/Magneto.xlsx"
NEW_LIST="./lists/2025-12-19 - Marvel Champions Universal Prebuilt Decks.xlsx"
DECK_SHEET='Hero Prebuilt Decks'

generate.build_ledger(OLD_LIST,NEW_LIST,DECK_SHEET)