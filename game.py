from random import randint, sample

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
		self.leg_bets     = reset_leg_bets()
		self.rolled_dice  = reset_dice_status()
		self.camel_locations
		self.leg_num      = 0
		self.leg_turn_num = 0

	def current_player(self):
		return self.player_list[(self.leg_num + self.leg_turn_num) % len(self.player_list)]

	def end_leg(self):
		for player in self.player_list():
			player.do_accounting()
		self.leg_bets     = reset_leg_bets()
		self.rolled_dice  = reset_dice_status()
		self.leg_num     += 1
		self.leg_turn_num = 0

	def roll_dice(self)
		self.current_player().give_money(1)
		not_rolled_yet = [camel for camel in camel_list if not self.rolled_dice[camel]]
		moving_camel   = sample(not_rolled_yet, 1)
		num_spaces     = randint(1, 3)
		self.rolled_dice[moving_camel] = num_spaces
		self.track.move(moving_camel, num_spaces)

class Track:
	def __init__(self):
		self.track = [Space(i) for i in range(20)]

	def add_trap(self, player, place, effect):
		self.track[place].oasis = effect
		self.track[place].oasis_player = oasis_player

	def move(self, moving_camel, num_spaces):
		#don't even optimise this part lmao 20 loops who cares
		for space in self.track:
			if moving_camel in space.camels:
				camel_index = space.camels.index(moving_camel)
				moving_camels = space.camels[moving_camels:]
				space.camels
				break
		spac


class Space:
	def __init__(self, num):
		self.num = num
		self.camels = []
		self.oasis = 0
		self.oasis_player = None