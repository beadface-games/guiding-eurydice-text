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
        lyre_highlight_color: t.Optional[str] = "\x1b[33m",
    ):
        def _highlight_note(note: Note) -> str:
            term_highlight = "" if lyre_highlight_mode == LyreHighlightMode.NO_HIGHLIGHT else "\x1b[0m"
            if lyre_highlight_mode == LyreHighlightMode.HIGHLIGHT_ALL:
                return lyre_highlight_color + str(note) + term_highlight

            name_str = lyre_highlight_color + "{:<2}".format(note.name) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_NAMES else "{:<2}".format(note.name)
            val_str = lyre_highlight_color + "{:02d}".format(note.val) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_VALUES else "{:02}".format(note.val)
            count_str = lyre_highlight_color + "{:02d}".format(note.count) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_COUNT else "{:02}".format(note.count)

            return f"{name_str} ({val_str}) - {count_str} remaining"
        
        def _highlight_text(text: str) -> str:
            term_highlight = "\x1b[0m" if lyre_highlight_mode == LyreHighlightMode.HIGHLIGHT_ALL else ""
            txt_highlight = lyre_highlight_color if lyre_highlight_mode == LyreHighlightMode.HIGHLIGHT_ALL else ""
            return txt_highlight + text + term_highlight
        
        res = ""
        i = 0
        note_len = 0

        while i < len(lyre.notes) and i < len(lines):
            if note_len == 0:
                note_len = len(str(lyre.notes[i]))

            highlighted_note = _highlight_note(lyre.notes[i])
            res += highlighted_note + " \x1b[35m|\x1b[0m " + _highlight_text(lines[i]) + "\n"
            i += 1
        
        if i < len(lyre.notes):
            while i < len(lyre.notes):
                highlighted_note = _highlight_note(lyre.notes[i])
                res += highlighted_note + " \x1b[35m|\x1b[0m\n"
                i += 1
        
        if i < len(lines):
            while i < len(lines):
                res += (" " * note_len) + " \x1b[35m|\x1b[0m " + _highlight_text(lines[i]) + "\n"
                i += 1
                
        return res
    
    def get_requirement(
        self,
        level: TextLevel,
    ):
        curr_phase = level.phase()
        requirement_line = ""

        if curr_phase == level.Phase.ORPHEUS:
            requirement_line += "Orpheus" 
        elif curr_phase == level.Phase.DEDUCTION:
            requirement_line += level.challenge_name
        
        requirement_line += " "
        requirement_verb = level.REQUIREMENT_VERBS[level.requirement_verb_idx % len(level.REQUIREMENT_VERBS)]

        if curr_phase == level.Phase.DEDUCTION and level.challenge_number > 1:
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
                "From Crete, \x1b[33mHymen\x1b[0m, dressed in yellow garments,",
                "flew through vast expanses of the air",
                "and moved to regions of the Cicones,",
                "summoned there by the voice of Orpheus.",
            ]
            
            hymen_wedding_lines_bottom = [
                "\x1b[33mHymen is the god of marriage.\x1b[0m"
            ]

            orpheus_wedding_lines_top = [
                "From Crete, Hymen, dressed in yellow garments,",
                "flew through vast expanses of the air",
                "and moved to regions of the Cicones,",
                "summoned there by the voice of \x1b[34mOrpheus\x1b[0m.", 
            ]

            orpheus_wedding_lines_bottom = [
                "\x1b[34mThat's you. You are from Thrace.\x1b[0m",
                "\x1b[34mYour father is Apollo, the god of music and poetry.\x1b[0m",
                "\x1b[34mYour mother is Calliope, one of the nine muses.\x1b[0m",
            ]

            failed_torch_lines = [
                "His trip was futile. Although he did attend",
                "\x1b[34mOrpheus\x1b[0m's wedding, he did not speak",
                "his usual words, or have a joyful face,",
                "or bring good luck. Even the torch he held",
                "spluttered with smoke, making his eyes water,",
                "and waving it around produced no flames."
            ]

            death_lines = [
                "What happened afterwards was even worse",
                "than any omen, for \x1b[32mEurydice\x1b[0m,",
                "Orpheus's new bride, while wandering",
                "through a meadow with a crowd of naiads,",
                "was bitten on the ankle by a snake.",
            ]

            death_line = "\x1b[31mShe collapsed and died.\x1b[0m"

            mourning_lines = [
                "\x1b[34mThe Thracian poet\x1b[0m,",
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
            "Each encounter will look like this."
        ]

        lyre_lines = [
            "This is your lyre. It is the only weapon you have.",
            "Each line represents a note you can play.",
            "",
            "Your first song of each level will always be to calm",
            "and reassure yourself."
        ]

        note_name_lines = [
            "Each note has a \x1b[33mname\x1b[0m.",
            "To play a note, you type the note's \x1b[33mname\x1b[0m",
            "and then press <Enter>.",
            "Careful when you type—if you type a nonexistent",
            "note's \x1b[33mname\x1b[0m too many times, you could ",
            "\x1b[31mbreak a string\x1b[0m.",
            "",
            "How many times is too many? You won't know",
            "until \x1b[31mit's too late\x1b[0m."
        ]

        note_value_lines = [
            "Each note also has a \x1b[33mvalue\x1b[0m.",
            "When you play a note by entering its name,",
            "the \x1b[33mvalue\x1b[0m will be added to a \x1b[34mrunning sum\x1b[0m",
            "displayed at the bottom of your screen.",
        ]

        note_remaining_lines = [
            "Each note also has a \x1b[33mlimit\x1b[0m on how many times you",
            "may play it. If you try to play an exhausted note",
            "too many times, you could \x1b[31mbreak a string\x1b[0m.",
            "",
            "How many times is too many? You won't know until",
            "\x1b[31mit's too late\x1b[0m."
        ]

        target_value_lines = [
            "You want to play notes that add up to the \x1b[34mtarget sum\x1b[0m",
            "You can play as many notes as you like",
            "to reach the \x1b[34msum\x1b[0m. Just make sure not to",
            "overplay \x1b[31mexhausted\x1b[0m notes.",
            "Your \x1b[34mtotal\x1b[0m will be shown at the bottom of the screen."
        ]

        finishing_lines = [
            "Once you are satisfied with your song and",
            "would like to submit it (hopefully once you've",
            "reached the \x1b[34mtarget sum\x1b[0m),",
            "press X and then <Enter> to finish playing.",
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
                lyre_highlight_color="\x1b[33m"
                ))
            level.print_lyre_prompt(omit_phase=True)
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                note_name_lines,
                LyreHighlightMode.NOTE_NAMES,
                lyre_highlight_color="\x1b[33m"
            ))
            level.print_lyre_prompt(omit_phase=True)
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()
            
            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                note_value_lines,
                LyreHighlightMode.NOTE_VALUES,
                lyre_highlight_color="\x1b[33m"
            ))
            level.print_lyre_prompt(omit_phase=True)
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
                lyre_highlight_color="\x1b[33m"
            ))
            level.print_lyre_prompt(omit_phase=True)
            level.print_requirement()
            self.print_mock_sum()
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header(omit_description=True)
            req_line = self.get_requirement(level)
            line_to_add = f"shown after the line \"\x1b[36m{req_line.split(":")[0]}\x1b[0m\"."
            target_value_lines.insert(1, line_to_add)
            print(self.get_lyre_with_lines(
                level.level.lyre,
                target_value_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color=""
            ))
            level.print_lyre_prompt(omit_phase=True)
            self.print_requirement(level, req_line, highlight_color="\x1b[36m")
            self.print_mock_sum(
                highlight_color="\x1b[34m",
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
            level.print_lyre_prompt(omit_phase=True)
            level.print_requirement()
            self.print_mock_sum(
                highlight_color="\x1b[34m",
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
            f"Try and use it now to ask \x1b[36m{level.challenge_name}\x1b[0m",
            "to help you."
        ]

        deduction_sum_lines = [
            "You will play your lyre as before, but this time,",
            "your \x1b[34mtarget sum\x1b[0m is a mystery."
        ]

        deduction_addend_lines = [
            "However, you do know \x1b[34mhow many notes\x1b[0m",
            f"\x1b[36m{level.challenge_name}\x1b[0m wants to hear. Make sure your",
            "song includes that many notes before pressing X",
            "followed by <Enter> to finish playing."
        ]

        deduction_fail_lines = [
            "Because you don't know your \x1b[34mtarget sum\x1b[0m,",
            "you have more than one chance to play the song",
            f"that \x1b[36m{level.challenge_name}\x1b[0m wants",
            "to hear. You don't want to fail too many times,",
            "or else you will \x1b[31mrun out of chances\x1b[0m.",
            "",
            "How many chances do you have?",
            "You won't know until it's \x1b[31mtoo late\x1b[0m."
        ]

        deduction_deduce_lines = [
            "It's important to pay attention to the songs",
            "that \x1b[31mfail\x1b[0m because you can use",
            "that information to deduce the song that will",
            "\x1b[32msucceed\x1b[0m."
        ]

        thwart_lines = [
            "Sometimes, in the course of playing an incorrect song",
            "you will \x1b[31mexhaust\x1b[0m a note needed for the correct song.",
            "In that case, the gods will have mercy on you and",
            "\x1b[32mrestore\x1b[0m the notes you need on your lyre. You will be",
            "notified when this happens.",
            "",
            "This is also information you can use to deduce the ",
            f"song that \x1b[36m{level.challenge_name}\x1b[0m wants to hear."
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
            level.print_lyre_prompt(omit_phase=True)
            req_lines = self.get_requirement(level).split(" ")
            req_line = "\x1b[36m" + req_lines[0] + "\x1b[0m " + " ".join(req_lines[1:len(req_lines) - 1]) + " \x1b[34m" + req_lines[len(req_lines) - 1] +  "\x1b[0m"
            print(req_line)
            self.print_mock_sum(
                highlight_color="\x1b[34m",
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
            level.print_lyre_prompt(omit_phase=True)
            req_lines = self.get_requirement(level).split(" ")
            req_line = "\x1b[36m" + req_lines[0] + "\x1b[0m " + " ".join(req_lines[1:len(req_lines)])
            print(req_line)
            self.print_mock_sum(
                highlight_color="\x1b[34m",
                highlight_mode=SumHighlightMode.ADDENDS,
                phase=TextLevel.Phase.DEDUCTION,
                level=level,
            )
            self.text_utility.wait_for_enter()

            self.text_utility.clear_screen()
            level.print_header()
            print(self.get_lyre_with_lines(
                level.level.lyre,
                deduction_fail_lines,
                LyreHighlightMode.NO_HIGHLIGHT,
                lyre_highlight_color="",
            ))
            level.print_lyre_prompt(omit_phase=True)
            req_lines = self.get_requirement(level).split(" ")
            req_line = "\x1b[36m" + req_lines[0] + "\x1b[0m " + " ".join(req_lines[1:len(req_lines)])
            print(req_line)
            self.print_mock_sum(
                highlight_color="\x1b[34m",
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
            level.print_lyre_prompt(omit_phase=True)
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
            level.print_lyre_prompt(omit_phase=True)
            req_lines = self.get_requirement(level).split(" ")
            req_line = "\x1b[36m" + req_lines[0] + "\x1b[0m " + " ".join(req_lines[1:len(req_lines)])
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
            level.print_lyre_prompt(omit_phase=True)
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




