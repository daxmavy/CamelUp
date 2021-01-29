# CamelUp
WebApp to simulate CamelUp - written in Python/ReactJS.

## Dependencies
Requires `python3.8` and `NodeJS'.
```
sudo apt install python3.8 python3.8-venv
npm install --global yarn
yarn global add pm2
```
Also make sure that `export PATH="$PATH:$(yarn global bin)"` is in the `.bashrc` so that pm2 can be found by bash.

## Usage (Hosting)
Clone the directory 
`git clone https://github.com/Chuangy/MockTrading`

Create a `.env` file in `frontend/` to initialise the environmental variables for the ReactJS application. It should contain the following information:
```
REACT_APP_PUBLIC_HOST={your_public_ip_address}
REACT_APP_PRIVATE_HOST={your_private_ip_address}
REACT_APP_PORT="8887"
```

Proceed to build the frontend ReactJS application.
```
cd frontend/
yarn install
yarn build
```
From the root directory, run the following:
```
pm2 start mocktrading.config.js --env production
```
The logs can be retrieved using
```
pm2 logs
```
and resources can be monitored using 
```
pm2 monit
```

## Features
- Lobby room before starting game
