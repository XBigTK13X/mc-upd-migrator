def generate_report(deck_order,card_moves,migration_chains):
    print("=-=-=- Migrating from the old list to the new list")
    chained = []
    print("=-=- Decks with updates")
    for migration_chain in migration_chains:
        if migration_chain.deck_name in card_moves:
            print(f'\n{migration_chain.deck_name}')
            entries = [str(xx) for xx in card_moves[migration_chain.deck_name]]
            print('\n'.join(entries))
            chained.append(migration_chain.deck_name)
    print("=-=- New decks")
    for deck_name in deck_order:
        if deck_name in card_moves and not deck_name in chained:
            print(f'\n{deck_name}')
            entries = [str(xx) for xx in card_moves[deck_name]]
            print('\n'.join(entries))