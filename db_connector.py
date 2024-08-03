from sqlalchemy import create_engine, inspect, Column, String, BigInteger, JSON
from sqlalchemy.orm import declarative_base, Session
import json

# i'll add option to switch to postgresql later
_db_string = "sqlite:///mountpoint/discord-ttsbot.db"

if _db_string is None:
    raise ValueError("DATABASE_URL environment variable is not set")

# Create the database engine
_engine = create_engine(_db_string)


def create_session():
    # remember to close the conn when done
    return Session(bind=_engine)


# this will be used for all database operations
conn = create_session()


# Create an inspector to get table information
inspector = inspect(_engine)

# base object for all tables
Base = declarative_base()


class QuotaTracker(Base):
    __tablename__ = "ttsbot_quota_tracker"
    characters_used = Column(BigInteger, default=0, primary_key=True)

    @staticmethod
    async def get_quota_usage():
        global conn
        try:
            quota = conn.query(QuotaTracker).first()
            if quota is None:
                quota = QuotaTracker()
                conn.add(quota)
                conn.commit()
            return quota.characters_used
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def add_to_quota(characters_used: int):
        global conn
        try:
            quota = conn.query(QuotaTracker).first()
            if quota is None:
                return False
            quota.characters_used += characters_used
            conn.commit()
            return True
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def modify_quota(characters_used: int):
        global conn
        try:
            quota = conn.query(QuotaTracker).first()
            if quota is None:
                return False
            quota.characters_used = characters_used
            conn.commit()
            return True
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False


class Server(Base):
    __tablename__ = "ttsbot_servers"

    id = Column(BigInteger, primary_key=True)
    lang = Column(String)
    voice = Column(String)

    @staticmethod
    async def _get(server_id: int):
        global conn
        try:
            server = conn.query(Server).filter_by(id=server_id).first()
            return server
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def _generate(server_id: int):
        global conn
        try:
            server = Server(id=server_id)
            conn.add(server)
            conn.commit()
            return server
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def get_or_generate(server_id: int):

        server = await Server._get(server_id)

        if server is None:
            server = await Server._generate(server_id)

        return server

    # above methods are used to get or generate a server object

    @staticmethod
    async def modify_server(server_id: int, lang: str = None, voice: str = None):
        global conn
        try:
            server = await Server.get_or_generate(server_id)
            if server is None:
                return False
            if voice is not None:
                server.voice = voice
            if lang is not None:
                server.lang = lang
            conn.commit()
            return True
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False


class User(Base):
    # will work on a "per-server" basis rather than a "per-user" basis
    # which will allow for a different voice for each server a user is in
    __tablename__ = "ttsbot_users"

    id = Column(BigInteger, primary_key=True)
    default_lang = Column(String, default="en-US")
    default_voice = Column(String, default="en-US-Wavenet-A")
    default_speed = Column(String, default="1.0")

    servers = Column(JSON, default={})
    # per server voice and speed dictionary
    # server_id: (lang, voice, speed)

    @staticmethod
    async def _get(user_id: int):
        global conn
        try:
            user = conn.query(User).filter_by(id=user_id).first()
            return user
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def _generate(user_id: int):
        global conn
        try:
            user = User(id=user_id)
            conn.add(user)
            conn.commit()
            return user
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False

    @staticmethod
    async def get_or_generate(user_id: int):
        user = await User._get(user_id)
        if user is None:
            user = await User._generate(user_id)
        return user

    @staticmethod
    async def modify_user(
        user_id: int,
        default_lang: str = None,
        default_voice: str = None,
        default_speed: str = None,
        server_id: str = None,
        server_lang: str = None,
        server_voice: str = None,
        server_speed: str = None,
    ):
        global conn
        try:
            user = conn.query(User).filter_by(id=user_id).first()
            if user is None:
                return False
            if default_lang is not None:
                user.default_lang = default_lang
            if default_voice is not None:
                user.default_voice = default_voice
            if default_speed is not None:
                user.default_speed = default_speed
            if server_id is not None:
                # we have to do json deserialization here
                deserialized_servers = json.loads(str(user.servers))
                print(deserialized_servers)
                print(user.servers)

                try:
                    _ = deserialized_servers[str(server_id)]
                except KeyError:
                    deserialized_servers[str(server_id)] = {}
                if server_lang is not None:
                    deserialized_servers[str(server_id)]["lang"] = server_lang
                if server_voice is not None:
                    deserialized_servers[str(server_id)]["voice"] = server_voice
                if server_speed is not None:
                    deserialized_servers[str(server_id)]["speed"] = server_speed
                user.servers = json.dumps(
                    deserialized_servers
                )  # dump the dictionary back to json

            conn.commit()
            return True
        except Exception as e:
            print(e)
            # reset the connection if an error occurs
            conn = create_session()
            return False


# This line has to come after the tables are defined
Base.metadata.create_all(_engine, checkfirst=True)
