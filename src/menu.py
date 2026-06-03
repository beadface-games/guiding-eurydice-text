# -*- coding: utf-8 -*-
from datetime import datetime as dt

import json
import os
import pathlib
import random
import re
import time
import typing as t

from src.level import TextLevel
from src.profile import DEFAULT_LEVEL_DATA_DIR, DEFAULT_PROFILE_DATA_DIR, Profile
from src.tutorial import TutorialPlayer
from src._utils import B_FOR_BACK_STR_MENU, DEFAULT_TUT_DATA_DIR, UserDataManager, TextUtility

type MenuAction = t.Callable[[t.Any], Menu]

class Option:
    def __init__(
        self,
        name: str,
        func: MenuAction,
    ):
        self.name = name
        self.func = func

    def run(self) -> t.Union[LevelMenu, None]:
        return self.func()
    
class Menu:
    def __init__(
        self,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
    ):
        self.debug = debug
        self.rng = rng or random.Random()
        
        self.text_utility = TextUtility(
            debug=self.debug,
            rng=self.rng,
        )

    def quit(self):
        self.text_utility.clear_screen()
        print(self.text_utility.center_text("Goodbye."))
        time.sleep(0.5)
        raise SystemExit(0)        

class ProfileMenu(Menu):
    def __init__(
        self,
        save_data_dir: t.Optional[pathlib.Path] = None,
        profile_data_dir: t.Optional[pathlib.Path] = None,
        tut_data_dir: t.Optional[pathlib.Path] = None,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
        user_data_manager: t.Optional[UserDataManager] = UserDataManager()
    ):
        self.rng = rng or random.Random()
        super().__init__(debug=debug, rng=self.rng)

        self.user_data_manager = user_data_manager
        self.level_data_dir = save_data_dir or pathlib.Path(DEFAULT_LEVEL_DATA_DIR)
        self.profile_data_dir = profile_data_dir or pathlib.Path(DEFAULT_PROFILE_DATA_DIR)
        self.tut_data_dir = tut_data_dir or pathlib.Path(DEFAULT_TUT_DATA_DIR)

        self.profiles = {}
        self.load_profiles()
        self.last_profile = self.get_last_profile()
        self.options = {}
        self.reload_options()  

        self.tutorial_player = TutorialPlayer(
            profile=self.last_profile,
            debug=self.debug,
            rng=self.rng,
            tut_data_dir=self.tut_data_dir)

    def sort_options(
        self,
        opts_to_sort: t.Optional[t.Dict[int, Option]] = None
    ):
        sorted_options = {}

        if opts_to_sort:
            sorted_options = {k: v for k, v in sorted(opts_to_sort.items(), key=lambda item: item[0])}
        else:
            sorted_options = {k: v for k, v in sorted(self.options.items(), key=lambda item: item[0])}

        self.options = sorted_options

    def insert_option(
        self,
        opt: Option,
        before: int,
    ):
        new_options = {}

        for key, val in self.options.items():
            if key >= before:
                new_options[key + 1] = val
            else:
                new_options[key] = val

        new_options[before] = opt
        self.sort_options(opts_to_sort=new_options)

    def reload_options(self):
        self.options = {
            1: 
            Option(
                "Create New Profile",
                self.create_new_profile,
            )
        }

        self.sort_options()

        if len(self.profiles.keys()) > 1:
            self.insert_option(Option(
                "Load Another Profile",
                self.load_other_profile,
            ), 1)

        if self.last_profile:
            self.insert_option(Option(
                f"Continue as {self.last_profile.name}",
                self.load_last_profile
            ), 1)

            if self.last_profile.has_viewed_intro:
                self.insert_option(Option(
                    "Play Intro",
                    self.play_intro
                ), len(self.options.keys()) + 1)

            if self.last_profile.has_viewed_tut:
                self.insert_option(Option(
                    "Play Tutorial",
                    self.play_tutorial,
                ), len(self.options.keys()) + 1)
            
    
    def load_profiles(self) -> t.Dict[int, Profile]:
        if not os.path.exists(self.profile_data_dir):
            raise FileNotFoundError(f"Unable to find profile directory at {str(self.profile_data_dir)}")
        
        files = []
        for _, _, filenames in os.walk(self.profile_data_dir):
            files.extend(filenames)
        
        if len(filenames) != 0:
            for file in filenames:
                if "profile" in file.lower() and file.endswith(".json"):
                    with open(self.profile_data_dir.joinpath(file), "r", encoding="utf-8") as f:
                        data = json.load(f)
                        profile = Profile.load(
                            profile_data=data,
                            debug=self.debug,
                        )
                        self.profiles[profile.id] = profile

    def get_last_profile(self) -> Profile:
        latest_timestamp = dt.min
        champ = None

        for _, profile in self.profiles.items():
            if profile.timestamp > latest_timestamp:
                latest_timestamp = profile.timestamp
                champ = profile
        
        return champ
    
    def get_next_id(self) -> int:
        champ = 0

        for id, _ in self.profiles.items():
            if id > champ:
                champ = id

        return champ + 1
    
    def profile_name_exists(self, name: str) -> bool:
        for _, profile in self.profiles.items():
            if profile.name == name:
                return True
            
        return False
    
    def validate_profile_name(self, name: str) -> t.Tuple[bool, str]:
        err_strs = []
        valid = True
        err_str = ""

        if name == "B":
            self.render()

        if len(name) < 1:
            valid = False
            err_strs.append("contain at least one character")
        if len(name) > 20:
            valid = False
            err_strs.append("contain fewer than 20 characters")
        if re.match("^[a-zA-Z0-9]+$", name) is None:
            valid = False
            err_strs.append("contain only alphanumeric characters")
        if self.profile_name_exists(name):
            valid = False
            err_strs.append("not be identical to an existing profile name")
        
        if not valid and len(err_strs) > 0:
            err_str = "Profile name must "
            
            if len(err_strs) > 2:
                err_str += ", ".join(err_strs[0:len(err_strs)]) + ", and " + err_strs[len(err_strs) - 1]
            elif len(err_strs) > 1:
                err_str += " and ".join(err_strs)
            else:
                err_str += err_strs[0]

            err_str += ". Please try again.\n> "
        
        return valid, err_str
    
    def validate_profile_selection(
            self,
            choice: str,
            valid_choices: t.List[int]
        ) -> t.Tuple[bool, str]:
        valid = True
        err_str = ""
        choice_int = -1

        if choice.upper() == "Q":
            self.quit()
        elif choice.upper() == "B":
            self.render()
        else:
            try:
                choice_int = int(choice)
            except ValueError:
                valid = False
                err_str = "That isn't a number."
            
            if choice_int not in valid_choices:
                valid = False
                err_str = "That isn't a number corresponding to a profile."
        
        return valid, err_str
    
    def render(
        self,
        prompt: t.Optional[str] = None,
    ) -> Menu:
        try:
            self.reload_options()
            self.text_utility.clear_screen()

            title = "Guiding Eurydice".upper()
            lines = [
                title,
                "=" * len(title),
                "\n" * (self.text_utility.get_term_height() // 2),
            ]

            option_dict = {}
            option_lines = []

            for i, option in self.options.items():
                option_dict[i] = option
                option_lines.append("{:02d}".format(i) + " " + option.name)

            lines.extend(option_lines)

            choice = self.text_utility.menu_screen(lines=lines, prompt=prompt)
            valid, err = self.validate_profile_selection(choice, option_dict.keys())

            while not valid:
                choice = self.text_utility.menu_screen(lines=lines, prompt=err + "\nPlease try again.\n> ")
                valid, err = self.validate_profile_selection(choice, option_dict.keys())
            
            opt = option_dict[int(choice)]
            return opt.run()
        except KeyboardInterrupt:
            self.quit()

# region menu actions

    def load_last_profile(self) -> LevelMenu:
        LevelMenu.from_profile(
            self.last_profile,
            debug=self.debug,
            rng=self.rng
        ).render(
            not self.last_profile.has_viewed_intro,
            not self.last_profile.has_viewed_tut,
        )

    def load_other_profile(self) -> LevelMenu:
        try:
            profile_list = [profile for _, profile in self.profiles.items() if profile != self.last_profile]
            profile_list.sort(key=lambda p: p.timestamp)     

            if len(profile_list) == 1:
                self.last_profile = profile_list[0]
                self.last_profile.save()
                self.render(prompt=f"Loaded your only other profile, {self.last_profile.name}.\n> ")
                
            profile_map = {}
            profile_strs = []

            for i, profile in enumerate(profile_list):
                profile_str = str(i + 1) + " " + profile.name
                profile_strs.append(profile_str)
                profile_map[i + 1] = profile
            
            choice = self.text_utility.menu_screen(lines=profile_strs, is_submenu=True)
            valid, err = self.validate_profile_selection(choice, profile_map.keys())

            while not valid:
                choice = self.text_utility.menu_screen(lines=profile_strs, prompt=err + "\nPlease try again.\n> ")
                valid, err = self.validate_profile_selection(choice, profile_map.keys())
            
            profile = profile_map[int(choice)]
            self.last_profile = profile
            self.last_profile.save()
            LevelMenu.from_profile(profile).render(not profile.has_viewed_intro)
        except KeyboardInterrupt:
            self.quit()

    def create_new_profile(self) -> LevelMenu:
        id = self.get_next_id()
        
        try:
            self.text_utility.clear_screen()
            name = self.text_utility.menu_screen(lines=["Create a New Profile"], prompt="Please enter a name for your new profile.\n" + B_FOR_BACK_STR_MENU + ".\n> ")
            valid, err_str = self.validate_profile_name(name)

            while not valid:
                name = input(err_str)
                valid, err_str = self.validate_profile_name(name)

            profile = Profile(
                id,
                name
            )

            profile.save()
            self.profiles[profile.id] = profile
            self.last_profile = profile
            self.load_last_profile()
        except KeyboardInterrupt:
            self.quit()   

    def play_intro(self) -> ProfileMenu:
        try:
            res = self.tutorial_player.play(level=None, phase=TextLevel.TutorialPhase.INTRO)
            if res:
                self.last_profile.has_viewed_intro = True
            self.last_profile.save()  
            return self.render()     
        except KeyboardInterrupt:
            self.quit()

    def play_tutorial(self) -> LevelMenu:
        levels = self.tutorial_player.load_tut_levels()

        i = 0
        res = True
        
        try:
            while res and (i < len(levels)):
                if levels[i].orpheus_only:
                    tutorial_phase = TextLevel.TutorialPhase.ORPHEUS_ONLY
                else:
                    tutorial_phase = TextLevel.TutorialPhase.DEDUCTION_START
            
                res = self.tutorial_player.play(level=levels[i], phase=tutorial_phase)

                i += 1
        except KeyboardInterrupt:
            return self.quit()
                
        self.last_profile.has_viewed_tut = True
        self.last_profile.save()
        return self.render()

# endregion

class LevelMenu(Menu):
    def __init__(
        self,
        profile: Profile,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None
    ):
        self.rng = rng or random.Random()
        super().__init__(debug=debug, rng=self.rng)
        self.profile = profile

        self.tutorial_player = TutorialPlayer(
            profile=self.profile,
            debug=self.debug,
            rng=self.rng,
        )

    def quit(self):
        self.profile.save()
        super().quit()

    @staticmethod
    def from_profile(
        profile: Profile,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None
    ) -> LevelMenu:
        return LevelMenu(
            profile=profile,
            debug=debug,
            rng=rng or random.Random()
        )

    def get_level_strs(self) -> t.List[str]:
        level_strs = []

        for id, level_info in sorted(self.profile.level_infos.items()):
            level_str = "{:02d}".format(id) + " - "

            if level_info.locked:
                level_str += "?" * 20
            else:
                level_str += level_info.title
            
            level_strs.append(level_str)
        
        return level_strs

    def validate_level_selection(self, choice: str) -> t.Tuple[bool, str]:
        valid = True
        err_str = ""
        choice_int = -1

        if choice.upper() == "B":
            ProfileMenu(
                debug=self.debug,
                rng = self.rng
            ).render()
        elif choice.upper() == "Q":
            self.quit()
        else:
            try:
                choice_int = int(choice)
            except ValueError:
                valid = False
                err_str = "That isn't a number."
            
            if choice_int not in self.profile.level_infos.keys():
                valid = False
                err_str = "That isn't the number of a level."
            elif self.profile.level_infos[choice_int].locked:
                valid = False
                err_str = "You haven't unlocked that level yet."
        
        return valid, err_str  

    def run_level(self, choice: str):
        choice_int = int(choice)
        level_info = self.profile.level_infos[choice_int]

        level = level_info.level()
        res = level.run()

        if res:
            self.profile.level_infos[choice_int].tutorial_complete = True

            if choice_int < len(self.profile.level_infos.keys()):
                try:
                    self.profile.level_infos[choice_int + 1].unlock()
                except ValueError:
                    if self.debug:
                        print("Failed to unlock level", choice_int + 1)
                        self.text_utility.wait_for_enter()
        
        self.profile.save()

        self.render(not self.profile.has_viewed_intro) 
    
    def render(self,
               play_intro: t.Optional[bool] = False,
               play_tutorial: t.Optional[bool] = False,
        ):
        try:
            self.text_utility.clear_screen()

            if play_intro:
                try:
                    res = self.tutorial_player.play(level=None, phase=TextLevel.TutorialPhase.INTRO)
                except KeyboardInterrupt:
                    return self.quit()
                
                if res:
                    self.profile.has_viewed_intro = True
                    self.profile.save()

            if play_tutorial:
                levels = self.tutorial_player.load_tut_levels()

                i = 0
                res = True
                
                try:
                    print(f"i: {i}")
                    while res and (i < len(levels)):
                        if levels[i].orpheus_only:
                            print("setting phase to orpheus only")
                            tutorial_phase = TextLevel.TutorialPhase.ORPHEUS_ONLY
                        else:
                            print("setting phase to orpheus start")
                            tutorial_phase = TextLevel.TutorialPhase.DEDUCTION_START
                    
                        res = self.tutorial_player.play(level=levels[i], phase=tutorial_phase)
                        i += 1
                except KeyboardInterrupt:
                    return self.quit()
                        
                self.profile.has_viewed_tut = True
                self.profile.save()     

            choice = self.text_utility.menu_screen(lines=self.get_level_strs(), is_submenu=True, additional_prompt=f"Welcome, {TextUtility.blue(self.profile.name)}.")
            valid, err = self.validate_level_selection(choice)

            while not valid:
                choice = self.text_utility.menu_screen(lines=self.get_level_strs(), prompt=err + "\nPlease try again.\n> ")
                valid, err = self.validate_level_selection(choice)

            self.run_level(choice)
        except KeyboardInterrupt:
            self.quit()
        
        




            