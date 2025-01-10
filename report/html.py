import os

def deck_to_markup(deck_name, moves):
    deck_markup = f'<h2>{deck_name}</h2><table>'
    entries = [f'''
            <tr class="aspect-{xx.card.aspect}">
            <td class="col-sm">{xx.action}</td>
            <td class="col-sm">{xx.card.aspect}</td>
            <td class="col-sm">{xx.card.kind}</td>
            <td class="col-md">{xx.card.name}</td>
            <td class="col-md">{xx.direction} {xx.target}</td>
            </tr>'''
            for xx in moves]
    for entry in entries:
        deck_markup += f'{entry}'
    deck_markup += "</table>"
    return deck_markup

def generate_report(deck_order,card_moves,migration_chains):
    os.makedirs('./out/',exist_ok=True)
    write_path = './out/report.html'
    with open(write_path,'w',encoding='utf-8') as write_handle:
        html_markup = '''
    <html>
    <head>
    <style>
    @media print, screen {
        body {margin: 2em; font-size:1.5em;}
        h2 {margin-top:1em;margin-bottom:0;}
        table {border-spacing: 0; border-collapse: collapse;}
        tr {border: solid black 2px;}
        td {padding:0.2em;font-size:1.3em;}
        .col-sm {width:8vw;}
        .col-md {width:30vw;}
        .aspect-basic {background:#99999955;}
        .aspect-aggression {background:#FF000055;}
        .aspect-justice {background:#FFFF0088;}
        .aspect-leadership {background:#6FA8DC55;}
        .aspect-protection {background:#00FF0055;}
        .aspect-pool {background:#FA719E55;}
    }
    </style>
    <title>Marvel Champions Deck Migration</title
    </head>
    <body>
        (((decks)))
    </body>
    </html>
    '''
        deck_markup = '<h1>UPDATED DECKS</h1>'
        chained = []
        for migration_chain in migration_chains:
            if migration_chain.deck_name in card_moves:
                deck_markup += deck_to_markup(migration_chain.deck_name, card_moves[migration_chain.deck_name])
                chained.append(migration_chain.deck_name)
        deck_markup += '<hr/><h1>NEW DECKS</h1>'
        for deck_name in deck_order:
            if deck_name in card_moves and not deck_name in chained:
                deck_markup += deck_to_markup(deck_name,card_moves[deck_name])
        html_markup = html_markup.replace('(((decks)))',deck_markup)
        decks_without_changes = False
        for deck_name in deck_order:
            if deck_name and not deck_name in card_moves and not deck_name in chained:
                if not decks_without_changes:
                    decks_without_changes = True
                    html_markup += f'<hr/><h1>UNCHANGED DECKS</h1>'
                html_markup += f'<h2>{deck_name}</h2>'
        write_handle.write(html_markup)