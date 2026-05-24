# -*- coding: utf-8 -*-

import random
import typing as t

from enum import Enum

from guiding_eurydice_core.src.lyre import Lyre, Note

from src.level import TextLevel
from src._utils import TextUtility, CONTINUE_PROMPT


class LyreHighlightMode(Enum):
    NOTE_NAMES = 0
    NOTE_VALUES = 1
    NOTE_COUNT = 2
    HIGHLIGHT_ALL = 3
    NO_HIGHLIGHT = 4

class SumHighlightMode(Enum):
    SUM = 0
    ADDENDS = 1
    NO_HIGHLIGHT = 2
    HIGHLIGHT_ALL = 3

class TutorialPlayer:
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

    def get_lyre_with_lines(
        self,
        lyre: Lyre,
        lines: t.List[str],
        lyre_highlight_mode: t.Optional[LyreHighlightMode] = LyreHighlightMode.NO_HIGHLIGHT,
        lyre_highlight_color: t.Optional[str] = TextUtility.YELLOW,
    ):
        def _highlight_note(note: Note) -> str:
            term_highlight = TextUtility.RESET if lyre_highlight_mode != LyreHighlightMode.NO_HIGHLIGHT else ""
            if lyre_highlight_mode == LyreHighlightMode.HIGHLIGHT_ALL:
                return lyre_highlight_color + str(note) + term_highlight

            name_str = lyre_highlight_color + "{:<2}".format(note.name) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_NAMES else "{:<2}".format(note.name)
            val_str = lyre_highlight_color + "{:02d}".format(note.val) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_VALUES else "{:02}".format(note.val)
            count_str = lyre_highlight_color + "{:02d}".format(note.count) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_COUNT else "{:02}".format(note.count)

            return f"{name_str} ({val_str}) - {count_str} remaining"
        
        def _highlight_text(text: str) -> str:
            term_highlight = TextUtility.RESET if lyre_highlight_mode != LyreHighlightMode.NO_HIGHLIGHT else ""
            txt_highlight = lyre_highlight_color if lyre_highlight_mode == LyreHighlightMode.HIGHLIGHT_ALL else ""
            return txt_highlight + text + term_highlight
        
        res = ""
        i = 0
        note_len = 0

        while i < len(lyre.notes) and i < len(lines):
            if note_len == 0:
                note_len = len(str(lyre.notes[i]))

            highlighted_note = _highlight_note(lyre.notes[i])
            res += highlighted_note + " " + TextUtility.magenta("|") + " " + _highlight_text(lines[i]) + "\n"
            i += 1
        
        if i < len(lyre.notes):
            while i < len(lyre.notes):
                highlighted_note = _highlight_note(lyre.notes[i])
                res += highlighted_note + " " + TextUtility.magenta("|") + "\n"
                i += 1
        
        if i < len(lines):
            while i < len(lines):
                res += (" " * note_len) + " " + TextUtility.magenta("|") + " " + _highlight_text(lines[i]) + "\n"
                i += 1
                
        return res
    
    def get_requirement(
        self,
        level: TextLevel,
    ):
        curr_phase = level.phase()
        requirement_line = ""

        if curr_phase == level.Phase.ORPHEUS:
            requirement_line += "You" 
        elif curr_phase == level.Phase.DEDUCTION:
            requirement_line += level.challenge_name
        
        requirement_line += " "
        requirement_verb = level.REQUIREMENT_VERBS[level.requirement_verb_idx % len(level.REQUIREMENT_VERBS)]

        if (curr_phase == level.Phase.DEDUCTION and level.challenge_number > 1) \
            or (curr_phase == level.Phase.ORPHEUS):
            requirement_line += requirement_verb.plur()
        else:
            requirement_line += requirement_verb.sing()

        requirement_line += ": "
        
        if curr_phase == level.Phase.ORPHEUS:
            requirement_line += str(level.level.orpheus_goal.val)
        elif curr_phase == level.Phase.DEDUCTION:
            requirement_line += "?"
        
        return requirement_line
    
    def print_requirement(
        self,
        level: TextLevel, 
        requirement_line: str,
        highlight_color: t.Optional[str] = "",
    ):
        highlight_term = "\x1b[0m" if len(highlight_color) > 0 else ""
        print(highlight_color + requirement_line + highlight_term)
        level.requirement_verb_idx += 1

    def print_mock_sum(
        self,
        highlight_color: t.Optional[str] = "",
        highlight_mode: t.Optional[SumHighlightMode] = SumHighlightMode.NO_HIGHLIGHT,
        phase: t.Optional[TextLevel.Phase] = TextLevel.Phase.ORPHEUS,
        level: t.Optional[TextLevel] = None,

    ):
        def _highlight(sum: str) -> str:
            if len(highlight_color) > 0:
                highlight_term = "\x1b[0m" 

                split_sum = sum.split("=")

                if len(split_sum) != 2:
                    raise ValueError("Got more than one substring when splitting sum string on '='")
                
                if highlight_mode == SumHighlightMode.HIGHLIGHT_ALL:
                    return highlight_color + sum + highlight_term
                elif highlight_mode == SumHighlightMode.SUM:
                    return split_sum[0] + " = " + highlight_color + split_sum[1] + highlight_term
                elif highlight_mode == SumHighlightMode.ADDENDS:
                    return highlight_color + split_sum[0] + highlight_term + " = " + split_sum[1]
            
            return sum

        mock_sum = "= 0" if phase == TextLevel.Phase.ORPHEUS else level.format_song_line([], 0)
        print(_highlight(mock_sum))

    def play_intro(self):
        try:
            initial_wedding_lines = [ 
                "From Crete, Hymen, dressed in yellow garments,",
                "flew through vast expanses of the air",
                "and moved to regions of the Cicones,",
                "summoned there by the voice of Orpheus.",
            ]

            hymen_wedding_lines_top = [
                "From Crete, " + TextUtility.yellow("Hymen") + ", dressed in yellow garments,",
                "flew through vast expanses of the air",
                "and moved to regions of the Cicones,",
                "summoned there by the voice of Orpheus.",
            ]
            
            hymen_wedding_lines_bottom = [
                TextUtility.yellow("Hymen is the god of marriage.")
            ]

            orpheus_wedding_lines_top = [
                "From Crete, Hymen, dressed in yellow garments,",
                "flew through vast expanses of the air",
                "and moved to regions of the Cicones,",
                "summoned there by the voice of " + TextUtility.blue("Orpheus") + ".", 
            ]

            orpheus_wedding_lines_bottom = [
                TextUtility.blue("That's you. You are from Thrace."),
                TextUtility.blue("Your father is Apollo, the god of music and poetry."),
                TextUtility.blue("Your mother is Calliope, one of the nine muses."),
            ]

            failed_torch_lines = [
                "His trip was futile. Although he did attend",
                TextUtility.blue("Orpheus") + "'s wedding, he did not speak",
                "his usual words, or have a joyful face,",
                "or bring good luck. Even the torch he held",
                "spluttered with smoke, making his eyes water,",
                "and waving it around produced no flames."
            ]

            death_lines = [
                "What happened afterwards was even worse",
                "than any omen, for " + TextUtility.green("Eurydice"),
                "Orpheus's new bride, while wandering",
                "through a meadow with a crowd of naiads,",
                "was bitten on the ankle by a snake.",
            ]

            death_line = TextUtility.red("She collapsed and died.")

            mourning_lines = [
                TextUtility.blue("The Thracian poet") + ",",
                "after he had had enough of mourning",
                "in the upper world, dared to travel down",
                "the Taenarian gate to the river Styx,",
                "to see if he could win the sympathy",
                "of dead shades below.",
            ]    

            self.text_utility.prose_screen(initial_wedding_lines)

            self.text_utility.prose_screen(
                hymen_wedding_lines_top,
                hymen_wedding_lines_bottom,
            )

            self.text_utility.prose_screen(
                orpheus_wedding_lines_top,
                orpheus_wedding_lines_bottom,
            )

            self.text_utility.prose_screen(failed_torch_lines)

            self.text_utility.prose_screen(death_lines)

            self.text_utility.prose_screen([death_line])

            self.text_utility.prose_screen(mourning_lines)
        except KeyboardInterrupt:
            lvl = TextLevel()
            lvl.graceful_shutdown()

    def play_orpheus_tutorial(
        self,
        level: TextLevel
    ):
        level_lines = [
            "You will need to pass through many obstacles and foes to rescue your wife.",
            "Each encounter will look like this..."
        ]

        lyre_lines = [
            "This is your lyre. It is the only weapon you have.",
            "Each line represents a note you can play.",
            "",
            "Your first song of each level will always be to calm",
            "and reassure yourself."
        ]

        note_name_lines = [
            "Each note has a " + TextUtility.yellow("name") + ".",
            "To play a note, enter its " + TextUtility.yellow("name") + ".",
            "Take care: if you attempt to play a",
            "nonexistent note, you could " + TextUtility.red("break a string") + ".",
        ]

        note_value_lines = [
            "Each note also has a " + TextUtility.yellow("value") + ".",
            "When you play a note, its " + TextUtility.yellow("value") + " will be added to your ",
            TextUtility.blue("melody") + ".",
        ]

        note_remaining_lines = [
            "Each note also has a " + TextUtility.yellow("limit") + " on how many times it",
            "can be played. If you try to play an exhausted note",
            "too many times, you could " + TextUtility.red("break a string") + ".",
        ]

        target_value_lines = [
            "You want to play notes that add up to the " + TextUtility.blue("song you"),
            "You can play as many notes as you like",
            "to reach the " + TextUtility.blue("song") + ". Just make sure not to",
            "overplay " + TextUtility.red("exhausted") + " notes.",
        ]

        finishing_lines = [
            "Once you are satisfied with your song and",
            "would like to finish playing, press X and ",
            "then <Enter>.",
            "",
            "Give it a try!"
        ]

        try:
            self.text_utility.clear_screen()
            lvl_text = self.text_utility.center_text(lines=level_lines)
            print(lvl_text)
            self.text_utility.pad_and_continue(lvl_text.split("\n"))

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                lyre_lines,
                LyreHighlightMode.HIGHLIGHT_ALL,
                lyre_highlight_color=TextUtility.YELLOW
                ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                note_name_lines,
                LyreHighlightMode.NOTE_NAMES,
                lyre_highlight_color=TextUtility.YELLOW
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()
            
            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                note_value_lines,
                LyreHighlightMode.NOTE_VALUES,
                lyre_highlight_color=TextUtility.YELLOW
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum(
                highlight_color="\x1b[34m",
                highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                note_remaining_lines,
                LyreHighlightMode.NOTE_COUNT,
                lyre_highlight_color=TextUtility.YELLOW
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            req_line = self.get_requirement(level)
            line_to_add =     TextUtility.blue("need") + ", shown after the line \"" + TextUtility.cyan(req_line.split(":")[0]) + "\"."
            target_value_lines.insert(1, line_to_add)
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                target_value_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color=""
            ))
            print("=" * self.text_utility.get_term_width())
            print(TextUtility.cyan(req_line.split(":")[0]) + ":" + TextUtility.blue(req_line.split(":")[1]))
            self.print_mock_sum(
                highlight_color="",
                highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                finishing_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum(
                highlight_color="",
                highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
            )
            self.text_utility.wait_for_enter()

            return level.run(tutorial_phase=TextLevel.TutorialPhase.ORPHEUS_ONLY)
        except KeyboardInterrupt:
            level.graceful_shutdown()

    def play_eurydice_tutorial(self, level: TextLevel):
        res = False

        try:
            res = level.run(tutorial_phase=TextLevel.TutorialPhase.DEDUCTION_START)
        except KeyboardInterrupt:
            level.graceful_shutdown()

        if not res:
            return

        deduction_tutorial_lines = [
            "You aren't the only one who is moved by your music.",
            "It has a tremendous power to persuade those around you.",
            f"Try and use it now to ask {TextUtility.cyan(level.challenge_name)}",
            "to help you."
        ]

        deduction_sum_lines = [
            "You will play your lyre as before, but this time,",
            "the " + TextUtility.blue("desired song") + " is a mystery."
        ]

        deduction_addend_lines = [
            "However, you do know " + TextUtility.blue("how many notes"),
            f"{TextUtility.cyan(level.challenge_name)} wants to hear. Make sure your song",
            "includes that many notes before you finish playing."
        ]

        deduction_fail_lines = [
            "you will have more than one chance to play.",
            "Don't fail too many times, or else you will ",
            TextUtility.red("run out of chances") + ".",
        ]

        deduction_deduce_lines = [
            "It's important to pay attention to the songs",
            "that " + TextUtility.red("fail") + " because that information can help you deduce",
            "the song that will " + TextUtility.green("succeed") + "."
        ]

        thwart_lines = [
            "Sometimes, in the course of playing an incorrect song",
            "you will " + TextUtility.red("exhaust") + " a note needed "
            "for the correct song.",
            "",
            "In that case, the gods will have mercy on you and",
            TextUtility.green("restore") + " the notes you need on your lyre. You will",
            "be notified when this happens.",
            "",
            "This information can also be used to deduce the ",
            "song that " + TextUtility.cyan(level.challenge_name) + " wants to hear."
        ]

        try_lines = [
            "It may take some time to get a feel for this part",
            "of your journey.",
            "",
            "Give it a try!"
        ]

        try:
            self.text_utility.clear_screen()
            ded_text = self.text_utility.center_text(lines=deduction_tutorial_lines)
            print(ded_text)
            self.text_utility.pad_and_continue(ded_text.split("\n"))

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                deduction_sum_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            req_lines = self.get_requirement(level).split(" ")
            req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines) - 1]) + " " + TextUtility.blue(req_lines[len(req_lines) - 1])
            print(req_line)
            self.print_mock_sum(
                highlight_color="",
                highlight_mode=SumHighlightMode.SUM,
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                deduction_addend_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            req_lines = self.get_requirement(level).split(" ")
            req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines)])
            print(req_line)
            self.print_mock_sum(
                highlight_color=TextUtility.BLUE,
                highlight_mode=SumHighlightMode.ADDENDS,
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            req_line = self.get_requirement(level)
            line_to_add = "Because you don't know the " + TextUtility.blue("song") + f" {TextUtility.cyan(req_line.split(":")[0])}, "
            deduction_fail_lines.insert(0, line_to_add)
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                deduction_fail_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            req_lines = self.get_requirement(level).split(" ")
            req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines) - 1]) + " " + TextUtility.blue(req_lines[len(req_lines) - 1])
            print(req_line)
            self.print_mock_sum(
                highlight_color="",
                highlight_mode=SumHighlightMode.SUM,
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                deduction_deduce_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum(
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                thwart_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            req_lines = self.get_requirement(level).split(" ")
            req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines)])
            print(req_line)
            self.print_mock_sum(
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                try_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            print("=" * self.text_utility.get_term_width())
            level.print_requirement()
            self.print_mock_sum(
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            return level.run(tutorial_phase=TextLevel.TutorialPhase.DEDUCTION_END)
        except KeyboardInterrupt:
            level.graceful_shutdown()

    def play_tutorial(
            self,
            level: TextLevel,
            tutorial_phase: TextLevel.TutorialPhase,
        ) -> bool:
        if tutorial_phase == TextLevel.TutorialPhase.NO_TUT:
            return
        elif tutorial_phase == TextLevel.TutorialPhase.ORPHEUS_ONLY:
            return self.play_orpheus_tutorial(level)
        elif tutorial_phase == TextLevel.TutorialPhase.DEDUCTION_START:
            return self.play_eurydice_tutorial(level)




