from __future__ import annotations
from enum import Enum

import json
import pathlib
import time
import typing as t

from guiding_eurydice_core.src.difficulty import Difficulty
from guiding_eurydice_core.src.lyre import Lyre, Note
from guiding_eurydice_core.src.level import Goal, Level
from src._utils import RequirementVerb, TextUtility

DIFFICULTY_JSON_PATH = pathlib.Path("guiding_eurydice_levels/difficulty_settings.json")


class TextLevel(Level):
    class QuitGameException(Exception):
        pass

    class Phase(Enum):
        class InvalidPhaseException(Exception):
            pass

        ORPHEUS = 0
        DEDUCTION = 1

    REQUIREMENT_VERBS = [
        RequirementVerb("want"),
        RequirementVerb("need"),
        RequirementVerb("desire"),
        RequirementVerb("crave"),
        RequirementVerb(plural="long", preposition="for"),
        RequirementVerb(plural="yearn", preposition="for")
    ]

    def __init__(
        self,
        title: t.Optional[str] = "",
        lyre: t.Optional[Lyre] = None,
        difficulty: t.Optional[Difficulty] = None,
        orpheus_goal: t.Optional[Goal] = None,
        orpheus_only: t.Optional[bool] = False,
        challenge_name: t.Optional[str] = "",
        challenge_number: t.Optional[int] = 1,
        descriptions: t.Optional[t.List[str]] = None,
        orpheus_prompts: t.Optional[t.List[str]] = None,
        deduction_prompts: t.Optional[t.List[str]] = None,
        success_text: t.Optional[t.List[str]] = None,
        fail_text: t.Optional[t.List[str]] = None,
        fatal_text: t.Optional[t.List[str]] = None,
        thwart_line: t.Optional[t.Lst[str]] = "In your attempts to guide her, you have left Eurydice with no path forward.",
        debug: t.Optional[bool] = False,
        given_seed: t.Optional[int] = None,
    ) -> None:
        self.title = title or ""
        self.difficulty = difficulty or Difficulty()
        self.challenge_name = challenge_name or ""
        self.challenge_number = challenge_number or 1
        self.descriptions = descriptions or []
        self.deduction_prompts = deduction_prompts or []
        self.orpheus_prompts = orpheus_prompts or []
        self.success_text = success_text or []
        self.fail_text = fail_text or []
        self.fatal_text = fatal_text or []
        self.thwart_line = thwart_line or "In your attempts to guide her, you have left Eurydice with no path forward."


        l = lyre or Lyre()

        og = orpheus_goal or Goal()

        self.orpheus_only = orpheus_only

        self.description_idx = 0
        self.phase_prompt_idx = 0
        self.fail_idx = 0
        self.fatal_idx = 0
        self.requirement_verb_idx = 0

        self.debug = debug

        self.level = Level(
            lyre=l,
            difficulty=self.difficulty,
            orpheus_goal=og,
            debug=self.debug,
            given_seed=given_seed,
        )   

        self.text_utility = TextUtility(
            rng=self.level.rng,
            debug=self.debug,
        )

        if self.debug:
            print("CREATED NEW TEXT LEVEL")
            print(f"title: {self.title}")
            print(f"difficulty: {str(self.difficulty)}")
            print(f"challenge name: {self.challenge_name}")
            print(f"challenge number: f{str(self.challenge_number)}")
            print(f"orpheus goal: {str(self.level.orpheus_goal)}")
            print(f"descriptions (len): {str(len(self.descriptions))}")
            print(f"deduction prompts (len): {str(len(self.deduction_prompts))}")
            print(f"orpheus prompts (len): {str(len(self.orpheus_prompts))}")
            print(f"success text (len): {str(len(self.success_text))}")
            print(f"fail text: {str(len(self.fail_text))}")
            print(f"fatal text (len): {str(len(self.fatal_text))}")
            print(f"thwart line: {self.thwart_line}")

    @staticmethod
    def from_json(
        json_path: pathlib.Path,
        debug: t.Optional[bool] = False,
        seed: t.Optional[int] = None,
    ) -> TextLevel:
        title = None
        difficulty = None
        lyre = None
        orpheus_goal = None
        orpheus_only = False
        challenge_name = None
        challenge_number = None
        descriptions = None
        orpheus_prompts = None
        deduction_prompts = None
        success_text = None
        fail_text = None
        fatal_text = None
        thwart_line = None

        with open(json_path, "r") as f:
            data = json.load(f)

            if ("title" in data.keys()) and (isinstance(data["title"], str)):
                title = data["title"]
            
            if ("difficulty" in data.keys()) and (isinstance(data["difficulty"], int)):
                difficulty = Difficulty.from_json(data["difficulty"], DIFFICULTY_JSON_PATH)

            if ("lyre" in data.keys()) and (isinstance(data["lyre"], list)):
                notes: list[int] = []
                for item in data["lyre"]:
                    if (isinstance(item, dict)) and ("note" in item.keys()):
                        n = item["note"]

                        if (
                            "name" in n.keys()
                            and isinstance(n["name"], str)
                            and "val" in n.keys()
                            and isinstance(n["val"], int)
                        ):
                            count = 1
                            if ("count" in n.keys()) and (isinstance(n["count"], int)):
                                count = n["count"]

                            note = Note(name=n["name"], val=n["val"], count=count)
                            notes.append(note)

                lyre = Lyre(
                    notes=notes,
                    debug=debug,
                    difficulty=difficulty,
                )

            if ("orpheus_goal" in data.keys()) and (isinstance(data["orpheus_goal"], int)):
                orpheus_goal = Goal(data["orpheus_goal"])

            if ("orpheus_only" in data.keys()) and (isinstance(data["orpheus_only"], bool)):
                orpheus_only = data["orpheus_only"]

            if ("thwart_line" in data.keys()) and (isinstance(data["thwart_line"], str)):
                thwart_line = data["thwart_line"]

            if "challenge" in data.keys():
                challenge = data["challenge"]

                if len(challenge.keys()) > 0:
                    if ("name" in challenge.keys()) and (isinstance(challenge["name"], str)):
                        challenge_name = challenge["name"]
                    
                    if ("number" in challenge.keys()) and (isinstance(challenge["number"], int)):
                        challenge_number = challenge["number"]

            if ("descriptions" in data.keys()) and (isinstance(data["descriptions"], list)):
                descriptions = data["descriptions"]

            if ("orpheus_prompts" in data.keys()) and (isinstance(data["orpheus_prompts"], list)):
                orpheus_prompts = data["orpheus_prompts"]

            if ("deduction_prompts" in data.keys()) and (isinstance(data["deduction_prompts"], list)):
                deduction_prompts = data["deduction_prompts"]

            if ("success_text" in data.keys()) and (isinstance(data["success_text"], list)):
                success_text = data["success_text"]

            if ("fail_text" in data.keys()) and (isinstance(data["fail_text"], list)):
                fail_text = data["fail_text"]

            if ("fatal_text" in data.keys()) and (isinstance(data["fatal_text"], list)):
                fatal_text = data["fatal_text"]

            return TextLevel(
                title=title,
                lyre=lyre,
                difficulty=difficulty,
                orpheus_goal=orpheus_goal,
                orpheus_only=orpheus_only,
                challenge_name=challenge_name,
                challenge_number=challenge_number,
                descriptions=descriptions,
                orpheus_prompts=orpheus_prompts,
                deduction_prompts=deduction_prompts,
                success_text=success_text,
                fail_text=fail_text,
                fatal_text=fatal_text,
                debug=debug,
                given_seed=seed,
                thwart_line=thwart_line,
            )

    def print(self):
        self.text_utility.clear_screen()
        self.print_header()
        self.print_lyre()
        self.print_lyre_prompt()
        self.print_requirement()

    def reset(self):
        self.level.reset()

    def phase(self) -> Phase:
        if self.orpheus_only or \
            (self.level.state == self.level.LevelState.READY):
            return self.Phase.ORPHEUS

        if (self.level.state == self.level.LevelState.ORPHEUS_SUCCESS) or \
            (self.level.state == self.level.LevelState.EURYDICE_FAIL) or \
            (self.level.state == self.level.LevelState.EURYDICE_THWARTED):
            return self.Phase.DEDUCTION
    
        raise self.Phase.InvalidPhaseException()
    
    def graceful_shutdown(self):
        self.text_utility.clear_screen()
        self.text_utility.fade_msg(
                "Your song dwindles into nothingness...",
                1000,
                4,
                min_time_in_ms_per_it=250,
            )
        time.sleep(1)
        raise SystemExit(0)
    
    def quit_or_try_again(self):
        print("Press Q + <Enter> to quit. Press <Enter> to try again.")

        i = input().strip()
        if i.upper() == "Q":
            self.graceful_shutdown()

        self.reset()
        self.run()

    def end(self):
        if self.level.state == Level.LevelState.SUCCESS:
            return
        
        if (self.challenge_name != "Eurydice"):
            self.print_fatal_msg()
            self.fatal_idx += 1
            self.quit_or_try_again()
        else:
            self.end_with_look()

    def end_with_look(self):            
            def _force_look_back():
                demand = "Press any key to look back".upper()
                self.text_utility.flash_msg(self.text_utility.center_text(line=demand), 1, 3)
                _ = input()
                self.text_utility.clear_screen()
                _print_demise_str()
                time.sleep(3)
            
            def _print_demise_str():
                demise_strs = [
                    "Because he loved her, he glanced behind him.",
                    "She instantly fell back. Poor Orpheus",
                    "stretched out both his arms, trying to hold her",
                    "and be held. He caught nothing but thin air.",
                ]

                print(self.text_utility.center_text(lines=self.text_utility.boxify_lines(demise_strs)))
            
            if self.level.state == Level.LevelState.ORPHEUS_FATAL:
                self.print_fatal_msg()
                self.fatal_idx += 1
                _force_look_back()
            elif self.level.state == Level.LevelState.EURYDICE_FATAL:
                print("Eurydice is lost.")
                _force_look_back()
            
            self.quit_or_try_again()

    def end_with_broken_string(
        self,
        broken_string: Note,        
    ):
        self.text_utility.clear_screen()
        print(self.text_utility.center_text(
            lines=[
                f"Your {broken_string.name} string snaps with a discordant twang.",
                "Without your lyre, you cannot go on."
            ]
        ))

        self.quit_or_try_again()

    def print_requirement(self):
        curr_phase = self.phase()
        requirement_line = ""

        if curr_phase == self.Phase.ORPHEUS:
            requirement_line += "Orpheus" 
        elif curr_phase == self.Phase.DEDUCTION:
            requirement_line += self.challenge_name
        
        requirement_line += " "
        requirement_verb = self.REQUIREMENT_VERBS[self.requirement_verb_idx % len(self.REQUIREMENT_VERBS)]

        if curr_phase == self.Phase.DEDUCTION and self.challenge_number > 1:
            requirement_line += requirement_verb.plur()
        else:
            requirement_line += requirement_verb.sing()

        requirement_line += ": "
        
        if curr_phase == self.Phase.ORPHEUS:
            requirement_line += str(self.level.orpheus_goal.val)
        elif curr_phase == self.Phase.DEDUCTION:
            requirement_line += "?"
        
        print(requirement_line)
        self.requirement_verb_idx += 1

    def print_header(
            self,
            omit_description: t.Optional[bool] = False,
        ):
        title_line = f"LEVEL {self.level.id}: {self.title.upper()} - seed={str(self.level.seed)} (Q to Quit)"
        description = self.descriptions[self.description_idx % len(self.descriptions)]

        if self.debug:
            title_line += f" ({str(self.level.get_state())})"

        term_width = self.text_utility.get_term_width()
        print("=" * term_width)
        print(
            " " * self.text_utility.get_horizontal_padding(term_width, title_line),
            title_line,
            " " * self.text_utility.get_horizontal_padding(term_width, title_line),
        )
        print("=" * term_width)

        if not omit_description:
            print(
                " " * self.text_utility.get_horizontal_padding(term_width, description),
                description,
                " " * self.text_utility.get_horizontal_padding(term_width, description),
            )
            print("-" * term_width)
            self.description_idx += 1

    def print_lyre(self):
        print(self.level)

    def print_success_msg(self, linger_time_s: t.Optional[int]=3):
        self.text_utility.clear_screen()
        print(self.text_utility.center_text(lines=self.text_utility.boxify_lines(lines=self.success_text)))
        time.sleep(linger_time_s)

    def print_fail_msg(self, linger_time_s: t.Optional[int]=3):
        self.text_utility.clear_screen()
        fail_msg = self.fail_text[self.fail_idx % len(self.fail_text)]
        print(self.text_utility.center_text(fail_msg))
        time.sleep(linger_time_s)
        self.fail_idx += 1

    def print_fatal_msg(self, linger_time_s: t.Optional[int]=3):
        self.text_utility.clear_screen()
        fatal_msg = self.fatal_text[self.fatal_idx % len(self.fatal_text)]
        print(self.text_utility.center_text(fatal_msg))
        time.sleep(linger_time_s)
        self.fatal_idx += 1

    def format_song_line(
        self,
        notes: t.List[Note],
        total: int,
        is_eurydices_turn: bool,
        eurydice_sum_len: t.Optional[int],
    ) -> str:
        values = [str(note.val) for note in notes]

        if is_eurydices_turn:
            blanks_needed = max((eurydice_sum_len or 0) - len(notes), 0)
            values.extend("_" for _ in range(blanks_needed))

        if not values:
            left_side = ""
        else:
            left_side = " + ".join(values)

        return f"{left_side} = {total}"

    def print_lyre_prompt(
        self,
        omit_phase: t.Optional[bool] = False
    ):

        if not omit_phase:
            phase_prompts = []

            if self.phase() == self.Phase.ORPHEUS:
                phase_prompts = self.orpheus_prompts

            if self.phase() == self.Phase.DEDUCTION:
                phase_prompts = self.deduction_prompts

            print(phase_prompts[self.phase_prompt_idx % len(phase_prompts)])
            self.phase_prompt_idx += 1
            print("-" * self.text_utility.get_term_width())

        lyre_prompt = "Type the name of a note and press Enter to play it. Press X to finish your song."

        print(lyre_prompt)
        print("=" * self.text_utility.get_term_width())

    def read_note(
        self,
        notes: t.List[Note],
        total: int,
        is_eurydices_turn: t.Optional[bool]=False,
        eurydice_sum_len: t.Optional[int]=0,
        warning: t.Optional[str]="",
    ) -> str:
        """
        Keep the repeated interaction small: instead of reprinting the whole
        level header/state after each submitted note, only print the changing
        song line as the next input prompt.

        This is intentionally still input()-based. For a truly static live UI
        where the same terminal row updates in-place while the user types, switch
        this method to a raw-key reader later.
        """
        song_line = self.format_song_line(notes, total, is_eurydices_turn, eurydice_sum_len)
        return input(f"{song_line}\n{warning}\n> ").strip()

    def run(
        self,
        orpheus_tutorial: t.Optional[bool] = False,
        deduction_tutorial: t.Optional[bool] = False,
    ):
        def _accept_notes(
            notes: t.List[Note],
            total: int,
            is_eurydices_turn: t.Optional[bool] = False,
            eurydice_sum_len: t.Optional[int] = 0,
        ) -> t.Tuple[int, int]:
            self.print()
            i = self.read_note(
                notes,
                total,
                bool(is_eurydices_turn),
                eurydice_sum_len,
            )

            while (i.upper() != "X") and (i.upper() != "Q"):
                note = self.level.lyre.get_note(i)
                skip = False
                warning = ""

                try:
                    note = self.level.lyre.play_note(i)
                except Lyre.NoSuchNoteException:
                    warning = "Your lyre has no such string."
                    skip = True
                except Lyre.NoteDepletedException:
                    warning = "You can't play that note anymore."
                    skip = True
                except Lyre.BrokenStringException:
                    self.end_with_broken_string(note)
                    skip = True

                if not skip:
                    notes.append(note)
                    total += note.val

                self.print()
                i = self.read_note(
                    notes,
                    total,
                    bool(is_eurydices_turn),
                    eurydice_sum_len,
                    warning,
                )
            
            if i.upper() == "Q":
                raise TextLevel.QuitGameException()

            return total, len(notes)

        try:  
            # ORPHEUS PHASE      
            if self.debug:
                print("Entering Orpheus phase...")             

            total, _ = _accept_notes([], 0)
            self.level.try_orpheus(total)

            if self.level.state == Level.LevelState.ORPHEUS_FATAL:
                self.end()
                return

            if self.level.state != Level.LevelState.ORPHEUS_SUCCESS:
                print(f"Got unexpected level state {str(self.level.state)}")
                return

            if not self.orpheus_only:
                eurydice_sum_length = self.level.set_eurydice_goal()

                if self.debug:
                    print(f"Set Eurydice's goal to {self.level.eurydice_goal.val} ({eurydice_sum_length} addends)")
                
                while (self.level.state == Level.LevelState.ORPHEUS_SUCCESS) or (
                    self.level.state == Level.LevelState.EURYDICE_FAIL
                ):
                    if self.debug:
                        print(f"Level state is {str(self.level.state)}. Beginning deduction phase.")

                    self.level.back_up_lyre()
                    self.level.back_up_rng()
                    total, num_notes = _accept_notes(
                        [],
                        0,
                        True,
                        eurydice_sum_length,
                    )

                    self.level.check_eurydice(num_notes, total, eurydice_sum_length)

                    if self.level.state == Level.LevelState.EURYDICE_THWARTED:
                        self.text_utility.clear_screen()
                        lines = [
                            self.thwart_line,
                            "The gods mercifully restore your lyre so that you may try again.",
                            "Press <Enter> to continue",
                        ]
                        print(self.text_utility.center_text(lines=lines))

                        if self.debug:
                            print("BEFORE: lives: ", str(self.level.eurydice_lives), " state: ", str(self.level.state))
                        _ = input()
                        self.level.resolve_thwart()
                        continue

                    if self.level.state == Level.LevelState.EURYDICE_FAIL:
                        self.print_fail_msg()
                        continue
            if orpheus_tutorial:
                print(self.text_utility.center_text("Nice work. You're ready for the hard part."))
                _ = input("Press <Enter> to continue.")
                return True
            else:
                self.end()
        except KeyboardInterrupt:
            self.graceful_shutdown()
        except TextLevel.QuitGameException:
            self.graceful_shutdown()