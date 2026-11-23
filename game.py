'''
FILNAMN.PY: Finns i sjön

__author__  = "Philip Urhammar"
__version__ = "3.2.0"
__email__   = "philip.urhammar@elev.ga.dbgy.se"
'''

import math
import random
import pygame
from pygame.math import Vector2


# -------------------------------------------------
# Klasser

class Card:
    def __init__(self, name, value, suit):
        self.name = name
        self.value = value
        self.suit = suit

    def __repr__(self):
        return f"{self.name}{self.suit}"


class Cards:
    def __init__(self):
        self.cards = []
        self.card_values = {
            "2": 2, "3": 3, "4": 4, "5": 5,
            "6": 6, "7": 7, "8": 8, "9": 9,
            "10": 10, "J": 11, "Q": 12,
            "K": 13, "A": 14
        }
        self.suits = ["♥", "♦", "♠", "♣"]
        self.generate_deck()

    def generate_deck(self):
        self.cards = []
        for name, val in self.card_values.items():
            for suit in self.suits:
                self.cards.append(Card(name, val, suit))

        random.shuffle(self.cards)


class Player:
    def __init__(self, name="Spelare"):
        self.name = name
        self.hand = []
        self.completed_sets = []

    def add_card_to_hand(self, card):
        self.hand.append(card)
        self.sort_hand()

    def sort_hand(self):
        self.hand.sort(key=lambda c: (c.value, c.suit))

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
        new_sets = []

        for card in self.hand:
            counts[card.name] = counts.get(card.name, 0) + 1

        for rank, count in counts.items():
            if count == 4:
                self.completed_sets.append(rank)
                self.remove_card_from_hand(rank)
                new_sets.append(rank)
        return new_sets


class Bot(Player):
    """AI-spelare med kortminne och utvärdering av tidigare drag."""

    def __init__(self, name="Bot"):
        super().__init__(name)
        self.known_player_ranks = set()
        self.failed_ranks = set()
        self.last_guess = None
        self.ai_thought = "Analyserar handen..."

    def observe_player_guess(self, rank, success):
        self.known_player_ranks.add(rank)
        self.failed_ranks.discard(rank)

    def observe_player_lost_rank(self, rank):
        self.known_player_ranks.discard(rank)

    def learn_from_own_turn(self, rank, got_cards, completed_set):
        """AI:n utvärderar hur det egna draget gick och uppdaterar sin strategi."""
        self.last_guess = rank
        if completed_set:
            self.known_player_ranks.discard(rank)
            self.failed_ranks.discard(rank)
            self.ai_thought = f"Fyrtal i {rank} klart! Byter fokus."
        elif got_cards > 0:
            self.known_player_ranks.discard(rank)
            self.failed_ranks.discard(rank)
            self.ai_thought = f"Tog {got_cards} st {rank}! Nu har jag fler av den."
        else:
            self.failed_ranks.add(rank)
            self.ai_thought = f"Missade på {rank}, undviker den nästa gång."

    def choose_guess(self):
        """Väljer bästa drag genom att poängsätta varje möjlig gissning."""
        if not self.hand:
            return None

        counts = {}
        for card in self.hand:
            counts[card.name] = counts.get(card.name, 0) + 1

        best_rank = None
        best_score = -999

        for rank, count in counts.items():
            score = count * 10

            if rank in self.known_player_ranks:
                score += 50
            if rank in self.failed_ranks:
                score -= 25
            if rank == self.last_guess and len(counts) > 1:
                score -= 40

            score += random.uniform(0, 4)

            if score > best_score:
                best_score = score
                best_rank = rank

        if best_rank in self.known_player_ranks:
            self.ai_thought = f"Minns att du frågade efter {best_rank}!"
        elif counts[best_rank] >= 2:
            self.ai_thought = f"Har redan {counts[best_rank]} st {best_rank}, jagar fyrtal."
        else:
            self.ai_thought = f"Testar lyckan på {best_rank}."

        return best_rank


# -------------------------------------------------
# Animationer & Partikeleffekter

class FlyingCard:
    def __init__(self, start_pos, end_pos, card=None, face_up=False, duration=420):
        self.start = Vector2(start_pos)
        self.end = Vector2(end_pos)
        self.card = card
        self.face_up = face_up
        self.start_time = pygame.time.get_ticks()
        self.duration = max(1, duration)
        self.done = False

    def update(self, now):
        raw_t = (now - self.start_time) / self.duration
        if raw_t >= 1.0:
            self.done = True
            return self.end.x, self.end.y, 0.0

        t = max(0.0, min(1.0, raw_t))
        ease = max(0.0, min(1.0, 1.0 - (1.0 - t) ** 3))
        pos = self.start.lerp(self.end, ease)
        arc = math.sin(t * math.pi)
        return pos.x, pos.y - arc * 35.0, arc


class Particle:
    def __init__(self, x, y, color):
        self.pos = Vector2(x, y)
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2.0, 6.5)
        self.vel = Vector2(math.cos(angle) * speed, math.sin(angle) * speed - 2)
        self.color = color
        self.life = random.randint(35, 65)
        self.size = random.randint(4, 8)

    def update(self):
        self.pos += self.vel
        self.vel.y += 0.15
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.size)


# -------------------------------------------------
# Grafikinställningar och ritfunktioner

pygame.init()
BREDD, HOJD = 1100, 720
skarm = pygame.display.set_mode((BREDD, HOJD))
pygame.display.set_caption("Finns i sjön - Philip Urhammar")
klocka = pygame.time.Clock()

font_titel = pygame.font.SysFont("arial", 40, bold=True)
font_stor = pygame.font.SysFont("arial", 26, bold=True)
font_mellan = pygame.font.SysFont("arial", 20, bold=True)
font_liten = pygame.font.SysFont("arial", 15, bold=True)
font_kort_horn = pygame.font.SysFont("arial", 18, bold=True)
font_kort_pip = pygame.font.SysFont("arial", 19)
font_kort_klad = pygame.font.SysFont("arial", 44, bold=True)

BORD_GRON = (24, 88, 46)
BORD_MITT = (32, 108, 58)
BORD_RAM = (15, 58, 30)
VIT = (250, 250, 250)
SVART = (25, 25, 25)
ROD = (205, 35, 35)
GULD = (255, 215, 0)
BAKSIDA_BLA = (30, 65, 145)
BAKSIDA_LJUS = (65, 110, 205)
KNAPP_GRON = (40, 145, 75)
KNAPP_HOVER = (55, 175, 95)
KNAPP_ROD = (180, 45, 45)
KNAPP_ROD_HOVER = (215, 60, 60)

PIP_LAYOUTS = {
    "2": [(0.5, 0.25), (0.5, 0.75)],
    "3": [(0.5, 0.22), (0.5, 0.50), (0.5, 0.78)],
    "4": [(0.34, 0.25), (0.66, 0.25), (0.34, 0.75), (0.66, 0.75)],
    "5": [(0.34, 0.25), (0.66, 0.25), (0.50, 0.50), (0.34, 0.75), (0.66, 0.75)],
    "6": [(0.34, 0.23), (0.66, 0.23), (0.34, 0.50), (0.66, 0.50), (0.34, 0.77), (0.66, 0.77)],
    "7": [(0.34, 0.23), (0.66, 0.23), (0.50, 0.36), (0.34, 0.50), (0.66, 0.50), (0.34, 0.77), (0.66, 0.77)],
    "8": [(0.34, 0.23), (0.66, 0.23), (0.50, 0.36), (0.34, 0.50), (0.66, 0.50), (0.50, 0.64), (0.34, 0.77), (0.66, 0.77)],
    "9": [(0.34, 0.20), (0.66, 0.20), (0.34, 0.40), (0.66, 0.40), (0.50, 0.50), (0.34, 0.60), (0.66, 0.60), (0.34, 0.80), (0.66, 0.80)],
    "10": [(0.34, 0.20), (0.66, 0.20), (0.50, 0.30), (0.34, 0.40), (0.66, 0.40), (0.34, 0.60), (0.66, 0.60), (0.50, 0.70), (0.34, 0.80), (0.66, 0.80)],
}


def rita_kort_framsida(yta, x, y, card, hovrad=False, skugga_offset=4):
    rekt = pygame.Rect(int(x), int(y), 95, 140)
    if hovrad:
        rekt.y -= 22

    skugga = rekt.move(skugga_offset, skugga_offset + 2)
    pygame.draw.rect(yta, (12, 42, 22), skugga, border_radius=10)

    pygame.draw.rect(yta, VIT, rekt, border_radius=10)
    ram_farg = GULD if hovrad else SVART
    ram_bredd = 3 if hovrad else 2
    pygame.draw.rect(yta, ram_farg, rekt, width=ram_bredd, border_radius=10)

    text_farg = ROD if card.suit in ["♥", "♦"] else SVART

    t_val = font_kort_horn.render(card.name, True, text_farg)
    t_suit = font_kort_horn.render(card.suit, True, text_farg)
    yta.blit(t_val, (rekt.x + 6, rekt.y + 5))
    yta.blit(t_suit, (rekt.x + 7, rekt.y + 23))

    yta.blit(t_val, (rekt.right - t_val.get_width() - 6, rekt.bottom - 42))
    yta.blit(t_suit, (rekt.right - t_suit.get_width() - 7, rekt.bottom - 24))

    if card.name in PIP_LAYOUTS:
        t_pip = font_kort_pip.render(card.suit, True, text_farg)
        for rx, ry in PIP_LAYOUTS[card.name]:
            px = rekt.x + int(rekt.width * rx)
            py = rekt.y + int(rekt.height * ry)
            yta.blit(t_pip, t_pip.get_rect(center=(px, py)))
    else:
        inre_ram = rekt.inflate(-32, -32)
        pygame.draw.rect(yta, (240, 240, 245), inre_ram, border_radius=6)
        pygame.draw.rect(yta, text_farg, inre_ram, width=1, border_radius=6)

        if card.name == "A":
            t_stor = font_kort_klad.render(card.suit, True, text_farg)
            yta.blit(t_stor, t_stor.get_rect(center=rekt.center))
        else:
            t_bokstav = font_kort_klad.render(card.name, True, text_farg)
            yta.blit(t_bokstav, t_bokstav.get_rect(center=(rekt.centerx, rekt.centery - 10)))
            t_liten_suit = font_kort_pip.render(card.suit, True, text_farg)
            yta.blit(t_liten_suit, t_liten_suit.get_rect(center=(rekt.centerx, rekt.centery + 22)))

    return rekt


def rita_kort_baksida(yta, x, y, markera_klickbar=False, puls=0):
    rekt = pygame.Rect(int(x), int(y), 95, 140)
    skugga = rekt.move(4, 5)
    pygame.draw.rect(yta, (12, 42, 22), skugga, border_radius=10)

    pygame.draw.rect(yta, VIT, rekt, border_radius=10)
    inre = rekt.inflate(-12, -12)
    pygame.draw.rect(yta, BAKSIDA_BLA, inre, border_radius=6)
    pygame.draw.rect(yta, BAKSIDA_LJUS, inre, width=2, border_radius=6)

    if markera_klickbar:
        glod = rekt.inflate(puls, puls)
        pygame.draw.rect(yta, GULD, glod, width=4, border_radius=12)
    else:
        pygame.draw.rect(yta, SVART, rekt, width=2, border_radius=10)
    return rekt


def rita_fardiga_hogar(yta, start_x, start_y, titel, sets):
    t_rubrik = font_liten.render(f"{titel} ({len(sets)})", True, VIT)
    yta.blit(t_rubrik, (start_x, start_y - 26))

    if not sets:
        tom_rekt = pygame.Rect(start_x, start_y, 52, 72)
        pygame.draw.rect(yta, (20, 72, 38), tom_rekt, border_radius=6)
        pygame.draw.rect(yta, (45, 120, 70), tom_rekt, width=2, border_radius=6)
        return

    for idx, rank in enumerate(sets):
        kol = idx % 3
        rad = idx // 3
        hx = start_x + kol * 64
        hy = start_y + rad * 84

        for lager in range(2, 0, -1):
            under = pygame.Rect(hx - lager * 2, hy - lager * 2, 52, 72)
            pygame.draw.rect(yta, (210, 210, 210), under, border_radius=6)
            pygame.draw.rect(yta, SVART, under, width=1, border_radius=6)

        topp = pygame.Rect(hx, hy, 52, 72)
        pygame.draw.rect(yta, VIT, topp, border_radius=6)
        pygame.draw.rect(yta, GULD, topp, width=2, border_radius=6)

        farg = ROD if rank in ["A", "K", "Q", "J"] else SVART
        t_rank = font_mellan.render(rank, True, farg)
        yta.blit(t_rank, t_rank.get_rect(center=topp.center))


def berakna_kort_x(antal, bredd_kort=95):
    if antal == 0:
        return []
    omrade_start = 240
    # Lämna lite utrymme till höger så kort inte krockar med topp-knapparna
    omrade_bredd = BREDD - 380
    steg = min(92, (omrade_bredd - bredd_kort) // max(1, antal - 1)) if antal > 1 else 0
    total_bredd = (antal - 1) * steg + bredd_kort
    start_x = omrade_start + (omrade_bredd - total_bredd) // 2
    return [start_x + i * steg for i in range(antal)]


def hitta_hovrat_kort(rektanglar, mus_pos):
    for i in range(len(rektanglar) - 1, -1, -1):
        if rektanglar[i].collidepoint(mus_pos):
            return i
    return None


def skapa_fyrverkeri(x, y, antal=35):
    farger = [GULD, VIT, (255, 100, 100), (100, 220, 255), (120, 255, 140)]
    return [Particle(x, y, random.choice(farger)) for _ in range(antal)]


def starta_ny_match():
    deck = Cards()
    player = Player("Spelare")
    bot = Bot("Bot")

    for _ in range(5):
        if deck.cards:
            player.add_card_to_hand(deck.cards.pop())
        if deck.cards:
            bot.add_card_to_hand(deck.cards.pop())

    player_starts = random.randint(0, 1) == 0
    if player_starts:
        state = "PLAYER_GUESS"
        msg = "Du börjar! Klicka på ett kort i din hand för att fråga botten."
    else:
        state = "BOT_TURN"
        msg = "Botten börjar och studerar sin hand..."

    return deck, player, bot, state, msg


# -------------------------------------------------
# Huvudprogrammet

deck, player, bot, state, message = starta_ny_match()
bot_timer = pygame.time.get_ticks() + 1200

# Slutskärmens ruta och knapp
slut_ruta = pygame.Rect(BREDD // 2 - 280, 145, 560, 430)
replay_knapp = pygame.Rect(slut_ruta.centerx - 125, slut_ruta.bottom - 85, 250, 54)
sjon_rekt = pygame.Rect(240 + (BREDD - 380) // 2 - 47, HOJD // 2 - 70, 95, 140)

# Knappar längst upp åt höger
stang_knapp = pygame.Rect(BREDD - 125, 24, 100, 36)
starta_om_knapp = pygame.Rect(BREDD - 245, 24, 110, 36)

flying_cards = []
particles = []
konfetti_timer = 0

kor = True
while kor:
    nu = pygame.time.get_ticks()
    mus_pos = pygame.mouse.get_pos()

    for fc in flying_cards[:]:
        fc.update(nu)
        if fc.done:
            flying_cards.remove(fc)

    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)

    # Fyll på hand automatiskt om någon blir tom medan sjön har kort
    if state != "GAME_OVER" and not flying_cards:
        if not player.hand and deck.cards:
            c = deck.cards.pop()
            player.add_card_to_hand(c)
            flying_cards.append(FlyingCard(sjon_rekt.topleft, (540, 535), c, True))
        if not bot.hand and deck.cards:
            c = deck.cards.pop()
            bot.add_card_to_hand(c)
            flying_cards.append(FlyingCard(sjon_rekt.topleft, (540, 35), None, False))

        if (not deck.cards and not player.hand and not bot.hand) or (
            len(player.completed_sets) + len(bot.completed_sets) == 13
        ):
            state = "GAME_OVER"
            if len(player.completed_sets) > len(bot.completed_sets):
                particles.extend(skapa_fyrverkeri(BREDD // 2, 260, 70))

    klick_x = berakna_kort_x(len(player.hand))
    klick_rektanglar = [pygame.Rect(x, 535, 95, 140) for x in klick_x]
    hovrat_index = hitta_hovrat_kort(klick_rektanglar, mus_pos) if state == "PLAYER_GUESS" else None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            kor = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Globala toppknappar längst upp till höger (funkar alltid)
            if stang_knapp.collidepoint(event.pos):
                kor = False
                break

            if starta_om_knapp.collidepoint(event.pos):
                deck, player, bot, state, message = starta_ny_match()
                flying_cards.clear()
                particles.clear()
                bot_timer = nu + 1200
                continue

            # Spelinteraktioner (pausade under flygande animationer)
            if not flying_cards:
                # 1. Spelaren frågar om ett kort
                if state == "PLAYER_GUESS" and hovrat_index is not None and hovrat_index < len(player.hand):
                    valda_kortet = player.hand[hovrat_index]
                    guess1 = valda_kortet.name

                    if bot.has_card(guess1):
                        bot.observe_player_guess(guess1, True)
                        taken = bot.remove_card_from_hand(guess1)
                        for idx, card in enumerate(taken):
                            player.add_card_to_hand(card)
                            flying_cards.append(
                                FlyingCard((540 + idx * 20, 35), (klick_x[hovrat_index], 535), card, True, 450)
                            )
                        nya_set = player.check_sets()
                        if nya_set:
                            bot.observe_player_lost_rank(nya_set[0])
                            particles.extend(skapa_fyrverkeri(120, 480, 45))
                            message = f"Snyggt! Du tog {len(taken)} st {guess1} och fick fyrtal i {nya_set[0]}! Gissa igen!"
                        else:
                            message = f"Rätt gissat! Botten gav dig {len(taken)} st {guess1}. Gissa igen!"
                    else:
                        bot.observe_player_guess(guess1, False)
                        if deck.cards:
                            state = "PLAYER_DRAW"
                            message = "Botten: 'Finns i sjön!' Klicka på högen i mitten för att dra."
                        else:
                            state = "BOT_TURN"
                            bot_timer = nu + 1200
                            message = "Finns i sjön, men högen är tom! Bottens tur..."

                # 2. Spelaren drar ett kort från sjön
                elif state == "PLAYER_DRAW":
                    if sjon_rekt.collidepoint(event.pos) and deck.cards:
                        draget = deck.cards.pop()
                        player.add_card_to_hand(draget)
                        flying_cards.append(FlyingCard(sjon_rekt.topleft, (560, 535), draget, True, 400))
                        nya_set = player.check_sets()
                        if nya_set:
                            bot.observe_player_lost_rank(nya_set[0])
                            particles.extend(skapa_fyrverkeri(120, 480, 45))
                            message = f"Du drog {draget} och fick fyrtal i {nya_set[0]}! Bottens tur..."
                        else:
                            message = f"Du drog {draget}. Bottens tur..."
                        state = "BOT_TURN"
                        bot_timer = nu + 1400

                # 3. Spela igen-knapp på slutskärmen
                elif state == "GAME_OVER":
                    if replay_knapp.collidepoint(event.pos):
                        deck, player, bot, state, message = starta_ny_match()
                        flying_cards.clear()
                        particles.clear()
                        bot_timer = nu + 1200

    # Bottens AI-tur
    if state == "BOT_TURN" and nu >= bot_timer and not flying_cards:
        guess1 = bot.choose_guess()
        if guess1:
            if player.has_card(guess1):
                taken = player.remove_card_from_hand(guess1)
                for idx, card in enumerate(taken):
                    bot.add_card_to_hand(card)
                    flying_cards.append(
                        FlyingCard((540 + idx * 20, 535), (540, 35), card, True, 480)
                    )
                nya_set = bot.check_sets()
                bot.learn_from_own_turn(guess1, len(taken), bool(nya_set))

                if nya_set:
                    particles.extend(skapa_fyrverkeri(120, 120, 40))
                    message = f"Botten gissade rätt på {guess1} och fick fyrtal i {nya_set[0]}!"
                else:
                    message = f"Botten gissade rätt på {guess1} och tog {len(taken)} kort från dig!"
                bot_timer = nu + 1600
            else:
                if deck.cards:
                    bot.add_card_to_hand(deck.cards.pop())
                    flying_cards.append(FlyingCard(sjon_rekt.topleft, (560, 35), None, False, 400))
                    nya_set = bot.check_sets()
                    bot.learn_from_own_turn(guess1, 0, bool(nya_set))

                    if nya_set:
                        particles.extend(skapa_fyrverkeri(120, 120, 40))
                        message = f"Botten gissade fel på {guess1}, drog kort och fick fyrtal i {nya_set[0]}! Din tur."
                    else:
                        message = f"Botten gissade fel på {guess1} och drog ett kort från sjön. Din tur!"
                else:
                    bot.learn_from_own_turn(guess1, 0, False)
                    message = f"Botten gissade fel på {guess1} (sjön tom). Din tur!"
                state = "PLAYER_GUESS"
        else:
            state = "PLAYER_GUESS"
            message = "Botten har inga kort kvar. Din tur!"

    # -------------------------------------------------
    # Rita spelbordet

    skarm.fill(BORD_GRON)
    pygame.draw.rect(skarm, BORD_RAM, (10, 10, BREDD - 20, HOJD - 20), width=8, border_radius=24)
    pygame.draw.ellipse(skarm, BORD_MITT, (250, 140, BREDD - 310, HOJD - 280))

    # Vänster sidopanel för färdiga korthögar
    panel_rekt = pygame.Rect(24, 24, 210, HOJD - 48)
    pygame.draw.rect(skarm, (18, 68, 36), panel_rekt, border_radius=16)
    pygame.draw.rect(skarm, (42, 125, 72), panel_rekt, width=2, border_radius=16)

    rita_fardiga_hogar(skarm, 38, 60, "Bottens högar", bot.completed_sets)
    pygame.draw.line(skarm, (42, 125, 72), (38, HOJD // 2), (218, HOJD // 2), 2)
    rita_fardiga_hogar(skarm, 38, HOJD // 2 + 42, "Dina högar", player.completed_sets)

    # Rita det aktiva brädet
    if state != "GAME_OVER":
        bot_x = berakna_kort_x(len(bot.hand))
        for x in bot_x:
            rita_kort_baksida(skarm, x, 35)

        t_ai = font_liten.render(f"AI-strategi: {bot.ai_thought}", True, (185, 235, 195))
        skarm.blit(t_ai, t_ai.get_rect(center=(sjon_rekt.centerx, 185)))

        puls = int((math.sin(nu * 0.008) + 1) * 4) if state == "PLAYER_DRAW" else 0
        if deck.cards:
            for offset in range(min(4, len(deck.cards))):
                rita_kort_baksida(
                    skarm,
                    sjon_rekt.x - offset * 3,
                    sjon_rekt.y - offset * 3,
                    markera_klickbar=(state == "PLAYER_DRAW" and offset == min(4, len(deck.cards)) - 1),
                    puls=puls,
                )
            t_sjon = font_mellan.render(f"Sjön: {len(deck.cards)} kort", True, VIT)
            skarm.blit(t_sjon, t_sjon.get_rect(center=(sjon_rekt.centerx, sjon_rekt.bottom + 24)))
        else:
            t_tom = font_mellan.render("Sjön är tom", True, (180, 220, 180))
            skarm.blit(t_tom, t_tom.get_rect(center=sjon_rekt.center))

        banner_rekt = pygame.Rect(275, 206, BREDD - 335, 44)
        pygame.draw.rect(skarm, (15, 55, 28), banner_rekt, border_radius=12)
        pygame.draw.rect(skarm, GULD if state == "PLAYER_DRAW" else (60, 150, 90), banner_rekt, width=2, border_radius=12)
        t_info = font_mellan.render(message, True, GULD if state == "PLAYER_DRAW" else VIT)
        skarm.blit(t_info, t_info.get_rect(center=banner_rekt.center))

        spelare_x = berakna_kort_x(len(player.hand))
        for i, card in enumerate(player.hand):
            if i != hovrat_index:
                rita_kort_framsida(skarm, spelare_x[i], 535, card, hovrad=False)

        if hovrat_index is not None and hovrat_index < len(player.hand):
            rita_kort_framsida(
                skarm,
                spelare_x[hovrat_index],
                535,
                player.hand[hovrat_index],
                hovrad=True,
            )

        for fc in flying_cards:
            fx, fy, hojd = fc.update(nu)
            skugga = int(4 + hojd * 14)
            if fc.face_up and fc.card:
                rita_kort_framsida(skarm, fx, fy, fc.card, hovrad=False, skugga_offset=skugga)
            else:
                rita_kort_baksida(skarm, fx, fy)

    # Partiklar
    for p in particles:
        p.draw(skarm)

    # Slutskärm
    if state == "GAME_OVER":
        spelare_poang = len(player.completed_sets)
        bot_poang = len(bot.completed_sets)
        vinst = spelare_poang > bot_poang
        oavgjort = spelare_poang == bot_poang

        if vinst and nu > konfetti_timer:
            particles.extend(skapa_fyrverkeri(random.randint(250, 850), random.randint(150, 350), 18))
            konfetti_timer = nu + 450

        kant_farg = GULD if vinst else ((180, 180, 180) if oavgjort else (230, 80, 80))

        pygame.draw.rect(skarm, (12, 42, 22), slut_ruta.move(6, 8), border_radius=22)
        pygame.draw.rect(skarm, (18, 48, 32), slut_ruta, border_radius=22)
        pygame.draw.rect(skarm, kant_farg, slut_ruta, width=4, border_radius=22)

        if vinst:
            rubrik_text = "GRATTIS, DU VANN!"
            under_text = "Du överlistade AI:n och regerar över sjön!"
        elif oavgjort:
            rubrik_text = "DET BLEV OAVGJORT!"
            under_text = "Jämnt skägg hela vägen!"
        else:
            rubrik_text = "TYVÄRR, DU FÖRLORADE"
            under_text = "AI:n läste ditt spel och knep flest fyrtal."

        t_rubrik = font_titel.render(rubrik_text, True, kant_farg)
        t_under = font_mellan.render(under_text, True, VIT)
        skarm.blit(t_rubrik, t_rubrik.get_rect(center=(slut_ruta.centerx, slut_ruta.top + 65)))
        skarm.blit(t_under, t_under.get_rect(center=(slut_ruta.centerx, slut_ruta.top + 115)))

        pygame.draw.line(
            skarm,
            (55, 110, 75),
            (slut_ruta.left + 40, slut_ruta.top + 150),
            (slut_ruta.right - 40, slut_ruta.top + 150),
            2,
        )

        t_res1 = font_stor.render(f"Dina fyrtal:  {spelare_poang} st", True, GULD if vinst else VIT)
        t_res2 = font_stor.render(
            f"AI:ns fyrtal:  {bot_poang} st",
            True,
            (255, 120, 120) if (not vinst and not oavgjort) else VIT,
        )
        skarm.blit(t_res1, t_res1.get_rect(center=(slut_ruta.centerx, slut_ruta.top + 205)))
        skarm.blit(t_res2, t_res2.get_rect(center=(slut_ruta.centerx, slut_ruta.top + 255)))

        knapp_farg = KNAPP_HOVER if replay_knapp.collidepoint(mus_pos) else KNAPP_GRON
        pygame.draw.rect(skarm, knapp_farg, replay_knapp, border_radius=14)
        pygame.draw.rect(skarm, VIT, replay_knapp, width=2, border_radius=14)
        t_replay = font_stor.render("Spela igen", True, VIT)
        skarm.blit(t_replay, t_replay.get_rect(center=replay_knapp.center))

    # -------------------------------------------------
    # Toppknappar längst upp till höger (Starta om & Stäng av)

    omstart_farg = KNAPP_HOVER if starta_om_knapp.collidepoint(mus_pos) else KNAPP_GRON
    pygame.draw.rect(skarm, omstart_farg, starta_om_knapp, border_radius=10)
    pygame.draw.rect(skarm, VIT, starta_om_knapp, width=2, border_radius=10)
    t_omstart = font_liten.render("Starta om", True, VIT)
    skarm.blit(t_omstart, t_omstart.get_rect(center=starta_om_knapp.center))

    stang_farg = KNAPP_ROD_HOVER if stang_knapp.collidepoint(mus_pos) else KNAPP_ROD
    pygame.draw.rect(skarm, stang_farg, stang_knapp, border_radius=10)
    pygame.draw.rect(skarm, VIT, stang_knapp, width=2, border_radius=10)
    t_stang = font_liten.render("Stäng av", True, VIT)
    skarm.blit(t_stang, t_stang.get_rect(center=stang_knapp.center))

    pygame.display.flip()
    klocka.tick(60)

pygame.quit()