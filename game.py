'''
FILNAMN.PY: Finns i sjön

__author__  = "Philip Urhammar"
__version__ = "1.0.0"
__email__   = "philip.urhammar@elev.ga.dbgy.se"
'''

import os
import random



#-------------------------------------------------
#Klasser

class Card:

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return str(self.name)

class Cards:
    def __init__(self):
        self.cards = []

        self.card_values = {
            "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9,
            "10": 10, "J": 11, "Q": 12,
            "K": 13, "A": 14
        }
        self.generate_deck()

    def generate_deck(self):
        self.cards = []
        for name, val in self.card_values.items():
            for i in range(4):
                self.cards.append(Card(name, val))

        random.shuffle(self.cards)

class Player:
    def __init__(self, name="Spelare"):
        self.name = name
        self.hand = []
        self.completed_sets = []

    def add_card_to_hand(self, card):
        self.hand.append(card)

    def has_card(self, card_name):
        for card in self.hand:
            if card.name.upper() == card_name.upper():
                return True
        return False

    def remove_card_from_hand(self, card_name):
        matching = []

        for card in self.hand[:]:
            if card.name.upper() == card_name.upper():
                matching.append(card)
                self.hand.remove(card)
        return matching

    def check_sets(self):
        counts = {}

        for card in self.hand:
            counts[card.name] = counts.get(card.name, 0) + 1

        for rank, count in counts.items():
            if count == 4:
                print(f"{self.name} gjorde klart en kortlek av {rank}!")
                self.completed_sets.append(rank)
                self.remove_card_from_hand(rank)

class Bot(Player):
    def __init__(self, name="Bot"):
        super().__init__(name)

#-------------------------------------------------
#Huvudprogrammet


while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    deck = Cards()
    player = Player("Spelare")
    bot = Bot("Bot")


    for i in range(5):
        if deck.cards:
            player.add_card_to_hand(deck.cards.pop())

        if deck.cards:
            bot.add_card_to_hand(deck.cards.pop())


    player_turn = random.randint(0, 1) == 0
    last_bot_guess = None

    while len(deck.cards) > 0 or len(player.hand) > 0 or len(bot.hand) > 0:
        os.system('cls' if os.name == 'nt' else 'clear')

        print("🂱 FINNS I SJÖN 🂱\n")

        print(f"Kort kvar i sjön: {len(deck.cards)}")

        print(f"Spelarens färdiga kortlekar: {player.completed_sets}")

        print(f"Bottens färdiga kortlekar: {bot.completed_sets}")

        print(f"Din hand: {player.hand}\n")

        if not player.hand and deck.cards:
            player.add_card_to_hand(deck.cards.pop())

        if not bot.hand and deck.cards:
            bot.add_card_to_hand(deck.cards.pop())

        if not player.hand and not deck.cards:
            break

        if not bot.hand and not deck.cards:
            break

        if player_turn:
            print("Spelarens tur")

            guess1 = input(
                "Vilket kort ur din hand vill du fråga efter? (2-10, J, Q, K, A): ").strip().upper()

            if not player.has_card(guess1):
                print("Du kan bara gissa på ett kort du själv har i handen!")

                input("\nTryck Enter för att försöka igen...")
                continue

            if bot.has_card(guess1):
                print(f"Rätt gissat! Botten hade {guess1}.")

                taken = bot.remove_card_from_hand(guess1)

                for card in taken:
                    player.add_card_to_hand(card)

            else:
                print("Fel gissat! Finns i sjön.")

                if deck.cards:
                    player.add_card_to_hand(deck.cards.pop())

                player_turn = False
            player.check_sets()

        else:
            print("Bottens tur")

            if bot.hand:
                possible_guesses = list(set(card.name for card in bot.hand))

                if last_bot_guess in possible_guesses and len(possible_guesses) > 1:
                    possible_guesses.remove(last_bot_guess)

                guess1 = random.choice(possible_guesses)
                last_bot_guess = guess1

                print(f"Botten gissar på: {guess1}")

                if player.has_card(guess1):
                    print(f"Botten gissade rätt och tar dina {guess1}!")
                    taken = player.remove_card_from_hand(guess1)

                    for card in taken:
                        bot.add_card_to_hand(card)

                else:
                    print("Botten gissade fel och drar ett kort från sjön!")

                    if deck.cards:
                        bot.add_card_to_hand(deck.cards.pop())

                    player_turn = True
                bot.check_sets()

            else:
                player_turn = True

        input("\nTryck Enter för nästa tur...")

    #------------------------------------------------
    #Avslutningen
    print("\n🂱 SPELET ÄR SLUT 🂱")

    print(f"Spelarens färdiga kortlekar ({len(player.completed_sets)} st): {player.completed_sets}")

    print(f"Bottens färdiga kortlekar ({len(bot.completed_sets)} st): {bot.completed_sets}")

    if len(player.completed_sets) > len(bot.completed_sets):
        print(f"Grattis, du vann ({len(player.completed_sets)} st > {len(bot.completed_sets)} st)!")

    elif len(bot.completed_sets) > len(player.completed_sets):
        print(f"Botten vann ({len(bot.completed_sets)} st > {len(player.completed_sets)} st)!")

    else:
        print("Det blev oavgjort!")


    while True:
        replay = input("\n🂱 Kör igen? ((J)a/(N)ej): ").capitalize()
        if replay == "J" or replay == "Ja":
            play_again = True
            break

        elif replay == "N" or replay == "Nej":
            print("Tack för att du spelade!")
            play_again = False
            break

        else:
            print("Ogiltigt svar. Försök igen.")

    if not play_again:
        break