import os

def generate_report(deck_order,card_moves,migration_chains):
    os.makedirs('./out/',exist_ok=True)
    write_path = './out/report.txt'
    with open(write_path,'w',encoding='utf-8') as write_handle:
        chained = []
        write_handle.write("=-=- UPDATED DECKS")
        for migration_chain in migration_chains:
            if migration_chain.deck_name in card_moves:
                write_handle.write(f'\n\n{migration_chain.deck_name}\n')
                entries = [str(xx) for xx in card_moves[migration_chain.deck_name]]
                write_handle.write('\n'.join(entries))
                chained.append(migration_chain.deck_name)
        write_handle.write("=-=- NEW DECKS")
        for deck_name in deck_order:
            if deck_name in card_moves and not deck_name in chained:
                write_handle.write(f'\n\n{deck_name}\n')
                entries = [str(xx) for xx in card_moves[deck_name]]
                write_handle.write('\n'.join(entries))