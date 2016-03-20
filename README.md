# Wildebeest Game App w/ Flask Server
A simple web application to play the game of Wildebeest.

## Server
Install python module Flask:
```sh
pip install Flask
```
Server defaults to http://127.0.0.1:5000/. Modify IP address with app.run():
```python
app.run(host="ip_address_here", port=5000)
```

---

## Run
Execute the server:
```sh
python server.py
```

---

## Release History
v1.1: Updated game piece and board graphics. Note: No visual indicators for king with jet pack, empress, or charged golf cart.

v1.0: Playable game of Wildebeest against a low-level computer.

---
## Feature Plans
* Neatly present game rules.
* Show move history and/or better indicate AI's move.
* Drag-and-drop to move pieces.
* Multiplayer support with chat.
* Improved AI.