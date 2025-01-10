# Marvel Champions - Universal Prebuilt Deck Migrator

This tool helps migrate from older deck lists to newer deck lists in the wonderful [Universal Prebuilt Deck Lists](https://boardgamegeek.com/geeklist/278797/marvel-champions-universal-prebuilt-decks) project by BGG user acharlie1377. It serves as an alternative to taken apart and rebuilding the entire list when new sets are released.

## How to Make a Migration Report

Clone the repo

`pip install -r requirements.txt`

Change the top of main.py to point to the list you are using and the list you want to use. You can find all lists as of 01/09/2024 in the `lists/` directory.

Optionally change the target sheet from the Hero lists to the Aspect lists depending on the kind of decks you use.

`python main.py`

Read the generated `out/report.html`. Follow it top to bottom to migrate from the old decks to the new decks.

## Using the Migration Report

The decks are listed in order by how many cards the new deck takes from an older deck. Higher decks on the list use fewer cards from old decks.

The migrator uses the concept of "the Supply." These are all of the cards in your collection that were not taken from a previous version of a hero's deck. When a card is removed from a hero's deck, it enters "the Supply."

When a card says "from Hero X", then the migrator expects that you take the listed card from Hero X's old deck and use it in the new hero's deck.

Any decks that only appear on the newer list assume that all aspect cards that come with that hero (precon and extra) have already been moved to the supply.

If you want to download your own lists, then ensure they are saved as `.xlsx` files, otherwise the script won't be able to pull color info to determine aspect.