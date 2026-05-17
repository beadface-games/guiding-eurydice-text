from __future__ import annotations

import json
import pathlib
import time
import typing as t

from guiding_eurydice_core.src.lyre import Lyre, Note
from guiding_eurydice_core.src.level import Goal, Level
from src._utils import TextUtility

class TextLevel(Level):
    class QuitGameException(Exception):
        pass

    def __init__(
        self,
        title: t.Optional[str] = "",
        lyre: t.Optional[Lyre] = None,
        orpheus_goal: t.Optional[Goal] = None,
        orpheus_only: t.Optional[bool] = False,
        descriptions: t.Optional[t.List[str]] = None,
        orpheus_prompts: t.Optional[t.List[str]] = None,
        deduction_prompts: t.Optional[t.List[str]] = None,
        success_text: t.Optional[t.List[str]] = None,
        fail_text: t.Optional[t.List[str]] = None,
        fatal_text: t.Optional[t.List[str]] = None,
        debug: t.Optional[bool] = False,
        given_seed: t.Optional[int] = None,
    ) -> None:
        self.title = title or ""
        self.descriptions = descriptions or []
        self.deduction_prompts = deduction_prompts or []
        self.orpheus_prompts = orpheus_prompts or []
        self.success_text = success_text or []
        self.fail_text = fail_text or []
        self.fatal_text = fatal_text or []

        l = lyre or Lyre()
        og = orpheus_goal or Goal()

        self.orpheus_only = orpheus_only

        self.description_idx = 0
        self.phase_prompt_idx = 0
        self.fail_idx = 0
        self.fatal_idx = 0

        self.debug = debug
        db = self.debug  

        self.level = Level(
            l,
            og,
            db,
            given_seed,
        )   

        self.text_utility = TextUtility(rng=self.level.rng)

    @staticmethod
    def from_json(
        json_path: pathlib.Path,
        debug: t.Optional[bool] = False,
        seed: t.Optional[int] = None,
    ) -> TextLevel:
        title = None
        lyre = None
        orpheus_goal = None
        orpheus_only = False
        descriptions = None
        orpheus_prompts = None
        deduction_prompts = None
        success_text = None
        fail_text = None
        fatal_text = None

        with open(json_path, "r") as f:
            data = json.load(f)

            if ("title" in data.keys()) and (isinstance(data["title"], str)):
                title = data["title"]

            if ("lyre" in data.keys()) and (isinstance(data["lyre"], list)):
                d: t.Dict[Note, int] = {}
                for item in data["lyre"]:
                    if (isinstance(item, dict)) and ("note" in item.keys()):
                        n = item["note"]

                        if (
                            "name" in n.keys()
                            and isinstance(n["name"], str)
                            and "val" in n.keys()
                            and isinstance(n["val"], int)
                        ):
                            note = Note(name=n["name"], val=n["val"])
                            d[note] = item["count"] if "count" in item.keys() else 1

                lyre = Lyre(d)

            if ("orpheus_goal" in data.keys()) and (isinstance(data["orpheus_goal"], int)):
                orpheus_goal = Goal(data["orpheus_goal"])

            if ("orpheus_only" in data.keys()) and (isinstance(data["orpheus_only"], bool)):
                orpheus_only = data["orpheus_only"]

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
                title,
                lyre,
                orpheus_goal,
                orpheus_only,
                descriptions,
                orpheus_prompts,
                deduction_prompts,
                success_text,
                fail_text,
                fatal_text,
                debug,
                seed,
            )

    def reset(self):
        self.level.reset()

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

            if self.level.state == Level.LevelState.SUCCESS:
                return
            
            if self.level.state == Level.LevelState.ORPHEUS_FATAL:
                self.print_fatal_msg()
                self.fatal_idx += 1
                _force_look_back()
            elif self.level.state == Level.LevelState.EURYDICE_FATAL:
                print("Eurydice is lost.")
                _force_look_back()

            print("Press Q to quit. Press any other key to try again.")

            i = input().strip()
            if i.upper() == "Q":
                return

            self.reset()
            self.run()

    def print_header(self):
        title_line = f"LEVEL {self.level.id}: {self.title.upper()} - seed={str(self.level.seed)} (Q to Quit)"
        description = self.descriptions[self.description_idx % len(self.descriptions)]

        if self.debug:
            title_line += f" ({str(self.level.get_state())})"

        print()
        term_width = self.text_utility.get_term_width()
        print("=" * term_width)
        print(
            " " * self.text_utility.get_horizontal_padding(term_width, title_line),
            title_line,
            " " * self.text_utility.get_horizontal_padding(term_width, title_line),
        )
        print("=" * term_width)
        print(
            " " * self.text_utility.get_horizontal_padding(term_width, description),
            description,
            " " * self.text_utility.get_horizontal_padding(term_width, description),
        )
        print("-" * term_width)
        print()
        print(self.level)

        self.description_idx += 1

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

    def print_lyre_prompt(self):
        print()

        phase_prompts = []

        if self.orpheus_only or \
            (self.level.state == self.level.LevelState.READY):
            phase_prompts = self.orpheus_prompts

        if (self.level.state == self.level.LevelState.ORPHEUS_SUCCESS) or \
            (self.level.state == self.level.LevelState.EURYDICE_FAIL) or \
            (self.level.state == self.level.LevelState.EURYDICE_THWARTED):
            phase_prompts = self.deduction_prompts

        lyre_prompts = [
            "Type the name of a note and press Enter to play it.",
            "Press X to finish your song.",
        ]

        print(phase_prompts[self.phase_prompt_idx % len(phase_prompts)])
        self.phase_prompt_idx += 1
        print("-" * len(self.text_utility.get_term_width()))

        for prompt in lyre_prompts:
            print(prompt)

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

    def run(self):
        def _graceful_shutdown():
            self.text_utility.clear_screen()
            self.text_utility.fade_msg(
                    "Your song dwindles into nothingness...",
                    1000,
                    4,
                    min_time_in_ms_per_it=250,
                )
            time.sleep(1)
            raise SystemExit(0)

        def _accept_notes(
            notes: t.List[Note],
            total: int,
            is_eurydices_turn: t.Optional[bool] = False,
            eurydice_sum_len: t.Optional[int] = 0,
        ) -> t.Tuple[int, int]:
            self.text_utility.clear_screen()
            self.print_header()
            self.print_lyre_prompt()
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
                    self.level.lyre.play_note(i)
                except Lyre.NoSuchNoteException:
                    warning = "Your lyre has no such string."
                    skip = True
                except Lyre.NoteDepletedException:
                    warning = "You can't play that note anymore."
                    skip = True

                if not skip:
                    notes.append(note)
                    total += note.val

                self.text_utility.clear_screen()
                self.print_header()
                self.print_lyre_prompt()
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
            self.print_header()
            self.print_lyre_prompt()
        
            total, _ = _accept_notes([], 0)
            self.level.try_orpheus(total)

            if self.level.state == Level.LevelState.ORPHEUS_FATAL:
                _end_level()
                return

            if self.level.state != Level.LevelState.ORPHEUS_SUCCESS:
                print(f"Got unexpected level state {str(self.level.state)}")
                return

            self.print_success_msg()

            if not self.orpheus_only:
                eurydice_sum_length = self.level.set_eurydice_goal()
                
                while (self.level.state == Level.LevelState.ORPHEUS_SUCCESS) or (
                    self.level.state == Level.LevelState.EURYDICE_FAIL
                ):
                    self.level.back_up_lyre()
                    self.level.back_up_rng()
                    print()
                    self.print_lyre_prompt()
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
                            "In your attempts to guide her, you have left Eurydice with no path forward.",
                            "The gods mercifully restore your lyre so that you may try again.",
                            "Press any key to continue",
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

                _end_level()
        except KeyboardInterrupt:
            _graceful_shutdown()
        except TextLevel.QuitGameException:
            _graceful_shutdown()