import openpyxl
import model

def read_decks_from_xls(file_path,deck_sheet,card_lookup):
    print(f"Reading {file_path}")
    names_by_column_index = {}
    decks_by_name = {}
    workbook = openpyxl.load_workbook(file_path)
    workbook.active = workbook[deck_sheet]
    row_count = 0
    for xls_row in workbook.active.rows:
        tick_tock = 0
        col_count = 0
        deck = None
        if row_count == 0:
            for xls_cell in xls_row:
                if tick_tock == 0:
                    if deck != None:
                        decks_by_name[deck.name] = deck
                        names_by_column_index[deck.column_index] = deck.name
                    deck = model.CardPool(name=xls_cell.value, kind='deck', column_index=col_count)
                tick_tock = (tick_tock + 1) % 2
                col_count += 1
            # Make sure the last deck isn't ignored
            decks_by_name[deck.name] = deck
            names_by_column_index[deck.column_index] = deck.name
        if row_count > 1:
            for ii in range(0,len(xls_row)-2,2):
                if ii % 2 == 0:
                    column_index = ii
                    if xls_row[ii].value == None:
                        break
                    card = model.Card(name=xls_row[ii].value,kind=xls_row[ii+1].value,color=xls_row[ii].fill.bgColor)
                    if not card.id in card_lookup:
                        card_lookup[card.id] = card
                    deck_name = names_by_column_index[column_index]
                    deck = decks_by_name[deck_name]
                    deck.put_card(card.id)
                    decks_by_name[deck_name] = deck
        row_count += 1
    return decks_by_name,card_lookup