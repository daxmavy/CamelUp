#!/usr/bin/env python3.8

import asyncio
import json
import random
import time
import traceback
import websockets

import util.helpers as util


class Server:
    def __init__(self):
        util.print_core('Initialising...')
        self._connected_users = set()
        self._lobby = Lobby()               # Lobby of the rooms
        self._q = asyncio.Queue()

    async def client_handler(self, websocket, path):
        self._connected_users.add(websocket)
        print('-' * 60)
        util.print_core('A client has connected!')
        print('-' * 60)
        try:
            async for _ in websocket:
                message = await websocket.recv()
                d = json.loads(message)
                await self._q.put((d, websocket))

        except Exception:
            traceback.print_exc()
            util.print_core('Client unexpectedly disconnected!')

    async def consume(self, q: asyncio.Queue):
        while True:
            msg, ws = await self._q.get()
            if isinstance(msg, dict):
                await self.update_and_send_response(msg, ws)

            elif isinstance(msg, list):
                for m in msg:
                    await self.update_and_send_response(m, ws)

            else:
                util.print_core('Unknown message datatype')

    async def update_and_send_response(self, msg, ws):
        if isinstance(msg, dict):
            msg_json = msg
            msg = json.dumps(msg)
        elif isinstance(msg, str):
            msg_json = json.loads(msg)

        if 'type' not in msg_json.keys():
            print('Uncaught message! No type!')
            return
        else:
            msg_type = msg_json['type']

        response = []
        # Handle messages here
        if msg_type == 'NewRoom':
            if self._lobby.new_room(msg_json['data']['name']):
                response = [
                    {
                        'type': 'Info',
                        'status': 'New room successfully created'
                    },
                    {
                        'type': 'RoomUpdate',
                        'data': self._lobby.get_rooms()
                    }
                ]
            else:
                response = {
                    'type': 'Info',
                    'status': 'Failed to create new room - duplicate name'
                }
        elif msg_type == 'DeleteRoom':
            if self._lobby.delete_room(msg_json['data']['name']):
                response = [
                    {
                        'type': 'Info',
                        'status': 'Deleted room'
                    },
                    {
                        'type': 'RoomUpdate',
                        'data': self._lobby.get_rooms()
                    }
                ]
            else:
                response = {
                    'type': 'Info',
                    'status': 'Failed to delete room - does not exist.'
                }
        elif msg_type == 'NewPlayer':
            name = msg_json['data']['name']
            password = msg_json['data']['password']
            c = await self._lobby.new_player(name, password, ws)
            if c:
                response = [
                    {
                        'type': 'Info',
                        'status': f'{name} successfully joined game'
                    },
                    {
                        'type': 'PlayerUpdate',
                        'data': self._lobby.get_players()
                    }
                ]
            else:
                response = {
                    'type': 'Info',
                    'status': 'Failed to login - incorrect password'
                }
        elif msg_type == 'DeletePlayer':
            name = msg_json['data']['name']
            if self._lobby.delete_player(name):
                response = [
                    {
                        'type': 'Info',
                        'status': f'Deleted player {name}'
                    },
                    {
                        'type': 'PlayerUpdate',
                        'data': self._lobby.get_players()
                    }
                ]
            else:
                response = {
                    'type': 'Info',
                    'status': 'Failed to delete player - does not exist.'
                }

        elif msg_type == 'JoinRoom':
            player = msg_json['data']['player']
            room = msg_json['data']['room']
            c1 = await self._lobby.get_room(room).join(self._lobby.get_player(player))
            if (c1):
                await self._lobby.get_player(player).join_room(room)
                response = {
                    'type': 'Info',
                    'status': f'{player} has joined {room}'
                }
            else:
                response = {
                    'type': 'Info',
                    'status': f'{player} failed to join {room}'
                }
        elif msg_type == 'LeaveRoom':
            player = msg_json['data']['player']
            room = msg_json['data']['room']
            if (
                self._lobby.get_player(player).leave_room(room) and
                self._lobby.get_room(room).leave(player)
            ):
                response = {
                    'type': 'Info',
                    'status': f'{player} has left {room}'
                }
            else:
                response = {
                    'type': 'Info',
                    'status': f'{player} failed to leave {room}'
                }
        elif msg_type == 'StartGame':
            room = self._lobby.get_room(msg_json['data']['room'])
            await room.start_game()

        await self.broadcast(response)

    async def broadcast(self, msg):
        if isinstance(msg, list):
            for m in msg:
                await self.broadcast(m)
        elif isinstance(msg, str):
            await self.broadcast(msg)
        elif isinstance(msg, dict):
            for ws in self._connected_users.copy():
                try:
                    await ws.send(json.dumps(msg))
                except:
                    if ws in self._connected_users:
                        self._connected_users.discard(ws)
                        # util.print_core('Could not send, removing ws')
                    else:
                        pass

    async def run(self, port='8887', host='localhost'):
        util.print_core(f'Starting server on port {port}')
        await websockets.server.serve(self.client_handler, host, port)

        consumer = asyncio.create_task(self.consume(self._q))
        await asyncio.gather(consumer)


class Lobby:
    def __init__(self):
        self._rooms = {}
        self._players = {}

    def new_room(self, name):
        if name in self._rooms.keys():
            util.print_core('Room already exists')
            return 0
        else:
            util.print_core('Making a new room')
            self._rooms[name] = Room(name)
            return 1

    def delete_room(self, name):
        if name in self._rooms.keys():
            del self._rooms[name]
            return 1
        else:
            return 0

    async def new_player(self, player_name, password, ws):
        if player_name in self._players.keys():
            util.print_core('Player already exists - attempting login')
            if self._players[player_name]._password == password:
                self._players[player_name].update_ws(ws)
                await self._players[player_name].send_message({
                    'type': 'PlayerDetails',
                    'data': player_name
                })
                util.print_core('Login success!')
                return 1
            else:
                return 0
        else:
            util.print_core(f'Creating player: {player_name}')
            self._players[player_name] = Player(player_name, password, ws)
            await self._players[player_name].send_message(
                {
                    'type': 'PlayerDetails',
                    'data': player_name
                }
            )
            util.print_core('New player creation success!')
            return 1

    def delete_player(self, player_name):
        if player_name in self._players.keys():
            del self._players[player_name]
            return 1
        else:
            return 0

    def get_rooms(self):
        return sorted(list(self._rooms.keys()))

    def get_players(self):
        return sorted(list(self._players.keys()))

    def get_player(self, player):
        return self._players[player]

    def get_room(self, room):
        return self._rooms[room]

    def __getitem__(self, key):
        if isinstance(key, str):
            return self._players[key]


class Player:
    def __init__(self, str name, object Game ):
        self.game = Game
        self.name = name
        self.password = 'GME'
        self.money = 6
        self.bets_available = {colour: True for colour in ['white', 'blue', 'yellow', 'green', 'orange']}
        self.tile_token_available = True
        self.leg_bets_placed = []

    def __init__(self, name, password, ws):
        self._player_name = name
        self._password = password
        self._ws = ws
        self._player_id = util.hash_string(name)
        self._rooms = set()

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


    

    

    async def join_room(self, room_name):
        if room_name in self._rooms:
            util.print_core(f'{self._player_name} is already in {room_name}')
            return 0
        else:
            self._rooms.add(room_name)

            await self.send_message({
                'type': 'CurrentRoom',
                'data': {
                    'name': room_name
                }
            })
            util.print_core(f'{self._player_name} has joined {room_name}')
            return 1

    def update_ws(self, new_ws):
        self._ws = new_ws

    def leave_room(self, room_name):
        if room_name in self._rooms:
            self._rooms.remove(room_name)
            util.print_core(f'{self._player_name} has left {room_name}')
            return 1
        return 0

    async def send_message(self, msg):
        try:
            if isinstance(msg, str):
                await self._ws.send(msg)
            elif isinstance(msg, list):
                for m in msg:
                    await self._ws.send(m)
            else:
                await self._ws.send(json.dumps(msg))
        except:
            util.print_core('Could not send!')


class Room:
    def __init__(self, name):
        self._name = name                   # Name of the room
        self._status = 'waiting'
        self._players = {}                  # Members of the room

    async def tell_room(self, msg):
        for _, player in self._players.items():
            try:
                await player.send_message(json.dumps(msg))
            except:
                util.print_core('Could not send!')

    async def join(self, player: Player):
        person_name = player._player_name
        if self._status != 'waiting' and person_name not in self._players.keys():
            util.print_core(
                f'{person_name} could not join {self._name} (already started)')
            return 0
        elif self._status != 'waiting' and person_name in self._players.keys():
            util.print_core(
                f'{person_name} is rejoining in {self._name} (started)')
            await player.send_message({
                'type': 'RoomPlayersUpdate',
                'data': {
                    'room': self._name,
                    'players': list(self._players.keys())
                }
            })
            await player.send_message({
                'type': 'GameStart',
                'data': {
                }
            })
            return 1
        else:
            self._players[person_name] = player
            util.print_core(f'{person_name} has joined {self._name}')
            await self.tell_room({
                'type': 'RoomPlayersUpdate',
                'data': {
                    'room': self._name,
                    'players': list(self._players.keys())
                }
            })
            return 1

    def leave(self, person_name):
        if self._status == 'waiting' and person_name in self._players.keys():
            del self._players[person_name]
            util.print_core(f'{person_name} has left {self._name}')
            return 1
        elif self._status == 'started' and person_name in self._players.keys():
            util.print_core(
                f'The game has already started but {person_name} has left {self._name}')
            return 1
        else:
            return 0

    async def start_game(self):
        if self._status == 'started':
            util.print_core(f'The game in {self._name} has already started!')
            await self.tell_room({
                'type': 'Info', 'status': f'The game in room {self._name} has already started'
            })
            return

        util.print_core(f'The game in {self._name} is starting!')
        await self.tell_room({
            'type': 'Info', 'status': f'The game in room {self._name} has begun'
        })

    def __hash__(self):
        return util.hash_string(self._name)

    def __eq__(self, r):
        if self.__hash__() == r.__hash__():
            return True
        else:
            return False

    def __ne__(self, r):
        return (not self.__eq__(r))


async def main(port='8887', host='localhost'):
    server = Server()
    await server.run(port=port, host=host)
