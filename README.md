# ⭐ Nejma ⭐


Inspired by `channels`, Nejma ⭐ allows you manage and send messages to groups of channels

Things you can build with `nejma`:
- chat
- notification
- handle users connected from multiple tabs)
- and more...


## Example

Take a look at this example [`nejma-chat`](https://github.com/taoufik07/nejma-chat), a simple chat application built using `nejma` and `starlette`.


## Installation

```shell
$ pip install nejma
```

## Getting started 

Here's an example of using `nejma` with websockets.

First import Channel and channel_layer from nejma

```python
from nejma import Channel, channel_layer
```

Create a channel on connect

```python
async def on_connect(self, websocket, **kwargs):
    await super().on_connect(websocket, **kwargs)

    self.channel = Channel(send=websocket.send)

```

Add groups, channels or send messages   

```python
async def on_receive(self, websocket, data):
    self.channel_layer.add(group, self.channel)

    await self.channel_layer.group_send(group, "Welcome !")
```

Finnaly, remove the channel once the connection is closed 

```python
async def on_disconnect(self, websocket, close_code):
    self.channel_layer.remove_channel(self.channel)
```


### Starlette
---

To use `nejma` with `starlette`, simply import the WebSocketEndpoint from nejma

```python
from nejma.ext.starlette import WebSocketEndpoint

@app.websocket_route("/ws")
class Chat(WebSocketEndpoint):
    encoding = "json"

    async def on_receive(self, websocket, data):
        room_id = data['room_id']
        message = data['message']
        username = data['username']

        if message.strip():
            group = f"group_{room_id}"

            self.channel_layer.add(group, self.channel)

            payload = {
                "username": username,
                "message": message,
                "room_id": room_id
            }
            await self.channel_layer.group_send(group, payload)
```

## Docs

The `ChannelLayer` class provided by `nejma` exposes the following methods :

`add(group, channel, send=None)`

Adds a channel to a giving group.

* send : method to send messages to a channel

```python
self.channel_layer.add(group, self.channel, send=websocket.send)
```

`async group_send(group, "Welcome !")`

Sends a message to a group of channels

```python
await self.channel_layer.group_send(group, "Welcome !")
```

`remove(group, channel)`

Removes a channel from a given group

```python
self.channel_layer.remove(group, self.channel)
```

`remove_channel(channel)`

Removes a channel from all the groups

```python
self.channel_layer.remove_channel(self.channel)
```

`flush()`

Reset all the groups

```python
self.channel_layer.flush()
```
