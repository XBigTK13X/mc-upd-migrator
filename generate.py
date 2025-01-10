import openpyxl
from report import html
import model
import excel

def calculate_moves(ledger,card_lookup):
    def move_sort(a,b):
        if a.source == a.deck_name and b.source != b.deck_name:
            return -1
        if b.source == b.deck_name and a.source != a.deck_name:
            return 1
        if a.source == 'Supply' and b.source != 'Supply':
            return -1
        if b.source == 'Supply' and a.source != 'Supply':
            return 1
        return -1 if a.card.id < b.card.id else 1
    moves = {}
    ordered_deck_names = sorted(list(ledger.deck_hits.keys()), key = lambda xx: ledger.deck_hits[xx])
    for deck_name in ordered_deck_names:
        moves[deck_name] = []
        is_new = deck_name in ledger.new_decks
        for card_id,entries in ledger.cards.items():
            from_count = len([xx for xx in entries['from'] if xx == deck_name])
            to_count = len([xx for xx in entries['to'] if xx == deck_name])
            if not is_new and not deck_name in ledger.deck_connections and (from_count > 0 or to_count > 0):
                ledger.deck_connections[deck_name] = model.MigrationChain(deck_name)
            if to_count > 0:
                if is_new:
                    for ii in range(0, to_count):
                        moves[deck_name].append(model.LedgerEntry(deck_name,'Supply',deck_name,card_lookup[card_id]))
                else:
                    for ii in range(0, to_count):
                        if len(entries['from']) > 0:
                            source_deck = entries['from'].pop()
                            moves[deck_name].append(model.LedgerEntry(deck_name,source_deck,deck_name,card_lookup[card_id]))
                            ledger.deck_connections[deck_name].connect(source_deck)
                        else:
                            ledger.deck_connections[deck_name].connect('Supply')
                            moves[deck_name].append(model.LedgerEntry(deck_name,'Supply',deck_name,card_lookup[card_id]))
            if from_count > 0:
                ledger.deck_connections[deck_name].connect('Supply')
                for ii in range(0, from_count):
                    moves[deck_name].append(model.LedgerEntry(deck_name,deck_name,'Supply',card_lookup[card_id]))
        import functools
        moves[deck_name] = sorted(moves[deck_name],key=functools.cmp_to_key(move_sort))
    return moves

def calculate_migration_chain(ledger):
    chains = []
    for deck_name,migration_chain in ledger.deck_connections.items():
        chains.append(migration_chain)
    chains = sorted(chains,key=lambda xx: xx.connection_count())
    return chains

def build_ledger(old_list,new_list,deck_sheet):
    card_lookup = {}
    old_decks,card_lookup = excel.read_decks_from_xls(old_list,deck_sheet,card_lookup)
    new_decks,card_lookup = excel.read_decks_from_xls(new_list,deck_sheet,card_lookup)
    decks_by_name = {}
    for deck_name,deck in old_decks.items():
        if not deck_name in decks_by_name:
            decks_by_name[deck_name] = {'old':deck}
        else:
            decks_by_name[deck_name]['old'] = deck

    for deck_name,deck in new_decks.items():
        if not deck_name in decks_by_name:
            decks_by_name[deck_name] = {'new':deck}
        else:
            decks_by_name[deck_name]['new'] = deck

    new_deck_count = 0

    ledger = model.Ledger()
    deck_order = []
    for deck_name,decks in decks_by_name.items():
        deck_order.append(deck_name)
        if 'new' in decks and 'old' in decks:
            old_deck = decks['old']
            old_card_ids = decks['old'].card_ids()
            new_deck = decks['new']
            new_card_ids = decks['new'].card_ids()
            for old_card_id in old_card_ids:
                if not old_card_id in new_card_ids:
                    for ii in range(0,old_deck.card_amount(old_card_id)):
                        ledger.remove_card_from(deck_name, old_card_id)
                else:
                    if old_deck.card_amount(old_card_id) < new_deck.card_amount(old_card_id):
                        delta = new_deck.card_amount(old_card_id) - old_deck.card_amount(old_card_id)
                        for ii in range(0,delta):
                            ledger.add_card_to(deck_name, old_card_id)
                    elif old_deck.card_amount(old_card_id) > new_deck.card_amount(old_card_id):
                        delta = old_deck.card_amount(old_card_id) - new_deck.card_amount(old_card_id)
                        for ii in range(0,delta):
                            ledger.remove_card_from(deck_name, old_card_id)
            for new_card_id in new_card_ids:
                if not new_card_id in old_card_ids:
                    for ii in range(0,new_deck.card_amount(new_card_id)):
                        ledger.add_card_to(deck_name, new_card_id)
        if 'new' in decks and not 'old' in decks:
            new_deck_count += 1
            for new_card_id,amount in decks['new'].cards.items():
                for ii in range(0,amount):
                    ledger.add_card_to(deck_name, new_card_id, is_new=True)
        ledger.ignore_corrections(deck_name)

    moves = calculate_moves(ledger,card_lookup)
    chains = calculate_migration_chain(ledger)
    html.generate_report(deck_order,moves,chains)