import json
import os
import pathlib
import typing as t

from guiding_eurydice_core.src.level import Goal, Level, Lyre, Note

class TextLevel(Level):
    def __init__(
        self,
        title: t.Optional[str]="",
        lyre: t.Optional[Lyre]=Lyre(),
        orpheus_goal: t.Optional[Goal]=Goal(),
        descriptions: t.Optional[t.List[str]]=[],
        success_text: t.Optional[t.List[str]]=[],
        fail_text: t.Optional[t.List[str]]=[],
        fatal_text: t.Optional[t.List[str]]=[],
        debug: t.Optional[bool]=False,
    ) -> TextLevel:
        self.level = Level()

        self.title = title
        self.descriptions = descriptions
        self.success_text = success_text
        self.fail_text = fail_text
        self.fatal_text = fatal_text
        self.debug = debug

        self.level.lyre = lyre
        self.level.orpheus_goal = orpheus_goal
        self.level.debug = debug

    @staticmethod
    def from_json(
        json_path: pathlib.Path,
        debug: t.Optional[bool]=False,
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
                d : t.Dict[Note, int] = {}
                for item in data["lyre"]:
                    if (isinstance(item, dict)) and ("note" in item.keys()):
                        n = item["note"]

                        if ("name" in n.keys()) and (isinstance(n["name"], str) and ("val" in n.keys()) and (isinstance(n["val"], int))):
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

            return TextLevel(title, lyre, orpheus_goal, descriptions, success_text, fail_text, fatal_text, debug)

    def reset(self):
        self.level.reset()

    def print_header(self):
        header = f"LEVEL {self.level.id}: {self.title.upper()}"

        if self.debug:
            header += f"({str(self.level.get_state())})"

        print()
        print("=" * len(header))
        print(header)
        print("=" * len(header))
        print()
        print(self.level)

    def print_success_msg(self, idx: int):
        while idx >= len(self.success_text):
            idx -= len(self.success_text)
        print(self.success_text[idx])

    def print_fail_msg(self, idx: int):
        while idx >= len(self.fail_text):
            idx -= len(self.fail_text)
        print(self.fail_text[idx])
    
    def print_fatal_msg(self, idx: int):
        while idx >= len(self.fatal_text):
            idx += len(self.fatal_text)
        print(self.fatal_text[idx])

    def print_lyre_prompt(
        self,
        notes: t.List[Note],
        total: int,
        is_eurydices_turn: bool,
        eurydice_sum_len: t.Optional[int],
    ):
        i = 0
        sum_str = ""

        lyre_prompt = "Type the name of a note and press Enter to play it. Press X to finish your song."
        print(lyre_prompt)
        print("-" * len(lyre_prompt))

        if is_eurydices_turn:
            while i < len(notes):
                sum_str += str(notes[i].val) + " + "
                i += 1
            
            while i < eurydice_sum_len:
                sum_str += "_ + "
                i += 1
            
        else:
            while i < len(notes):
                sum_str += str(notes[i].val) + " + "
                i += 1

        sum_str = sum_str[:-3] + " = " + str(total)

        print(sum_str)
    
    def run(self):
        def _end_level():
            def _print_demise_str():
                def _get_len_of_longest_str(arr: t.List[str]) -> int:
                    champ = 0

                    for s in arr:
                        if len(s) > champ:
                            champ = len(s)
                    
                    return champ
                
                def _get_padding(term_width: int, len: int) -> int:
                    padding = int((term_width - len) / 2)
                    if padding < 0:
                        padding = 0
                    return int(padding * 0.75)

                def _get_suffix(s: str, longest_len: int) -> str:
                    spaces = longest_len - len(s)
                    return " " * spaces + " |"


                demise_strs = [
                                    "Because he loved her, he glanced behind him.",
                                    "She instantly fell back. Poor Orpheus",
                                    "stretched out both his arms, trying to hold her",
                                    "and be held. He caught nothing but thin air.",
                                ]

                longest_len = _get_len_of_longest_str(demise_strs)
                term_width = os.get_terminal_size().columns

                
                print()
                
                padding = _get_padding(term_width, longest_len)

                print(
                    " " * padding,
                    "-" * (longest_len + 4),
                )

                for s in demise_strs:
                    res =  "| " + s + _get_suffix(s, longest_len) 
                    print(" " * padding, res, " " * padding)
                
                print(
                    " " * padding,
                    "-" * (longest_len + 4),
                )
                print()
            
            if self.level.state == Level.LevelState.SUCCESS:
                return
            if self.level.state in [Level.LevelState.ORPHEUS_FATAL, Level.LevelState.EURYDICE_FATAL]:
                print("Press any key to look back")
                _ = input()
                _print_demise_str()               

            print("Press X to quit. Press any key to try again.")

            i = input()
            if (i == "X"):
                return
            
            self.reset()
            self.run()

        def _accept_notes(
                notes: t.List[Note],
                total: int,
                is_eurydices_turn: t.Optional[bool]=False,
                eurydice_sum_len: t.Optional[int]=0,

            ) -> int:
            def _cleanup(
                    notes,
                    total,
                    is_eurydices_turn,
                    eurydice_sum_len,
                ):
                self.print_header()
                self.print_lyre_prompt(
                    notes,
                    total,
                    is_eurydices_turn,
                    eurydice_sum_len,
                )
                return input()
            
            if (is_eurydices_turn):
                self.print_lyre_prompt(
                    notes,
                    total,
                    is_eurydices_turn,
                    eurydice_sum_len,
                )
            i = input()
            while(i != "X"):
                note = self.level.lyre.get_note(i)
                skip = False

                try:
                    self.level.lyre.play_note(i)
                except Lyre.NoSuchNoteException:
                    print("Your lyre has no such string.")
                    skip = True
                except Lyre.NoteDepletedException:
                    print("You can't play that note anymore.")
                    skip = True
                
                if not skip:
                    notes.append(note)
                    total += note.val

                i = _cleanup(
                    notes,
                    total,
                    is_eurydices_turn,
                    eurydice_sum_len,
                )
            return total

        success_idx = 0
        fail_idx = 0
        fatal_idx = 0

        self.print_header()

        total = _accept_notes([], 0)
        self.level.try_orpheus(total)

        if self.level.state == Level.LevelState.ORPHEUS_FATAL:
            self.print_fatal_msg(fatal_idx)
            fatal_idx += 1
            _end_level()
            return
        
        if self.level.state != Level.LevelState.ORPHEUS_SUCCESS:
            print(f"Got unexpected level state {str(self.level.state)}")
            return
        
        self.print_success_msg(success_idx)
        success_idx += 1

        eurydice_sum_length = self.level.set_eurydice_goal()

        while (self.level.state == Level.LevelState.ORPHEUS_SUCCESS) or (self.level.state == Level.LevelState.EURYDICE_FAIL):
            self.print_header()
            total = _accept_notes(
                [],
                0,
                True,
                eurydice_sum_length,
                )

            self.level.try_eurydice(total, eurydice_sum_length)

            if self.level.state == Level.LevelState.EURYDICE_FAIL:
                self.print_fail_msg(fail_idx)
                fail_idx += 1
                continue
            else:
                break

        _end_level()          





        
