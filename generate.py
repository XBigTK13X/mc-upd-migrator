import openpyxl
from report import html,stdout,text,markdown

ASPECT_COLORS = {
    'FF999999': 'Basic',
    'FFFF0000': 'Aggression',
    'FF6FA8DC': 'Leadership',
    'FFFFFF00': 'Justice',
    'FF00FF00': 'Protection',
    'FFFA719E': "Pool"
}

class Card:
    def __init__(self, name, kind, color):
        global ASPECT_COLORS
        self.name = name
        self.kind = kind
        self.color = color.rgb
        self.aspect = ASPECT_COLORS[self.color]
        self.id = f'[{self.aspect} - {self.kind}] {self.name}'

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.name} [{self.kind} - {self.aspect}] '

class CardPool:
    def __init__(self, name, kind, column_index=None):
        self.name = name
        self.cards = {}
        self.kind = kind
        self.column_index = column_index

    def put_card(self,card_id,count=1):
        if not card_id in self.cards:
            self.cards[card_id] = 0
        self.cards[card_id] += count

    def card_ids(self):
        return list(self.cards.keys())

    def card_amount(self,card_id):
        if not card_id in self.cards:
            return 0
        return self.cards[card_id]

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f'{self.cards}'

class LedgerEntry:
    def __init__(self, deck_name, source, destination, card):
        self.deck_name = deck_name
        self.source = source
        self.destination = destination
        self.card = card

        self.action = 'Add'
        self.direction = 'from'
        if self.source == self.deck_name:
            self.action = 'Remove'
            self.direction = 'to'
        self.target = self.source
        if self.source == 'Supply':
            self.target = 'the Supply'
        if self.destination == 'Supply':
            self.target = 'the Supply'

    def __repr__(self):
        return f'{self.action} {self.card.id} {self.direction} {self.target}'

    def __str__(self):
        return self.__repr__()

class MigrationChain:
    def __init__(self, deck_name):
        self.deck_name = deck_name
        self.connections = []

    def connect(self, deck_name):
        if not deck_name in self.connections:
            self.connections.append(deck_name)

    def connection_count(self):
        return len(self.connections)

class Ledger:
    def __init__(self):
        self.cards = {}
        self.deck_hits = {}
        self.new_decks = []
        self.deck_connections = {}

    def remove_card_from(self,deck_name,card_id):
        if not card_id in self.cards:
            self.cards[card_id] = {'to':[],'from':[]}
        self.cards[card_id]['from'].append(deck_name)
        if not deck_name in self.deck_hits:
            self.deck_hits[deck_name] = 0
        self.deck_hits[deck_name] += 1

    def add_card_to(self,deck_name,card_id,is_new=False):
        if is_new:
            if not deck_name in self.new_decks:
                self.new_decks.append(deck_name)
        if not card_id in self.cards:
            self.cards[card_id] = {'to':[],'from':[]}
        self.cards[card_id]['to'].append(deck_name)
        if not deck_name in self.deck_hits:
            self.deck_hits[deck_name] = 0
        self.deck_hits[deck_name] += 1

    def calculate_moves(self,card_lookup):
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
        ordered_deck_names = sorted(list(self.deck_hits.keys()), key = lambda xx: self.deck_hits[xx])
        for deck_name in ordered_deck_names:
            moves[deck_name] = []
            is_new = deck_name in self.new_decks
            for card_id,entries in self.cards.items():
                from_count = len([xx for xx in entries['from'] if xx == deck_name])
                to_count = len([xx for xx in entries['to'] if xx == deck_name])
                if not is_new and not deck_name in self.deck_connections and (from_count > 0 or to_count > 0):
                    self.deck_connections[deck_name] = MigrationChain(deck_name)
                if to_count > 0:
                    if is_new:
                        for ii in range(0, to_count):
                            moves[deck_name].append(LedgerEntry(deck_name,'Supply',deck_name,card_lookup[card_id]))
                    else:
                        for ii in range(0, to_count):
                            if len(entries['from']) > 0:
                                source_deck = entries['from'].pop()
                                moves[deck_name].append(LedgerEntry(deck_name,source_deck,deck_name,card_lookup[card_id]))
                                self.deck_connections[deck_name].connect(source_deck)
                            else:
                                self.deck_connections[deck_name].connect('Supply')
                                moves[deck_name].append(LedgerEntry(deck_name,'Supply',deck_name,card_lookup[card_id]))
                if from_count > 0:
                    self.deck_connections[deck_name].connect('Supply')
                    for ii in range(0, from_count):
                        moves[deck_name].append(LedgerEntry(deck_name,deck_name,'Supply',card_lookup[card_id]))
            import functools
            moves[deck_name] = sorted(moves[deck_name],key=functools.cmp_to_key(move_sort))
        return moves

    def calculate_migration_chain(self):
        chains = []
        for deck_name,migration_chain in self.deck_connections.items():
            chains.append(migration_chain)
        chains = sorted(chains,key=lambda xx: xx.connection_count())
        return chains

    def ignore_corrections(self,deck_name):
        # TODO When a card correction was made, it can be ignored
        # For example, NeXt Generation to Apocalypse changed Drax's Booster Boots from Support to Upgrade
        pass


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
                    deck = CardPool(name=xls_cell.value, kind='deck', column_index=col_count)
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
                    card = Card(name=xls_row[ii].value,kind=xls_row[ii+1].value,color=xls_row[ii].fill.bgColor)
                    if not card.id in card_lookup:
                        card_lookup[card.id] = card
                    deck_name = names_by_column_index[column_index]
                    deck = decks_by_name[deck_name]
                    deck.put_card(card.id)
                    decks_by_name[deck_name] = deck
        row_count += 1
    return decks_by_name,card_lookup

def build_ledger(old_list,new_list,deck_sheet):
    card_lookup = {}
    old_decks,card_lookup = read_decks_from_xls(old_list,deck_sheet,card_lookup)
    new_decks,card_lookup = read_decks_from_xls(new_list,deck_sheet,card_lookup)
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

    ledger = Ledger()
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

    moves = ledger.calculate_moves(card_lookup)
    chains = ledger.calculate_migration_chain()
    html.generate_report(deck_order,moves,chains)