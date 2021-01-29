import React from "react";
import { Form, Input, Select, Radio, InputNumber } from "antd";

import Loader from "react-loader-spinner";

import "antd/dist/antd.css";
import "react-loader-spinner/dist/loader/css/react-spinner-loader.css";

import "./Game.css";

export class Game extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      last_render_time: null,
      ws: null,
      current_room: null,
      current_players: [],
      rooms: [],
      players: [],
      player_name: "no_name",
      status: "none",
    };
  }

  componentDidMount() {
    this.connect();
    setInterval(
      () =>
        this.setState({
          last_render_time: Date.now(),
        }),
      200
    );
  }

  connect = () => {
    console.log(process.env);
    const public_host = process.env.REACT_APP_PUBLIC_HOST
      ? process.env.REACT_APP_PUBLIC_HOST
      : "localhost";
    const port = process.env.REACT_APP_PORT
      ? process.env.REACT_APP_PORT
      : "8887";
    const ws_uri = `ws://${public_host}:${port}`;
    console.log(`Attempting to connect to ${ws_uri}`);
    let ws = new WebSocket(ws_uri);
    ws.onopen = () => {
      console.log("Conncted to the websocket!");
      this.setState({ ws: ws });

      ws.send("");
      ws.send(JSON.stringify({ type: "NewRoom", data: { name: "TestRoom" } }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "Info":
          console.log(message.status);
          break;
        case "PlayerDetails":
          this.setState({
            player_name: message.data,
          });
          break;
        case "PlayerUpdate":
          console.log("Received player update!");
          this.setState({
            players: message.data,
          });
          break;
        case "RoomUpdate":
          console.log("Received room update!");
          this.setState({
            rooms: message.data,
          });
          break;
        case "RoomPlayersUpdate":
          console.log("Received update of players in room!");
          if (this.state.current_room === message.data.room) {
            this.setState({
              current_players: message.data.players,
            });
          }
          break;
        case "GameStart":
          console.log("Received cards from the dealer!");
          this.setState({
            cards: message.data.cards,
            status: "started",
          });
          break;
        default:
          console.log(`Unknown message: ${JSON.stringify(message)}`);
      }
    };
  };

  handleNewRoom(r) {
    console.log(`Creating new room ${r}`);
    this.state.ws.send("");
    this.state.ws.send(JSON.stringify({ type: "NewRoom", data: { name: r } }));
  }

  handleJoinRoom(r) {
    if (this.state.player_name === "no_name") {
      console.log("Please enter name first...");
    } else {
      this.setState({
        current_room: r,
      });
      this.state.ws.send("");
      this.state.ws.send(
        JSON.stringify({
          type: "JoinRoom",
          data: { room: r, player: this.state.player_name },
        })
      );
    }
  }

  handleLeaveRoom(r) {
    this.setState({
      current_room: null,
      current_players: [],
      cards: [],
      revealed_cards: {},
      status: "none",
    });
    this.state.ws.send("");
    this.state.ws.send(
      JSON.stringify({
        type: "LeaveRoom",
        data: { room: r, player: this.state.player_name },
      })
    );
  }

  handleStart() {
    this.state.ws.send("");
    this.state.ws.send(
      JSON.stringify({
        type: "StartGame",
        data: { room: this.state.current_room },
      })
    );
  }

  shouldComponentUpdate(nextProps, nextState) {
    if (JSON.stringify(nextProps) !== JSON.stringify(this.props)) {
      return true;
    } else if (JSON.stringify(nextState) !== JSON.stringify(this.state)) {
      return true;
    }
    return false;
  }

  render() {
    return (
      <div className="game_wrapper">
        <div className="left_bar">
          <Player player_name={this.state.player_name} ws={this.state.ws} />
          <Lobby players={this.state.players} />
          <AvailableRooms
            current_room={this.state.current_room}
            rooms={this.state.rooms}
            onJoinRoom={this.handleJoinRoom.bind(this)}
            onLeaveRoom={this.handleLeaveRoom.bind(this)}
            onNewRoom={this.handleNewRoom.bind(this)}
          />
        </div>
        <div className="right_bar">
          <Room
            room={this.state.current_room}
            player_name={this.state.player_name}
            status={this.state.status}
            players={this.state.current_players}
            onStart={this.handleStart.bind(this)}
          />
        </div>
        {this.state.status === "none" ? (
          <div className="loading_wrapper">
            <div>
              <h1>Waiting for game start...</h1>
            </div>
            <Loader
              type="BallTriangle"
              color="#1E1E1E"
              height={200}
              width={200}
            />
            <div>
              <h2>First enter your name if you haven't already done so...</h2>
              <h3>Then join a room....</h3>
            </div>
          </div>
        ) : (
          <>
            <div className="tool_bar">Toolbar</div>
            <div className="main_canvas">Main Canvas</div>
          </>
        )}
      </div>
    );
  }
}

class Player extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      player_name: "Username",
      password: "Password",
    };
  }

  handleNameChange(e) {
    this.setState({ player_name: e.target.value });
  }

  handlePasswordChange(e) {
    this.setState({ password: e.target.value });
  }

  handleSubmit(e) {
    this.props.ws.send("");
    this.props.ws.send(
      JSON.stringify({
        type: "NewPlayer",
        data: {
          name: this.state.player_name,
          password: this.state.password,
        },
      })
    );
    e.preventDefault();
  }

  render() {
    return (
      <div className="player">
        <div className="label">Player details</div>
        <div className="player_name_changer">
          {this.props.player_name === "no_name" ? (
            <form onSubmit={this.handleSubmit.bind(this)}>
              <input
                value={this.state.player_name}
                onChange={this.handleNameChange.bind(this)}
              />
              <input
                value={this.state.password}
                onChange={this.handlePasswordChange.bind(this)}
              />
              <input
                type="submit"
                style={{ position: "absolute", left: "-9999px" }}
              />
            </form>
          ) : (
            <div className="player_name text">{this.props.player_name}</div>
          )}
        </div>
      </div>
    );
  }
}

class Room extends React.Component {
  constructor(props) {
    super(props);
  }

  shouldComponentUpdate(nextProps) {
    if (JSON.stringify(nextProps) !== JSON.stringify(this.props)) {
      return true;
    }
    return false;
  }

  render() {
    const players = this.props.players ? this.props.players : [];
    return (
      <div className="curent_room">
        <div className="label">
          {this.props.room ? this.props.room : "Not in a room"}
        </div>
        <div className="players">
          {players
            .reduce((acc, element) => {
              if (element === this.props.player_name) {
                return [element, ...acc];
              }
              return [...acc, element];
            }, [])
            .map((p) => {
              return (
                <div className="player_info" key={p}>
                  {p === this.props.player_name ? (
                    <div className="player_name yourself text row" key="name">
                      {p}
                    </div>
                  ) : (
                    <div className="player_name text row" key="name">
                      {p}
                    </div>
                  )}
                </div>
              );
            })}
        </div>
        {this.props.room ? (
          this.props.status !== "started" ? (
            <div className="start_button" onClick={this.props.onStart}>
              Start Game
            </div>
          ) : (
            <div className="started" onClick={this.props.onStart}>
              Started
            </div>
          )
        ) : (
          ""
        )}
      </div>
    );
  }
}

class AvailableRooms extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      new_room_name: "",
    };
  }

  handleName(e) {
    this.setState({ new_room_name: e.target.value });
    e.target.value = "";
  }

  render() {
    const rooms = this.props.rooms;
    return (
      <div className="room">
        <div className="label">Available rooms</div>
        {rooms.map((r) => {
          return (
            <div className="row" key={r}>
              <div className="room_name text" key={r}>
                {r}
              </div>
              {this.props.current_room !== r ? (
                <div
                  className="button text"
                  onClick={this.props.onJoinRoom.bind(this, r)}
                >
                  Join
                </div>
              ) : (
                <div
                  className="button text"
                  onClick={this.props.onLeaveRoom.bind(this, r)}
                >
                  Leave
                </div>
              )}
            </div>
          );
        })}
        <div className="row" key="new_room">
          <Input
            className="room_name text"
            onChange={this.handleName.bind(this)}
          />
          <div
            className="button text"
            onClick={this.props.onNewRoom.bind(this, this.state.new_room_name)}
          >
            Create
          </div>
        </div>
      </div>
    );
  }
}

class Lobby extends React.Component {
  constructor(props) {
    super(props);
  }

  shouldComponentUpdate(nextProps) {
    if (JSON.stringify(nextProps) !== JSON.stringify(this.props)) {
      return true;
    }
    return false;
  }

  render() {
    const players = this.props.players;
    return (
      <div className="lobby">
        <div className="label">Players</div>
        {players.map((p) => {
          return (
            <div className="row" key={p}>
              <div className="player_name text" key={p}>
                {p}
              </div>
            </div>
          );
        })}
      </div>
    );
  }
}

export default Game;
