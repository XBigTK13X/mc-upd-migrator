import openpyxl
import model

def read_decks_from_xls(file_path,deck_sheet,card_lookup):
    print(f"Reading {file_path}")
    names_by_column_index = {}
    decks_by_name = {}
    workbook = openpyxl.load_workbook(file_path,data_only=True)
    workbook.active = workbook[deck_sheet]
    xls_rows = []
    for row in workbook.active.rows:
        xls_rows.append(row)
    for row_index in range(0,len(xls_rows)):
        xls_row = xls_rows[row_index]
        deck = None
        if row_index == 0:
            for column_index in range(0,len(xls_row)-2,2):
                deck_name_cell = xls_row[column_index]
                if deck_name_cell.value != None:
                    deck = model.CardPool(name=deck_name_cell.value, kind='deck', column_index=column_index)
                    decks_by_name[deck.name] = deck
                    names_by_column_index[deck.column_index] = deck.name

        if row_index > 1:
            for column_index in range(0,len(xls_row)-2,2):
                if column_index % 2 == 0:
                    name_cell = xls_row[column_index]
                    kind_cell = xls_row[column_index + 1]
                    if xls_row[column_index].value == None:
                        continue
                    card = model.Card(
                        name=name_cell.value,
                        kind=kind_cell.value,
                        color=name_cell.fill.bgColor
                    )
                    if not card.id in card_lookup:
                        card_lookup[card.id] = card
                    deck_name = names_by_column_index[column_index]
                    deck = decks_by_name[deck_name]
                    deck.put_card(card.id)
                    decks_by_name[deck_name] = deck
    return decks_by_name,card_lookup