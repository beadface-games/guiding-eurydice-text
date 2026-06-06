# -*- coding: utf-8 -*-
import json
import os
import pathlib
import typing as t

from datetime import datetime as dt
from pypresence import Presence

from src.level import TextLevel
from src.utils import (
    DATE_FORMAT_STR,
    DEFAULT_LEVEL_DATA_DIR,
    DEFAULT_PROFILE_DATA_DIR,
    TextUtility,
    UserDataManager,
)

class Stats():
    def __init__(
        self,
        num_orpheus_fatals: t.Optional[int] = None,
        num_orpheus_successes: t.Optional[int] = None,
        num_eurydice_fatals: t.Optional[int] = None,
        num_successes: t.Optional[int] = None,
    ):
        self.num_orpheus_fatals = num_orpheus_fatals or 0
        self.num_orpheus_successes = num_orpheus_successes or 0
        self.num_eurydice_fatals = num_eurydice_fatals or 0
        self.num_successes = num_successes or 0

    def to_dict(self) -> t.Dict[str, t.Any]:
        return {
            "num_orpheus_fatals": self.num_orpheus_fatals,
            "num_orpheus_successes": self.num_orpheus_successes,
            "num_eurydice_fatals": self.num_eurydice_fatals,
            "num_successes": self.num_successes
        }
    
    @staticmethod
    def from_dict(data: t.Dict[str, t.Any]) -> Stats:
        num_orpheus_fatals = None
        num_orpheus_successes = None
        num_eurydice_fatals = None
        num_successes = None

        if ("num_orpheus_fatals" in data.keys()) and (isinstance(data["num_orpheus_fatals"], int)):
            num_orpheus_fatals = data["num_orpheus_fatals"]
        
        if ("num_orpheus_successes" in data.keys()) and (isinstance(data["num_orpheus_successes"], int)):
            num_orpheus_successes = data["num_orpheus_successes"]

        if ("num_eurydice_fatals" in data.keys()) and (isinstance(data["num_eurydice_fatals"], int)):
            num_eurydice_fatals = data["num_eurydice_fatals"]

        if ("num_successes" in data.keys()) and (isinstance(data["num_successes"], int)):
            num_successes = data["num_successes"]

        return Stats(
            num_orpheus_fatals=num_orpheus_fatals,
            num_orpheus_successes=num_orpheus_successes,
            num_eurydice_fatals=num_eurydice_fatals,
            num_successes=num_successes,
        )

    def all_attempts(self) -> int:
        return self.num_orpheus_fails + \
                self.num_orpheus_successes + \
                self.num_eurydice_fails + \
                self.num_successes


class LevelInfo():
    class LevelMissingException(Exception):
        pass

    def __init__(
        self,
        id: int,
        title: str,
        level_path: t.Optional[pathlib.Path] = None,
        stats: t.Optional[LevelInfo.Stats] = None,
        locked: t.Optional[bool] = True,
        debug: t.Optional[bool] = False,
        user_data_manager: t.Optional[UserDataManager] = UserDataManager(),
        presence: t.Optional[Presence] = None,
    ):
        if not id:
            raise ValueError(f"No ID provided for profile at path {level_path}")
        
        self.id = id
        self.level_path = level_path or pathlib.Path(DEFAULT_LEVEL_DATA_DIR).joinpath(pathlib.Path("level" + str(id) + ".json"))
        self.title = title 
        self.user_data_manager = user_data_manager

        if not os.path.exists(self.user_data_manager.resource_path(self.level_path)):
            raise LevelInfo.LevelMissingException(f"Unable to find level at {self.level_path}")
        
        self.locked = locked

        self.stats = stats or Stats()
        self.debug = debug

        self.presence = None
        if presence:
            self.presence = presence

    def __str__(self) -> str:
        res = ""
        res += "LevelInfo".upper() + "\n"
        res += "id: " + str(self.id) + "\n"
        res += "title: " + self.title + "\n"
        res += "level_path:" + str(self.level_path) + "\n"
        res += "stats: " + str(self.stats) + "\n"
        res += "locked: " + str(self.locked) + "\n"
        return res

    def unlock(self):
        self.locked = False 

    def to_dict(self) -> t.Dict[str, t.Any]:
        lid = {}
        lid["title"] = self.title
        lid["level_path"] = str(self.level_path)
        lid["locked"] = self.locked
        lid["stats"] = self.stats.to_dict()

        return lid
    
    @staticmethod
    def from_dict(
        id: int,
        level_data: t.Dict[str, t.Any],
        debug: t.Optional[bool] = False,
        presence: t.Optional[Presence] = None,
    ) -> LevelInfo:
        title = None
        level_path = None
        locked = True
        stats = None
        
        if ("title" in level_data.keys()) and (isinstance(level_data["title"], str)):
            title = level_data["title"]

        if ("level_path" in level_data.keys()) and (isinstance(level_data["level_path"], str)):
            level_path = level_data["level_path"]
        
        if ("locked" in level_data.keys()) and (isinstance(level_data["locked"], bool)):
            locked = level_data["locked"]
        
        if ("stats" in level_data.keys()) and (isinstance(level_data["stats"], dict)):
            stats = Stats.from_dict(level_data["stats"])

        return LevelInfo(
            id=id,
            title=title,
            level_path=level_path,
            locked=locked,
            stats=stats,
            debug=debug,
            presence=presence,
        )

    def level(self) -> TextLevel:
        return TextLevel.from_json(
            json_path=self.user_data_manager.resource_path(self.level_path),
            debug=self.debug,
            presence=self.presence,
        )

class Profile():
    class CorruptProfileException(Exception):
        pass

    def __init__(
        self,
        id: int,
        name: t.Optional[str] = None,
        level_infos: t.Optional[t.Dict[int, LevelInfo]] = None,
        timestamp: t.Optional[dt] = None,
        profile_data_dir: t.Optional[pathlib.Path] = None,
        level_data_dir: t.Optional[pathlib.Path] = None,
        has_viewed_intro: t.Optional[bool] = False,
        has_viewed_tut: t.Optional[bool] = False,
        debug: t.Optional[bool] = False,
        user_data_manager: t.Optional[UserDataManager] = UserDataManager(),
        presence: t.Optional[Presence] = None,
    ):
        self.id = id
        self.name = name or ""
        self.level_infos: t.Dict[int, LevelInfo] = level_infos or {}
        self.timestamp = timestamp or dt.now()
        self.profile_data_dir = profile_data_dir or DEFAULT_PROFILE_DATA_DIR
        self.level_data_dir = level_data_dir or pathlib.Path(DEFAULT_LEVEL_DATA_DIR)
        self.has_viewed_intro = has_viewed_intro
        self.has_viewed_tut = has_viewed_tut
        self.debug = debug
        self.user_data_manager = user_data_manager

        self.text_utility = TextUtility(debug=self.debug)

        if presence:
            self.presence = presence

        if len(self.level_infos.keys()) < 1:
            self.init_levels()
        else:
            for _, li in self.level_infos.items():
                li.debug = self.debug

    @staticmethod
    def load(
        profile_data: t.Dict[str, t.Any],
        debug: t.Optional[bool] = False,
        presence: t.Optional[Presence] = None,
    ) -> Profile:
        id = None
        name = None
        level_infos = {}
        timestamp = None
        profile_data_dir = None
        level_data_dir = None
        has_viewed_intro = None
        has_viewed_tut = None

        if ("id" in profile_data.keys()) and (isinstance(profile_data["id"], int)):
            id = profile_data["id"]
        else:
            raise Profile.CorruptProfileException()

        if ("name" in profile_data.keys()) and (isinstance(profile_data["name"], str)):
            name = profile_data["name"]

        if ("timestamp" in profile_data.keys()) and (isinstance(profile_data["timestamp"], str)):
            try:
                timestamp = dt.strptime(profile_data["timestamp"], DATE_FORMAT_STR)
            except ValueError:
                if debug:
                    print(f"Failed to parse timestamp {profile_data["timestamp"]}. Setting to now")
                    timestamp = dt.now()
        else:
            timestamp = dt.now()
        
        if ("level_info" in profile_data.keys()) and (isinstance(profile_data["level_info"], dict)):
            for i, lid in profile_data["level_info"].items():
                id_int = int(i)
                if (isinstance(lid, dict)):
                    level_info = LevelInfo.from_dict(id=id_int, level_data=lid, presence=presence)
                    level_infos[id_int] = level_info

        if ("level_data_dir" in profile_data.keys()) and (isinstance(profile_data["level_data_dir"], str)):
            level_data_dir = pathlib.Path(profile_data["level_data_dir"])

        if ("profile_data_dir" in profile_data.keys()) and (isinstance(profile_data["profile_data_dir"], str)):
            profile_data_dir = pathlib.Path(profile_data["profile_data_dir"])
        
        if ("has_viewed_intro" in profile_data.keys()) and (isinstance(profile_data["has_viewed_intro"], bool)):
            has_viewed_intro = profile_data["has_viewed_intro"]

        if ("has_viewed_tut" in profile_data.keys()) and (isinstance(profile_data["has_viewed_tut"], bool)):
            has_viewed_tut = profile_data["has_viewed_tut"]
        
        return Profile(
            id=id,
            name=name,
            level_infos=level_infos,
            timestamp=timestamp,
            profile_data_dir=profile_data_dir,
            level_data_dir=level_data_dir,
            has_viewed_intro=has_viewed_intro,
            has_viewed_tut=has_viewed_tut,
            presence=presence,
            debug=debug
        )
    
    def to_dict(self) -> t.Dict[str, t.Any]:
        res = {}

        res["id"] = self.id
        res["name"] = self.name

        lis = {}
        for id, li in self.level_infos.items():
            id_int = -1
            id_int = int(id)
            lid = li.to_dict()
            lis[id_int] = lid

        res["level_info"] = lis
        res["timestamp"] = dt.strftime(self.timestamp, DATE_FORMAT_STR)
        res["profile_data_dir"] = str(self.profile_data_dir)
        res["level_data_dir"] = str(self.level_data_dir)
        res["has_viewed_intro"] = self.has_viewed_intro
        res["has_viewed_tut"] = self.has_viewed_tut

        return res
    
    def update_timestamp(self):
        self.timestamp = dt.now()
    
    def save(self) -> pathlib.Path:
        self.update_timestamp()
        dict = self.to_dict()

        ex = None
        file_path = self.profile_data_dir.joinpath("{:02d}".format(self.id) + "_" + self.name + "_profile.json")  
        with open(file_path, "w") as f:
            try:
                json.dump(dict, f, indent=4, ensure_ascii=False)
            except Exception as e:
                ex = e
                
        if ex:
            os.remove(file_path)
            raise(ex)       
        
        return file_path
    
    def init_levels(self):
        level_infos = {}
        level_files = []
        
        for _, _, filenames in os.walk(self.user_data_manager.resource_path(self.level_data_dir)):
            level_files.extend(filenames)

        if len(level_files) < 1:
            raise FileNotFoundError(f"Couldn't find level files in  {str(self.user_data_manager.resource_path(self.level_data_dir))}")
        
        for file in level_files:
            if file.startswith("level") and file.endswith(".json"):
                file_path = self.user_data_manager.resource_path(self.level_data_dir.joinpath(file))
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    title = None
                    id = None

                    if ("id" in data.keys()) and (isinstance(data["id"], int)):
                        id = data["id"]

                    else:
                        raise ValueError(f"No id found in level file {file_path}")

                    if ("title" in data.keys()) and (isinstance(data["title"], str)):
                        title = data["title"]
                    else:
                        raise ValueError(f"No title found in level file {file_path}")

                    tutorial_complete = False if id < 3 else True
            
                    level_info = LevelInfo(
                        id=id,
                        title=title,
                        level_path=file_path,
                        stats=Stats(),
                        locked=True,
                        debug=self.debug,
                        presence=self.presence,
                    )
            
                    level_infos[id] = level_info
        
        self.level_infos = level_infos

        if len(self.level_infos) < 1:
            raise ValueError(f"Failed to load any levels at {str(self.user_data_manager.resource_path(self.level_data_dir))}")

        self.level_infos[1].unlock()



        
        


        




    





                





