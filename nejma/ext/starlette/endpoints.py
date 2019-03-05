import asyncio
import functools

from starlette import status
from starlette.endpoints import WebSocketEndpoint as BaseWebSocketEndpoint
from starlette.websockets import WebSocket

from nejma.layers import Channel, channel_layer


class WebSocketEndpoint(BaseWebSocketEndpoint):
    encoding = "json"

    async def __call__(self, receive, send):
        websocket = WebSocket(self.scope, receive=receive, send=send)
        await self.on_connect(websocket)

        self.channel_layer = channel_layer

        self.channel = Channel()

        loop = asyncio.get_event_loop()

        callables = [
            functools.partial(websocket.receive),
            functools.partial(self.channel.receive),
        ]
        tasks = [asyncio.ensure_future(task()) for task in callables]
        try:
            cont = True
            while cont:
                await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                for i, task in enumerate(tasks):
                    if task.done():
                        message = task.result()
                        if message["type"] == "websocket.receive":
                            data = await self.decode(websocket, message)
                            await self.on_receive(websocket, data)
                        elif message["type"] == "websocket.disconnect":
                            close_code = int(
                                message.get("code", status.WS_1000_NORMAL_CLOSURE)
                            )
                            cont = False
                            break
                        else:
                            await self.dispatch(websocket, message)
                        tasks[i] = asyncio.ensure_future(callables[i]())
        except Exception as exc:
            close_code = status.WS_1011_INTERNAL_ERROR
            raise exc from None
        finally:
            for task in tasks:
                task.cancel()
                try:
                    await task
                except:
                    pass
            await self.on_disconnect(websocket, close_code)

    async def dispatch(self, websocket, message):
        assert "type" in message
        handler = getattr(self, message["type"].replace(".", "_"), None)
        if not handler:
            raise ValueError(f"'{message['type']}' is not defined")
        await handler(websocket, message)

    async def on_connect(self, websocket, **kwargs):
        await super().on_connect(websocket, **kwargs)

    async def on_disconnect(self, websocket, close_code):
        self.channel_layer.remove_channel(self.channel)
