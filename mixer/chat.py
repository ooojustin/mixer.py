import inspect
import requests
import shlex
import asyncio
from enum import Enum

from .ws import MixerWS
from .objects import MixerChatMessage

class MixerChat:

    class ParamType(Enum):
        NUMBER = 0,
        POSITIVE_NUMBER = 1,
        MIXER_USER = 2

    class ChatCommands:

        def add(self, name, func, **kwargs):
            """Manually adds a new command, given a name a reference to the callable.

            Args:
                name (str): Name of the command.
                func (function): The function to link this command to.
            """

            if not inspect.iscoroutinefunction(func):
                return

            name = name.lower()
            sig = inspect.signature(func)
            params = sig.parameters
            command = {
                "function": func,
                "signature": sig,
                "description": func.__doc__, # command docstring (should be a brief description)
                "params": list(params.keys())[1:], # list of parameter names
                "param_count": len(params) - 1, # ignore data parameter (required)
                "roles": kwargs.pop("roles", []), # list of roles permitted to use this command
                "aliases": kwargs.pop("aliases", []) + [name] # list of shortcuts to this, basically
            }

            existing = self.get(name, command["param_count"])
            if isinstance(existing, dict):
                # this command name already exists with this parameter count
                # it cant be overloaded unless we override the old one
                return

            if name in self.commands:
                self.commands[name].append(command)
            else:
                self.commands[name] = [command]

        def get(self, name, param_count = None):
            """Gets a chat command from the name and number of parameters.

            Args:
                name (str): The name of the command.
                param_count (int): The number of parameters expected.
            """

            # get a list of overloaded commands
            command_list = self.commands.get(name, [])

            # make sure the command actually exists
            if len(command_list) == 0:

                # resolve command aliasing
                for commands in self.commands.values():
                    for command in commands:
                        if name in command["aliases"]:
                            command_list.append(command)

                # if we didn't find any aliases, return
                if len(command_list) == 0:
                    return None

            # if parma_count isnt specified, return the first defined func
            if param_count is None:
                return command_list[0]

            # look for a definition with a matching parameter count
            for command in command_list:
                if command["param_count"] == param_count:
                    return command

            # return false because the command is defined but no matching parameter count
            return False

        def help(self, name, param_count = None):
            """Gets a description of a specific command.

            Args:
                name (str): The name of the command.
                param_count (int): The number of parameters expected.

            Returns:
                str: A description/documentation of a chat command.
            """

            command = self.get(name, param_count)

            if command is False:
                return "failed to find '{}' command with {} parameters.".format(name, param_count)
            elif command is None:
                return "failed to find '{}' command.".format(name)
            elif command["description"] is None:
                return "command '{}' with {} parameters is undocumented.".format(name, param_count)

            # list parameters
            if command["param_count"] > 0:
                params = ", ".join(command["params"])
                str = "{} ({}) -> {}".format(name, params, command["description"])
            else:
                str = "{} -> {}".format(name, command["description"])

            # show aliases to this command
            aliases = command["aliases"].copy()
            aliases.remove(name)
            if len(aliases) > 0:
                aliases = ", ".join(aliases)
                str += " (aliases: {})".format(aliases)

            return str

        async def trigger(self, command, message, params):
            response = await command["function"](message, *params)
            if response is not None:
                response = "@{} {}".format(message.username, response)
                await self.chat.send_message(response)

        async def handle(self, message):
            """Handle/parse a chat message as a command.

            Args:
                message (MixerChatMessage): A chat message wrapper.

            Returns:
                bool: Indicates if the message was handled as a command.
            """

            # command prefix check
            pl = len(self.prefix)
            if message.text[:pl] != self.prefix:
                return False

            # handle it as a command
            try:
                parsed = shlex.split(message.text) # split string by whitespace and account for quotes
                name = parsed[0][pl:].lower() # the name of the command -> 0th item with command prefix removed
                parameters = parsed[1:] # remove first parsed item, because its the command name
            except:
                await self.chat.send_message("an error occurred while parsing that command.")
                return True

            # make sure the command exists
            command = self.get(name, len(parameters))
            if command is None:
                await self.chat.send_message("unrecognized command '{}'.".format(name))
                return True
            elif command is False:
                await self.chat.send_message("invalid parameter count for command '{}'.".format(name))
                return True

            # if we have "roles", verify the user has permission to use command
            if len(command["roles"]) > 0:
                permitted = False
                for role in command["roles"]:
                    if message.has_role(role):
                        permitted = True
                        break
                if not permitted:
                    await self.chat.send_message("@{} you are not permitted to use this command.".format(message.username))
                    return True


            # handle parameter type annotations
            ParamType = self.chat.ParamType
            param_names = command["params"]
            param_objects = command["signature"].parameters
            for i in range(len(parameters)):
                param_object = param_objects[param_names[i]]
                if param_object.annotation == ParamType.NUMBER or param_object.annotation == ParamType.POSITIVE_NUMBER:
                    try:
                        parameters[i] = float(parameters[i])
                    except:
                        await self.chat.send_message("the '{}' parameter must be numeric.".format(param_names[i]))
                        return True
                    if param_object.annotation == ParamType.POSITIVE_NUMBER and parameters[i] <= 0:
                        await self.chat.send_message("the '{}' parameter must be a positive number.".format(param_names[i]))
                        return True
                elif param_object.annotation == ParamType.MIXER_USER:
                    if parameters[i][:1] != "@":
                        await self.chat.send_message("the '{}' parameter must be a tagged user.".format(param_names[i]))
                        return True
                    try:
                        channel = await self.chat.api.get_channel(parameters[i][1:])
                        parameters[i] = channel.user
                    except:
                        await self.chat.send_message("the '{}' parameter must be a tagged user.".format(param_names[i]))
                        return True

            # NOTE:
            # the asyncio.ensure_future function is used rather than a standard await
            # since the executed command may contain async sleeping,
            # awaiting the call may freeze handling of incoming messages
            # https://docs.python.org/3/library/asyncio-future.html#asyncio.ensure_future
            coro = self.trigger(command, message, parameters)
            task = asyncio.ensure_future(coro)

            return True

        def __init__(self, chat, prefix):

            self.chat = chat
            self.prefix = prefix
            self.commands = dict()

            # initialize default commands
            for name, methods in DEFAULT_COMMANDS.items():
                for method in methods:
                    self.add(name, method)

    # used to uniquely identify 'method' packets
    packet_id = 0

    # used to store references to functions (see __call__ and call_func)
    funcs = dict()
    callbacks = dict()

    # map events to functions
    event_map = {
        # ChatMessage -> handle_message (handled manually)
        "WelcomeEvent": "welcomed",
        "UserJoin": "user_joined",
        "UserLeave": "user_left",
        "PollStart": "poll_started",
        "PollEnd": "poll_end",
        "DeleteMessage": "message_deleted",
        "PurgeMessage": "messages_purged",
        "ClearMessages": "messages_cleared",
        "UserUpdate": "user_updated",
        "UserTimeout": "user_timed_out",
        "SkillAttribution": "handle_skill",
        "DeleteSkillAttribution": "skill_cancelled"
    }

    @classmethod
    async def create(cls, api, username_or_id, command_prefix = "!"):

        self = MixerChat()
        self.api = api
        self.channel = await self.api.get_channel(username_or_id)
        self.commands = self.ChatCommands(self, command_prefix)

        return self

    def __call__(self, method):
        if inspect.iscoroutinefunction(method):
            self.funcs[method.__name__] = method

    async def call_func(self, name, *args):

        # make sure the function exists
        # these are added via __call__ (@instance_name decorator)
        if not name in self.funcs: return

        # get a reference to the function
        func = self.funcs[name]

        # call the function
        await func(*args)

    async def send_method_packet(self, method, *args):
        """Sends a 'method' type packet to the Mixer chat websocket.

        Args:
            method (str): The method name.
            *args: List of arguments to pass to the server for this method.

        Returns:
            int: Unique packet identifier, used to register a callback.
        """
        packet = {
            "type": "method",
            "method": method,
            "arguments": list(args),
            "id": self.packet_id
        }
        await self.websocket.send_packet(packet)
        self.packet_id += 1
        return packet["id"]

    def register_method_callback(self, id, callback):
        """Creates a callback to handle replies to a method packet.

        Args:
            id (int): Unique packet ID returned by send_method_packet.
            callback (function): Callable to trigger when reply packet is received.
        """
        if inspect.iscoroutinefunction(callback):
            if not id in self.callbacks:
                self.callbacks[id] = callback

    async def start(self, oauth):
        """Initializes a websocket connection and starts handling commands.

        Args:
            oauth (MixerOAuth): Wrapper for access/refresh tokens.
        """

        url = "{}/chats/{}".format(self.api.API_URL, self.channel.id)
        response = requests.get(url, headers = oauth.header)
        chat_info = response.json() # https://pastebin.com/Z3RyUgBh

        # authentication callback (executed when w received reply for 'auth' method)
        async def auth_callback(data):
            if data["authenticated"]:
                await self.call_func("on_ready", oauth.username, oauth.user_id)

        # send auth packet upon connection and register auth_callback
        async def connected_callback():
            auth_packet_id = await self.send_method_packet("auth", self.channel.id, oauth.user_id, chat_info["authkey"])
            self.register_method_callback(auth_packet_id, auth_callback)

        # establish websocket connection and receive welcome packet
        self.websocket = MixerWS(chat_info["endpoints"][0])
        self.websocket.on_connected = connected_callback
        await self.websocket.connect()

        # infinite loop to handle future packets from server
        while True:

            # receive a packet from the server
            packet = await self.websocket.receive_packet()

            # handle 'event' packets from server
            if packet["type"] == "event":

                # custom handling for chat messages (commands and stuff)
                if packet["event"] == "ChatMessage":
                    message = MixerChatMessage(packet["data"])
                    message.chat = self
                    message.api = self.api
                    message.handled = await self.commands.handle(message)
                    await self.call_func("handle_message", message)
                    continue

                # call corresponding event handler
                if packet["event"] in self.event_map:
                    func_name = self.event_map[packet["event"]]
                    await self.call_func(func_name, packet["data"])

                continue

            # handle 'reply' packets from server
            if packet["type"] == "reply":

                # see if there's a reply callback for this packet
                callback = self.callbacks.pop(packet["id"], None)
                if callback is not None:

                    # invoke callback with data from reply packet
                    response = packet.get("data", packet)
                    await callback(response)

                continue

    async def send_message(self, message, user = None):
        """Send a message in the chat.

        Args:
            message (str): Message to send.
            user (str): Username to whisper to. Optional, will be sent in all chat if not provided.
        """
        if user is None:
            await self.send_method_packet("msg", message)
        else:
            await self.send_method_packet("whisper", user, message)

    def command(self, **kwargs):
        return lambda f: self.commands.add(f.__name__, f, **kwargs)

async def help_0(message):
    """Displays a list of commands that can be used in the chat."""

    chat = message.chat
    command_count = 0
    command_names = list()

    # build a list of command names/descriptions with params
    for name, commands in chat.commands.commands.items():

        variants = list()

        for command in commands:

            if command["description"] is None:
                continue

            command_count += 1
            variants.append(str(command["param_count"]))

        if len(variants) == 0:
            continue
        elif len(variants) == 1:
            command_names.append(name)
        else:
            param_counts = ", ".join(variants)
            command_names.append("{} ({})".format(name, param_counts))

    # delete original >help message
    await message.delete()

    # formate response messages
    message1 = "There are a total of {} commands: {}."
    message2 = "To see information about a specific command, use '{}help command_name'."
    message1 = message1.format(command_count, ", ".join(command_names))
    message2 = message2.format(chat.commands.prefix)

    # whisper formatted response messages to used
    await chat.send_message(message1, message.username)
    await asyncio.sleep(.5) # wait before sending second message :p
    await chat.send_message(message2, message.username)

async def help_1(message, name):
    """Provides a description of a specific command."""
    name = name.lower()
    return message.chat.commands.help(name)

async def help_2(message, name, parameter_count_or_name):
    """Provides a description of a command given a parameter count or parameter name."""
    chat = message.chat

    # if the second parameter is an int, assume they're specifying parameter count
    name = name.lower()
    try:
        return chat.commands.help(name, int(parameter_count_or_name))
    except ValueError: pass

    # fallback to 'help' command if it doesnt exist
    if not name in chat.commands.commands:
        return chat.commands.help(name)

    # try to find a definition of the specified command with the given parameter name
    for command in chat.commands.commands[name]:
        if parameter_count_or_name in command["params"]:
            return chat.commands.help(name, command["param_count"])
    return "no variation of command '{}' has parameter named '{}'.".format(name, parameter_count_or_name)

DEFAULT_COMMANDS = {
    "help": [help_0, help_1, help_2]
}
