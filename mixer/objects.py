# https://dev.mixer.com/rest/index.html#TimeStamped
class TimeStamped:

    def __datetime(self, name):
        str = self.data.get(name)
        return dateutil.parser.parse(str) if str is not None else None

    @property
    def created_at(self):
        """datetime: The date/time the data was created."""
        return self.__datetime("createdAt")

    @property
    def updated_at(self):
        """datetime: The date/time the data was updated."""
        return self.__datetime("updatedAt")

    @property
    def deleted_at(self):
        """datetime: The date/time the data was deleted."""
        return self.__datetime("deletedAt")

# https://dev.mixer.com/rest/index.html#UserWithChannel
class MixerUser(TimeStamped):

    def __init__(self, data, channel = None):
        self.data = data

        # determine channel information
        if isinstance(channel, MixerChannel):
            self._channel = channel
        else:
            channel_data = self.data.get("channel")
            self._channel = MixerChannel(channel_data, self)

    api = None
    def set_api(self, api):
        self.api = api
        self.channel.api = api

    @property
    def avatar_url(self):
        """str: A link to the users avatar on Mixer."""
        return self.data.get("avatarUrl")

    @property
    def bio(self):
        """str: The users biography on their Mixer profile. This may contain HTML."""
        return self.data.get("bio")

    @property
    def channel(self):
        """:class:`mixer.objects.MixerChannel`: Information about the Mixer channel associated with this user."""
        return self._channel

    @property
    def experience(self):
        """int: The user's experience points."""
        return self.data.get("experience")

    @property
    def groups(self):
        """list: A list of groups that the user is in. Each contains 'id' and 'name'."""
        return self.data.get("groups")

    @property
    def id(self):
        """int: The unique ID of the user."""
        return self.data.get("id")

    @property
    def level(self):
        """int: The user's current level on Mixer, as determined by the number of experience points the user has."""
        return self.data.get("level")

    @property
    def social(self):
        """dict: Social links."""
        return self.data.get("social")

    @property
    def sparks(self):
        """int: The amount of sparks the user has."""
        return self.data.get("sparks")

    @property
    def username(self):
        """str: The user's name. This is unique on the site and is also their channel name."""
        return self.data.get("username")

    @property
    def verified(self):
        """bool: Indicates whether the user has verified their e-mail."""
        return self.data.get("verified")

# https://dev.mixer.com/rest/index.html#ExpandedChannel
class MixerChannel:

    def __init__(self, data, user = None):
        self.data = data

        # determine user information
        if isinstance(user, MixerUser):
            self._user = user
        else:
            user_data = self.data.get("user")
            self._user = MixerUser(user_data, self)

    api = None
    def set_api(self, api):
        self.api = api
        self.user.api = api

    @property
    def id(self):
        """int: The unique ID of the channel."""
        return self.data.get("id")

    @property
    def username(self):
        """str: The name and url of the channel."""
        return self.data.get("token")

    @property
    def online(self):
        """bool: Indicates if the channel is currently streaming."""
        return self.data.get("online")

    @property
    def user(self):
        """:class:`mixer.objects.MixerUser`: Information about the Mixer user associated with this channel."""
        return self._user

    @property
    def featured(self):
        """bool: True if feature_level is > 0."""
        return self.data.get("featured")

    @property
    def feature_level(self):
        """int: The featured level for this channel. Its value controls the position and order of channels in the featured carousel."""
        return self.data.get("featureLevel")

    @property
    def partnered(self):
        """bool: Indicates if the channel is partnered."""
        return self.data.get("partnered")

    @property
    def transcoding_profile_id(self):
        """int: The id of the transcoding profile."""
        return self.data.get("transcodingProfileId")

    @property
    def suspended(self):
        """bool: Indicates if the channel is suspended."""
        return self.data.get("suspendeded")

    @property
    def name(self):
        """str: The title of the channel."""
        return self.data.get("name")

    @property
    def audience(self):
        """str ('family', 'teen', '18+'): The target audience of the channel."""
        return self.data.get("audience")

    @property
    def viewers_total(self):
        """int: Amount of unique viewers that have ever viewed this channel."""
        return self.data.get("viewersTotal")

    @property
    def viewers(self):
        """int: Amount of viewers currently watching this channel."""
        return self.data.get("viewersCurrent")

    @property
    def followers(self):
        """int: Amount of people following this channel."""
        return self.data.get("numFollowers")

    @property
    def description(self):
        """str: The description of the channel. Note that this may contain HTML."""
        return self.data.get("description")

    @property
    def game_type(self):
        """dict: The type of game broadcasted on the users channel."""
        return self.data.get("type")

    @property
    def interactive(self):
        """bool: Indicates if the channel is interactive."""
        return self.data.get("interactive")

    @property
    def interactive_game_id(self):
        """int: The ID of the interactive game used."""
        return self.data.get("interactiveGameId")

    @property
    def ftl(self):
        """int: The FTL stream id."""
        return self.data.get("ftl")

    @property
    def has_vod(self):
        """bool: Indicates if the channel has vod saved."""
        return self.data.get("hasVod")

    @property
    def language_id(self):
        """str: The ISO 639 language id."""
        return self.data.get("languageId")

    @property
    def banner_url(self):
        """str: The URL of the banner image."""
        return self.data.get("bannerUrl")

    @property
    def hosteeId(self):
        """int: The ID of the hostee channel."""
        return self.data.get("hosteeId")

    @property
    def has_transcodes(self):
        """bool: Indicates if the channel has transcodes enabled."""
        return self.data.get("hasTranscodes")

    @property
    def vods_enabled(self):
        """bool: Indicates if the channel has vod recording enabled."""
        return self.data.get("vodsEnabled")

    @property
    def costream_id(self):
        """str: The costream that the channel is in, if any."""
        return self.data.get("costreamId")

    @property
    def thumbnail(self):
        """dict: The resource information regarding the channel thumbnail."""
        return self.data.get("thumbnail")

    @property
    def cover(self):
        """dict: The resource information regarding the channel cover."""
        return self.data.get("cover")

    @property
    def badge(self):
        """dict: The resource information regarding the channel badge for subscribers."""
        return self.data.get("badge")

    @property
    def broadcast(self):
        """dict: Returns information about a channels ongoing broadcast."""
        return self.api.get_broadcast(self.id)

    @property
    def uptime(self):
        """int: Returns how long the current broadcast has been going for, in seconds."""
        return self.api.get_uptime(self.id)

    async def get_leaderboard(self, type, limit = 10):
        """dict: Gets a list of users on a specified leaderboard."""
        return await self.api.get_leaderboard(type, self.id, limit)

    async def get_uptime(self):
        """datetime.timedelta: The duration of the active broadcast."""
        return await self.api.get_uptime(self.id)

# https://pastebin.com/NW6NcS8z
class MixerChatMessage:

    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        """str: The unique identifier of the message."""
        return self.data.get("id")

    @property
    def username(self):
        """str: The username of the person who sent the message."""
        return self.data.get("user_name")

    @property
    def user_id(self):
        """int: The id of the user who sent the message."""

    @property
    def roles(self):
        """list: The roles the user has in the chat room."""
        return self.data.get("user_roles")

    @property
    def message_raw(self):
        """dict: The raw message data retrieved from the server."""
        return self.data.get("message")

    def has_role(self, role):
        """Determines whether or not the sender of the message has a specified role.

        Args:
            role (str): The role to check the sender for. (ex: 'Owner')

        Returns:
            bool: Indicates whether or not the message sender has the role.
        """
        return role in roles

    @property
    def text(self):
        """str: The raw text of the message."""
        text = ""
        for piece in self.message_raw["message"]:
            text += piece["text"]
        return text

    @property
    def tags(self):
        """list: A list of usernames tagged in this message, in order."""
        tags = list()
        for piece in self.message_raw["message"]:
            if piece["type"] == "tag":
                tags.append(piece["username"])
        return tags

    @property
    def skill(self):
        """dict: Gets the skill used that's associated with the message."""
        return self.message_raw["meta"].get("skill")

    @property
    def is_skill(self):
        """bool: Indicates if the message is a skill."""
        return self.message_raw["meta"].get("is_skill", False)

    @property
    def is_whisper(self):
        """bool: Indicates if the message is a whisper."""
        return self.message_raw["meta"].get("whisper", False)

    @property
    def is_censored(self):
        """bool: Indicates if the message is censored by Catbot's auto-moderation."""
        return self.message_raw["meta"].get("whisper", False)

    async def delete(self):
        """Deletes this message from the chat."""
        await self.chat.send_method_packet("deleteMessage", self.id)
