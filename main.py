import generate

OLD_LIST="./lists/NeXt Evolution.xlsx"
NEW_LIST="./lists/Marvel Champions Universal Prebuilt Decks.xlsx"
DECK_SHEET='Hero Prebuilt Decks'

generate.build_ledger(OLD_LIST,NEW_LIST,DECK_SHEET)