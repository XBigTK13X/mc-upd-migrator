import os

def deck_to_markup(progress, deck_name, moves):
    removals = len([xx for xx in moves if "Remove" in xx.action])
    additions = len([xx for xx in moves if "Add" in xx.action])
    progress_info = ''
    if additions > 0 and removals < 0:
        progress_info = f'[-{removals}/+{additions}]'
    elif additions > 0 and removals >=0:
        progress_info = f'[+{additions}]'
    elif additions <= 0 and removals < 0:
        progress_info = f'[-{removals}]'
    deck_markup = f'''<h2>
        {progress} {deck_name} {progress_info}
        </h2>
        <table>
        '''
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
        a {
            margin: 1.5em;
            font-size: 1em;
        }
        h1 {text-align:center;}
        h2 {margin-top:1em;margin-bottom:.2em;}
        table {border-spacing: 0; border-collapse: collapse;}
        tr {border: solid black 2px;}
        td {padding:0.2em;font-size:1.3em;}
        .link {width:20vw;}
        .col-sm {width:8vw;}
        .col-md {width:30vw;}
        .aspect-basic {background:#99999955;}
        .aspect-aggression {background:#FF000055;}
        .aspect-justice {background:#FFFF0088;}
        .aspect-leadership {background:#6F88EC55;}
        .aspect-protection {background:#00FF0055;}
        .aspect-pool {background:#FA719E55;}
    }
    </style>
    <title>Marvel Champions Deck Migration</title
    </head>
    <body>
        <div>
            <div class="link">
            <a target="_blank" href="https://boardgamegeek.com/geeklist/278797/marvel-champions-universal-prebuilt-decks">BGG GeekList</a>
            </div>
            <div class="link">
            <a target="_blank" href="https://docs.google.com/spreadsheets/d/1uDnn-7Urtprf3awFV0cSUHseIqJQYCVF7ckineFVBP4/edit?usp=sharing">Latest Deck Lists</a>
            </div>
            <div class="link">
            <a target="_blank" href="https://drive.google.com/drive/folders/1M2qAy6ddI7Doj7G1UcX4Me71tnPtwM9J?usp=sharing">Deck Lists Archive</a>
            </div>
            <div class="link">
            <a target="_blank" href="https://github.com/XBigTK13X/mc-upd-migrator">Deck List Migrator</a>
            </div>
        </div>
        (((decks)))
    </body>
    </html>
    '''
        chained = []
        updated_count = len([xx for xx in migration_chains if xx.deck_name in card_moves])
        updated_index = 1
        deck_markup = f'<h1>{updated_count} UPDATED DECKS</h1>'
        for migration_chain in migration_chains:
            if migration_chain.deck_name in card_moves:
                deck_markup += deck_to_markup(f'[{updated_index:03}/{updated_count:03}]', migration_chain.deck_name, card_moves[migration_chain.deck_name])
                chained.append(migration_chain.deck_name)
                updated_index += 1

        new_count = len([xx for xx in deck_order if xx in card_moves and not xx in chained])
        new_index = 1
        deck_markup += f'<hr/><h1>{new_count} NEW DECKS</h1>'
        for deck_name in deck_order:
            if deck_name in card_moves and not deck_name in chained:
                deck_markup += deck_to_markup(f'[{new_index:03}/{new_count:03}]',deck_name,card_moves[deck_name])
                new_index += 1

        decks_without_changes = False
        for deck_name in deck_order:
            if deck_name and not deck_name in card_moves and not deck_name in chained:
                if not decks_without_changes:
                    decks_without_changes = True
                    deck_markup += f'<hr/><h1>UNCHANGED DECKS</h1>'
                deck_markup += f'<h2>{deck_name}</h2>'

        html_markup = html_markup.replace('(((decks)))',deck_markup)
        write_handle.write(html_markup)