import json

# https://dev.mixer.com/rest/index.html#UserWithChannel
class MixerUser:

    api = None

    def __init__(self, data, channel = None):
        self.data = data
        self.channel = channel

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
        return self.channel if isinstance(self.channel, MixerChannel) else MixerChannel(self.channel, self)

    @property
    def registered(self):
        """datetime: The date & time the users account was created at."""
        str = self.data.get("createdAt")
        return dateutil.parser.parse(str)

    @property
    def deleted(self):
        """datetime: The date & time the users account was deleted at."""
        str = self.data.get("deletedAt")
        return dateutil.parser.parse(str) if not str is None else None

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

    @property
    def updated(self):
        """datetime: The date & time the users account was updated at."""

# https://dev.mixer.com/rest/index.html#ExpandedChannel
class MixerChannel:

    api = None

    def __init__(self, data, user = None):
        self.data = data
        self.user = user

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
        return self.user if isinstance(self.user, MixerUser) else MixerUser(self.user, self)

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

    def get_leaderboard(self, type, limit = 10):
        """dict: Gets a list of users on a specified leaderboard."""
        return self.api.get_leaderboard(type, self.id, limit)

# https://pastebin.com/NW6NcS8z
class MixerChatMessage:

    def __init__(self, data):
        self.__dict__.update(**data)

    def has_role(self, role):
        return role in self.user_roles

    def get_text(self):
        text = ""
        for piece in self.message["message"]:
            text += piece["text"]
        return text

    def get_tags(self):
        tags = list()
        for piece in self.message["message"]:
            if piece["type"] == "tag":
                tags.append(piece["username"])
        return tags

    def get_skill(self):
        return self.message["meta"].get("skill")

    async def delete(self):
        await self.chat.send_method_packet("deleteMessage", self.id)
