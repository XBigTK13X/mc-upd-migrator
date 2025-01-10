ASPECT_COLORS = {
    'FF999999': 'Basic',
    'FFFF0000': 'Aggression',
    'FF6FA8DC': 'Leadership',
    'FFFFFF00': 'Justice',
    'FF00FF00': 'Protection',
    'FFFA719E': "Pool"
}

KIND_ORDER = {
    'Ally': 0,
    'Support': 1,
    'Event': 2,
    'Upgrade': 3,
    'Resource': 4,
    'Player Side Scheme': 5
}

ASPECT_ORDER = {
    'Basic': 6,
    'Aggression': 1,
    'Leadership': 2,
    'Justice': 3,
    'Protection': 4,
    'Pool': 5
}

class Card:
    def __init__(self, name, kind, color):
        global ASPECT_COLORS
        global KIND_ORDER
        self.name = name
        self.kind = kind
        self.color = color.rgb
        self.aspect = ASPECT_COLORS[self.color]
        self.id = f'[{self.aspect} - {self.kind}] {self.name}'
        self.kind_order = KIND_ORDER[self.kind]
        self.aspect_order = ASPECT_ORDER[self.aspect]

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

class MigrationChain:
    def __init__(self, deck_name):
        self.deck_name = deck_name
        self.connections = []

    def connect(self, deck_name):
        if not deck_name in self.connections:
            self.connections.append(deck_name)

    def connection_count(self):
        return len(self.connections)

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

    @staticmethod
    def sort_order(a,b):
        if a.source == a.deck_name and b.source != b.deck_name:
            return -1
        if b.source == b.deck_name and a.source != a.deck_name:
            return 1
        if a.source == 'Supply' and b.source != 'Supply':
            return -1
        if b.source == 'Supply' and a.source != 'Supply':
            return 1
        if a.card.aspect_order != b.card.aspect_order:
            return a.card.aspect_order - b.card.aspect_order
        if a.card.kind_order != b.card.kind_order:
            return a.card.kind_order - b.card.kind_order
        return -1 if a.card.id < b.card.id else 1

    def __repr__(self):
        return f'{self.action} {self.card.id} {self.direction} {self.target}'

    def __str__(self):
        return self.__repr__()

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

    def ignore_corrections(self,deck_name):
        # TODO When a card correction was made, it can be ignored
        # For example, NeXt Generation to Apocalypse changed Drax's Booster Boots from Support to Upgrade
        pass