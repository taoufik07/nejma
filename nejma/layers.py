import time
import uuid
import re


class Channel:
    def __init__(self, name=None, send=None, expires=60):
        if name:
            assert self.validate_name(name), "Invalid channel name"
        self.name = name or str(uuid.uuid4())
        self.expires = expires
        self.created_at = time.time()
        self._send = send

    async def send(self, message):
        await self._send(message)

    def validate_name(self, name):
        if name.isidentifier():
            return True
        raise TypeError(
            "Channels names must be valid python identifier"
            + "only alphanumerics and underscores are accepted"
        )

    def is_expired(self):
        return self.expires + int(self.created_at) < time.time()


class ChannelLayer:
    def __init__(self, expires=36000, capacity=100):
        self.capacity = capacity
        self.expires = expires

        self.groups = {}

    def add(self, group_name, channel, send=None):
        assert self.validate_name(group_name), "Invalid group name"
        if isinstance(channel, (str, bytes)):
            channel = Channel(name=channel, send=send)

        self.groups.setdefault(group_name, {})
        # lookup
        self.groups[group_name][channel] = 1

    def remove(self, group_name, channel):
        if group_name in self.groups:
            if channel in self.groups[group_name]:
                del self.groups[group_name][channel]

    def flush(self):
        self.groups = {}

    async def group_send(self, group, payload):
        self.clean_expired()
        for channel in self.groups.get(group, {}):
            await channel.send(payload)

    def remove_channel(self, channel):
        for group in self.groups:
            if channel in self.groups[group]:
                del self.groups[group][channel]

    def validate_name(self, name):
        if name.isidentifier():
            return True
        raise TypeError(
            "Group names must be valid python identifier"
            + "only alphanumerics and underscores are accepted"
        )

    def clean_expired(self):
        for group in self.groups:
            # Can't change dict size during iteration
            for channel in list(self.groups.get(group, {})):
                if channel.is_expired():
                    del self.groups[group][channel]


channel_layer = ChannelLayer()
