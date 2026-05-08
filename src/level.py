from __future__ import annotations

import json
import os
import pathlib
import time
import typing as t

from guiding_eurydice_core.src.level import Goal, Level, Lyre, Note


class TextLevel(Level):
    def __init__(
        self,
        title: t.Optional[str] = "",
        lyre: t.Optional[Lyre] = None,
        orpheus_goal: t.Optional[Goal] = None,
        descriptions: t.Optional[t.List[str]] = None,
        success_text: t.Optional[t.List[str]] = None,
        fail_text: t.Optional[t.List[str]] = None,
        fatal_text: t.Optional[t.List[str]] = None,
        debug: t.Optional[bool] = False,
    ) -> None:
        self.level = Level()

        self.title = title or ""
        self.descriptions = descriptions or []
        self.success_text = success_text or []
        self.fail_text = fail_text or []
        self.fatal_text = fatal_text or []
        self.debug = bool(debug)

        self.level.lyre = lyre or Lyre()
        self.level.orpheus_goal = orpheus_goal or Goal()
        self.level.debug = self.debug

        self.success_idx = 0
        self.fail_idx = 0
        self.fatal_idx = 0

    @staticmethod
    def from_json(
        json_path: pathlib.Path,
        debug: t.Optional[bool] = False,
    ) -> TextLevel:
        title = None
        lyre = None
        orpheus_goal = None
        descriptions = None
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

            if ("descriptions" in data.keys()) and (isinstance(data["descriptions"], list)):
                descriptions = data["descriptions"]

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
                descriptions,
                success_text,
                fail_text,
                fatal_text,
                debug,
            )

    def reset(self):
        self.level.reset()

    @staticmethod
    def _get_term_width() -> int:
                return os.get_terminal_size().columns

    @staticmethod      
    def _get_term_height() -> int:
        return os.get_terminal_size().lines
    
    @staticmethod
    def _get_horizontal_padding(term_width: int, s: str) -> int:
        padding = int((term_width - len(s)) / 2)
        if padding < 0:
            padding = 0
        return int(padding * 0.9)
    
    @staticmethod
    def _get_vertical_padding(
            term_height: int,
            lines: t.List[str],
            num_extra_lines: t.Optional[int]=0
        ) -> int:
        actual_lines = num_extra_lines

        for line in lines:
            if len(line) > TextLevel._get_term_width():
                actual_lines += 2
            else:
                actual_lines += 1
        
        padding = int((term_height - actual_lines) / 2)
        if padding < 0:
            padding = 0

        return padding

    @staticmethod
    def get_longest_str(arr: t.List[str]) -> str:
        champ_i = 0
        champ_s = ""

        for s in arr:
            if len(s) > champ_i:
                champ_i = len(s)
                champ_s = s

        return champ_s

    @staticmethod
    def clear_screen():
        # ANSI clear screen + move cursor home. Works in modern Windows Terminal,
        # PowerShell, Git Bash, macOS Terminal, and most Linux terminals.
        print("\033[2J\033[H", end="")

    @staticmethod
    def clear_lines(n: int):
      for _ in range(n):
        print("\033[F\033[K", end="")

    @staticmethod
    def flash_msg(msg: str, time_in_s: float, iterations: int):
        for _ in range(iterations):
            TextLevel.clear_screen()
            print()
            time.sleep(time_in_s)
            print(msg)
            time.sleep(time_in_s)

    def print_header(self):
        header = f"LEVEL {self.level.id}: {self.title.upper()}"

        if self.debug:
            header += f" ({str(self.level.get_state())})"

        print()
        print("=" * len(header))
        print(header)
        print("=" * len(header))
        print()
        print(self.level)

    def print_success_msg(self, idx: int):
        if not self.success_text:
            return
        print(self.success_text[idx % len(self.success_text)])

    def print_fail_msg(self, idx: int):
        if not self.fail_text:
            return
        print(self.fail_text[idx % len(self.fail_text)])

    def print_fatal_msg(self, idx: int, linger_time_s: t.Optional[int]=3):
        TextLevel.clear_screen()
        fatal_msg = self.fatal_text[idx % len(self.fatal_text)]
        horizontal_padding = TextLevel._get_horizontal_padding(TextLevel._get_term_width(), fatal_msg)
        vertical_padding = TextLevel._get_vertical_padding(TextLevel._get_term_height(), [fatal_msg])

        print(
            "\n" * vertical_padding,
            " " * horizontal_padding,
            fatal_msg,
            " " * horizontal_padding,
            "\n" * vertical_padding)
        time.sleep(linger_time_s)

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
            left_side = "_"
        else:
            left_side = " + ".join(values)

        return f"{left_side} = {total}"

    def print_lyre_prompt(self):
        print()

        lyre_prompts = ["Type the name of a note and press Enter to play it.", "Press X to finish your song."]
        longest_str = TextLevel.get_longest_str(lyre_prompts)

        for prompt in lyre_prompts:
            print(prompt)

        print("-" * len(longest_str))

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
        def _end_level():            
            def _force_look_back():
                demand = "Press any key to look back".upper()
                horizontal_padding = TextLevel._get_horizontal_padding(TextLevel._get_term_width(), demand) 
                vertical_padding = TextLevel._get_vertical_padding(TextLevel._get_term_height(), [demand])
                TextLevel.flash_msg(("\n" * vertical_padding) + (">" * horizontal_padding) + demand + ("<" * horizontal_padding) + ("\n" * vertical_padding), 1, 3)
                _ = input()
                TextLevel.clear_screen()
                _print_demise_str()
                time.sleep(3)
            
            def _print_demise_str():
                def _get_suffix(s: str, longest_str: str) -> str:
                    spaces = len(longest_str) - len(s)
                    return " " * spaces + " |"

                demise_strs = [
                    "Because he loved her, he glanced behind him.",
                    "She instantly fell back. Poor Orpheus",
                    "stretched out both his arms, trying to hold her",
                    "and be held. He caught nothing but thin air.",
                ]

                longest_str = TextLevel.get_longest_str(demise_strs)

                print()

                horizontal_padding = TextLevel._get_horizontal_padding(TextLevel._get_term_width(), longest_str) - 1
                vertical_padding = TextLevel._get_vertical_padding(TextLevel._get_term_height(), demise_strs, 2)

                print(
                    "\n" * vertical_padding,
                    " " * (horizontal_padding - 1),
                    "-" * (len(longest_str) + 4),
                )

                for s in demise_strs:
                    res = "| " + s + _get_suffix(s, longest_str)
                    print(" " * horizontal_padding, res, " " * horizontal_padding)

                print(
                    " " * horizontal_padding,
                    "-" * (len(longest_str) + 4),
                    "\n" * vertical_padding
                )
                print()

            if self.level.state == Level.LevelState.SUCCESS:
                return
            
            if self.level.state == Level.LevelState.ORPHEUS_FATAL:
                self.print_fatal_msg(self.fatal_idx)
                self.fatal_idx += 1
                _force_look_back()
            elif self.level.state == Level.LevelState.EURYDICE_FATAL:
                print("Eurydice is lost.")
                _force_look_back()

            print("Press X to quit. Press any key to try again.")

            i = input().strip()
            if i.upper() == "X":
                return

            self.reset()
            self.run()

        def _accept_notes(
            notes: t.List[Note],
            total: int,
            is_eurydices_turn: t.Optional[bool] = False,
            eurydice_sum_len: t.Optional[int] = 0,
        ) -> int:
            TextLevel.clear_screen()
            self.print_header()
            self.print_lyre_prompt()
            i = self.read_note(
                notes,
                total,
                bool(is_eurydices_turn),
                eurydice_sum_len,
            )
        
            while i.upper() != "X":
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

                TextLevel.clear_screen()
                self.print_header()
                self.print_lyre_prompt()
                i = self.read_note(
                    notes,
                    total,
                    bool(is_eurydices_turn),
                    eurydice_sum_len,
                    warning,
                )

            return total

        TextLevel.clear_screen()
        self.print_header()
        self.print_lyre_prompt()
      
        total = _accept_notes([], 0)
        self.level.try_orpheus(total)

        if self.level.state == Level.LevelState.ORPHEUS_FATAL:
            _end_level()
            return

        if self.level.state != Level.LevelState.ORPHEUS_SUCCESS:
            print(f"Got unexpected level state {str(self.level.state)}")
            return

        self.print_success_msg(self.success_idx)
        self.success_idx += 1

        eurydice_sum_length = self.level.set_eurydice_goal()

        while (self.level.state == Level.LevelState.ORPHEUS_SUCCESS) or (
            self.level.state == Level.LevelState.EURYDICE_FAIL
        ):
            print()
            self.print_lyre_prompt()
            total = _accept_notes(
                [],
                0,
                True,
                eurydice_sum_length,
            )

            self.level.try_eurydice(total, eurydice_sum_length)

            if self.level.state == Level.LevelState.EURYDICE_FAIL:
                self.print_fail_msg(self.fail_idx)
                self.fail_idx += 1
                continue
            else:
                break

        _end_level()
