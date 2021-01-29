class Player:
    # to init: pass name (input from server) and main game (directions from Room object)
    def __init__(self, str name, object Game ):
        self.game = Game
        self.name = name
        self.password = 'GME'
        self.money = 6
        self.bets_available = {colour: True for colour in ['white', 'blue', 'yellow', 'green', 'orange']}
        self.tile_token_available = True
        self.leg_bets_placed = []

    # server input: which camel chosen
    def place_leg_bet(self, str colour):
        available = self.game.is_leg_bet_available(colour)
        if available:
            bet = self.game.make_leg_bet(colour)
            self.leg_bets_placed.append((colour, bet[0], bet[1], bet[2]))
        else:
            # fail and pass message
    
    def place_end_short(self, str colour):
        available = self.bets_available[colour]
        if available:
            self.game.place_end_short(self.name, colour)
            self.bets_available[colour] = False
        else:
            # fail and pass message
    
    def place_end_long(self, str colour):
        available = self.bets_available[colour]
        if available:
            self.game.place_end_long(self.name, colour)
            self.bets_available[colour] = False
        else:
            # fail and pass message

    def roll_dice(self):
        self.money = self.money + 1
        self.game.roll_dice()

    def place_oasis(self, tile_number):
        token_available = self.tile_token_available
        tile_available = self.game.tile_available(tile_number)
        if not token_available:
            # fail and say that the token has already been used
        elif not tile_available:
            # fail and say that the tile isn't aviailabe
        else:
            self.game.place_oasis()
            self.tile_token_available = False

    def place_desert(self, tile_number):
        token_available = self.tile_token_available
        tile_available = self.game.tile_available(tile_number)
        if not token_available:
            # fail and say that the token has already been used
        elif not tile_available:
            # fail and say that the tile isn't aviailabe
        else:
            self.game.place_desert()
            self.tile_token_available = False
    
    def do_accounting(self):
        ranking = self.game.get_camel_ranking()
        for bet in self.leg_bets_placed:
            bet_colour = bet[0]
            if bet_colour = ranking[0]:
                self.money = self.money + bet[1]
            elif bet_colour = ranking[1]:
                self.money = self.money + bet[2]
            else:
                self.money = self.money + bet[3]
                self.money = 0 if self.money < 0 # stopping it from going negative
        self.leg_bets_placed = []
        self.tile_token_available = True


            



    

    
        

    
        
            

        






