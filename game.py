from random import randint, sample
import copy

camel_list = ['white', 'blue', 'yellow', 'green', 'orange']

def reset_leg_bets():
	return {camel:[5,3,1] for camel in camel_list}

def reset_dice_status():
	return {camel:0 for camel in camel_list}

class Game:
	def __init__(self, player_list):
		self.player_list  = player_list
		self.winner_bets  = []
		self.loser_bets   = []
		self.track        = Track()
        self.leg_bets_INIT = {colour: [
            (2,1,-1), (3,1,-1), (5,2,-1)
        ] for colour in camel_list}
		self.leg_bets     = copy.deepcopy(self.leg_bets_INIT)
		self.rolled_dice  = reset_dice_status()
		self.camel_locations
		self.leg_num      = 0
		self.leg_turn_num = 0

	def current_player(self):
		return self.player_list[(self.leg_num + self.leg_turn_num) % len(self.player_list)]

	def end_leg(self):
		for player in self.player_list():
			player.do_accounting()
		self.leg_bets     = copy.deepcopy(self.leg_bets_INIT)
		self.rolled_dice  = reset_dice_status()
		self.leg_num     += 1
		self.leg_turn_num = 0

	def roll_dice(self)
		not_rolled_yet = [camel for camel in camel_list if not self.rolled_dice[camel]]
		moving_camel   = sample(not_rolled_yet, 1)
		num_spaces     = randint(1, 3)
		self.rolled_dice[moving_camel] = num_spaces
		self.track.move(moving_camel, num_spaces)

    def is_leg_bet_available(self):
        if len(self.leg_bets[colour]) = 0:
            return False
        else:
            return True

    def make_leg_bet(self, str colour):
        # assumes that you've already run 'is_leg_bet_available'
        self.leg_bets[colour].pop()

    def place_end_long(self, str player_name, str colour):
        self.winner_bets.append((player_name, colour))

    def place_end_short(self):
        self.loser_bets.append((player_name, colour))

class Track:
	def __init__(self):
		self.track = [Space(i) for i in range(20)]

	def add_trap(self, player, place, effect):
		self.track[place].oasis = effect
		self.track[place].oasis_player = oasis_player

	def move(self, moving_camel, num_spaces):
		#returns winning camel if game finished

		#don't even optimise this part lmao 20 loops who cares
		for space in self.track:
			if moving_camel in space.camels:
				camel_index = space.camels.index(moving_camel)
				# extracting camels and every camel on top
				moving_camels = space.camels[camel_index:]
				break
		# take out these camels from this space
		space.camels = space.camels[:camel_index]
		# calculate target space
		target_space_num = space.num + num_spaces

		if target_space_num >= 20:
			return moving_camels[-1]
		else:
            self.track[target_space_num].camels.extend(moving_camels)
            if self.track[target_space_num].oasis = 1:
                self.move(moving_camel, 1)
            elif self.track[target_space_num].oasis = -1:
                self.move(moving_camel, -1)


class Space:
	def __init__(self, num):
		self.num = num
		self.camels = []
		self.oasis = 0
		self.oasis_player = None