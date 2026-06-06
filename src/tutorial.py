import os
import pathlib
import random
import time
import typing as t

from enum import Enum
from pypresence import Presence

from guiding_eurydice_core.src.lyre import Lyre, Note

from src.level import RequirementVerb, TextLevel
from src.profile import Profile
from src.utils import CONTINUE_PROMPT, B_FOR_BACK_STR_SCREEN, DEFAULT_TUT_DATA_DIR, Q_TO_MENU_STR, S_TO_SKIP_STR, PROMPT_STR, TextUtility

# region intro lines

INTRO_LINES_1 = [ 
    "From Crete, Hymen, dressed in yellow garments,",
    "flew through vast expanses of the air",
    "and moved to regions of the Cicones,",
    "summoned there by the voice of Orpheus.",
]

INTRO_LINES_2 = [
    "From Crete, " + TextUtility.yellow("Hymen") + ", dressed in yellow garments,",
    "flew through vast expanses of the air",
    "and moved to regions of the Cicones,",
    "summoned there by the voice of Orpheus.",
]

FOOTNOTES_2 = [
    TextUtility.yellow("Hymen is the god of marriage.")
]

INTRO_LINES_3 = [
    "From Crete, Hymen, dressed in yellow garments,",
    "flew through vast expanses of the air",
    "and moved to regions of the Cicones,",
    "summoned there by the voice of " + TextUtility.blue("Orpheus") + ".", 
]

FOOTNOTES_3 = [
    TextUtility.blue("That's you. You are from Thrace."),
    TextUtility.blue("Your father is Apollo, the god of music and poetry."),
    TextUtility.blue("Your mother is Calliope, one of the nine muses."),
]

INTRO_LINES_4 = [
    "His trip was futile. Although he did attend",
    TextUtility.blue("Orpheus") + "'s wedding, he did not speak",
    "his usual words, or have a joyful face,",
    "or bring good luck. Even the torch he held",
    "spluttered with smoke, making his eyes water,",
    "and waving it around produced no flames."
]

INTRO_LINES_5 = [
    "What happened afterwards was even worse",
    "than any omen, for " + TextUtility.green("Eurydice"),
    "Orpheus's new bride, while wandering",
    "through a meadow with a crowd of naiads,",
    "was bitten on the ankle by a snake.",
]

INTRO_LINES_6 = [TextUtility.red("She collapsed and died.")]

INTRO_LINES_7 = [
    TextUtility.blue("The Thracian poet") + ",",
    "after he had had enough of mourning",
    "in the upper world, dared to travel down",
    "the Taenarian gate to the river Styx,",
    "to see if he could win the sympathy",
    "of dead shades below.",
] 

# endregion

# region Orpheus tutorial lines

LEVEL_LINES = [
    "You will need to pass through many obstacles and foes to rescue your wife.",
    "Each encounter will look like this..."
]

LYRE_LINES = [
    "This is your lyre. It is all you have.",
    "Each line represents a note you can play.",
    "Your first song of each level will always be",
    "to calm and reassure yourself."
]

NOTE_ID_LINES = [
    "Each note has an " + TextUtility.yellow("ID") + ".",
    "You can use the note's ID to " + TextUtility.cyan("mark") + " a note. ",
     TextUtility.cyan("Marking") + " a note can help you keep track of",
    "which notes you want to use in your song."
]

NOTE_MARK_LINES = [
    "To " + TextUtility.cyan("mark") + " a note, type its ID followed by one of the ",
    "following special characters: " + TextUtility.green("!") + ", " + TextUtility.yellow("?") + ", or " + TextUtility.red("X"),
    TextUtility.green("!") + " will put a " + TextUtility.green(TextUtility.V) + " next to the note's ID. " + TextUtility.yellow("?") + " will put a " + TextUtility.yellow(TextUtility.Q) + " there, and " + TextUtility.red("X") + " will put a " + TextUtility.red(TextUtility.X) + " there.",
    "To remove a note's existing mark, just type its ID followed",
    "by the same special character. To replace a note's existing",
    "mark, type its ID followed by the new mark you wish to apply."
 ]

NOTE_NAME_LINES = [
    "Each note has a " + TextUtility.yellow("name") + ".",
    "To play a note, enter its " + TextUtility.yellow("name") + ".",
    "Take care: if you attempt to play a",
    "nonexistent note, you could " + TextUtility.red("break a string") + ".",
]

NOTE_VALUE_LINES = [
    "Each note also has a " + TextUtility.yellow("value") + ".",
    "When you play a note, its " + TextUtility.yellow("value") + " will be added",
    "to your " + TextUtility.cyan("melody") + ".",
]

NOTE_REMAINING_LINES = [
    "Each note also has a " + TextUtility.yellow("limit") + " on how many times",
    "it can be played. If you try to play an",
    "exhausted note too many times, you could ",
    TextUtility.red("break a string") + ".",
]

TARGET_VALUE_LINES = [
    "You want to play notes that add up to the " + TextUtility.cyan("song"),
    "You can play as many notes as you like",
    "to reach the " + TextUtility.cyan("song") + ". Just make sure not to",
    "overplay " + TextUtility.red("exhausted") + " notes.",
]

FINISHING_LINES = [
    "Once you are satisfied with your song and",
    "would like to finish playing, press P and ",
    "then <Enter>.",
    "",
    "Give it a try!"
]

# endregion

# region deduction tutorial lines

DEDUCTION_SUM_LINES = [
    "You will play your lyre as before, but this",
    "time, the " + TextUtility.blue("desired song") + " is a mystery.",
]

DEDUCTION_NOTE_POOL_LINES = [
    "Furthermore, you have only the notes remaining",
    "from your last song. Any notes you " + TextUtility.red("exhausted"),
    "while playing for yourself are still",
    "unavailable to you. In some cases, if you have",
    TextUtility.red("exhausted") + " too many notes while",
    "playing for yourself, it may be impossible to",
]

DEDUCTION_FAIL_LINES = [
    "you will have more than one chance to play.",
    "Don't fail too many times, or else you will ",
    TextUtility.red("run out of chances") + ".",
]

DEDUCTION_DEDUCE_LINES = [
    "It's important to pay attention to the songs",
    "that " + TextUtility.red("fail") + " because that information can help",
    "you deduce the song that will " + TextUtility.green("succeed") + "."
]

TRY_LINES = [
    "It may take some time to get a feel for this",
    "part of your journey.",
    "",
    "Give it a try!"
]

# endregion

# region highlight modes

class LyreHighlightMode(Enum):
    NOTE_NAMES = 0
    NOTE_VALUES = 1
    NOTE_COUNTS = 2
    HIGHLIGHT_ALL = 3
    NO_HIGHLIGHT = 4
    NOTE_IDS = 5

class SumHighlightMode(Enum):
    SUM = 0
    ADDENDS = 1
    NO_HIGHLIGHT = 2
    HIGHLIGHT_ALL = 3

# endregion

class TutorialUtility:
    def __init__(
        self,
        requirement_verb: t.Optional[RequirementVerb] = None,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
    ):
        self.debug = debug
        self.rng = rng or random.Random()

        self.requirement_verb_idx = self.rng.randint(0, len(TextLevel.REQUIREMENT_VERBS))
        self.requirement_verb = requirement_verb or TextLevel.REQUIREMENT_VERBS[self.requirement_verb_idx % len(TextLevel.REQUIREMENT_VERBS)]

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

            id_str = lyre_highlight_color + "{:2d}".format(note.id) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_IDS else "{:2}".format(note.id)
            name_str = lyre_highlight_color + "{:<2}".format(note.name) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_NAMES else "{:<2}".format(note.name)
            val_str = lyre_highlight_color + "{:02d}".format(note.val) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_VALUES else "{:02}".format(note.val)
            count_str = lyre_highlight_color + "{:02d}".format(note.count) + term_highlight if lyre_highlight_mode == LyreHighlightMode.NOTE_COUNTS else "{:02}".format(note.count)

            return f"{id_str} |   | {name_str} ({val_str}) - {count_str} remaining"
        
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
            requirement_line += self.text_utility.blue("You")
        elif curr_phase == level.Phase.DEDUCTION:
            requirement_line += level.challenge_name
        
        requirement_line += " "

        if (curr_phase == level.Phase.DEDUCTION and level.challenge_number > 1) \
            or (curr_phase == level.Phase.ORPHEUS):
            requirement_line += self.requirement_verb.plur()
        else:
            requirement_line += self.requirement_verb.sing()

        requirement_line += ": "
        
        if curr_phase == level.Phase.ORPHEUS:
            requirement_line += str(level.level.orpheus_goal.val)
        elif curr_phase == level.Phase.DEDUCTION:
            requirement_line += "?"
        
        return requirement_line
    
    def print_requirement(
        self,
        requirement_line: str,
        highlight_color: t.Optional[str] = "",
    ):
        highlight_term = "\x1b[0m" if len(highlight_color) > 0 else ""
        print(highlight_color + requirement_line + highlight_term)

    def get_mock_sum(
        self,
        highlight_color: t.Optional[str] = "",
        highlight_mode: t.Optional[SumHighlightMode] = SumHighlightMode.NO_HIGHLIGHT,
        phase: t.Optional[TextLevel.Phase] = TextLevel.Phase.ORPHEUS,
        level: t.Optional[TextLevel] = None,
    ) -> str:
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
        return _highlight(mock_sum)

    def pad_and_continue(
        self,
        lines: t.List[str],
        back_enabled: t.Optional[bool] = False,
        skip_enabled: t.Optional[bool] = True,
    ) -> str:
        prompt_strs = [
            CONTINUE_PROMPT,
            Q_TO_MENU_STR,
            PROMPT_STR,
        ]

        if skip_enabled:
            prompt_strs.insert(1, S_TO_SKIP_STR)

        if back_enabled:
            prompt_strs.insert(1, B_FOR_BACK_STR_SCREEN)
        

        print("\n".join(lines))

        return input("\n".join(prompt_strs))
            
    
    def prose_screen(
        self,
        lines: t.List[str],
        footnote_lines: t.Optional[t.List[str]] = None,
        center_footnotes: t.Optional[bool] = False,
        max_width: int = 64,
        back_enabled: t.Optional[bool] = False,
        skip_enabled: t.Optional[bool] = False,
    ):
        res_lines = []
        if not self.debug:
            self.text_utility.clear_screen()

        term_width = self.text_utility.get_term_width()
        term_height = self.text_utility.get_term_height()

        wrapped = self.text_utility.wrap_lines(lines, max_width)
        footnote_wrapped = self.text_utility.wrap_lines(footnote_lines or [], max_width)

        block_width = max((self.text_utility.visible_len(line) for line in wrapped), default=0)
        left_padding = max((term_width - block_width) // 2, 0)

        top_padding = max((term_height - len(wrapped)) // 2 - 2, 0)
        res_lines.extend([""] * top_padding)

        for line in wrapped:
            res_lines.append((" " * left_padding) + line)

        # Footnote area, near bottom.
        prompt_reserved_lines = 2
        footnote_gap = max(
            term_height
            - top_padding
            - len(wrapped)
            - len(footnote_wrapped)
            - prompt_reserved_lines,
            1,
        ) - 1

        res_lines.extend([""] * footnote_gap)

        if footnote_wrapped:
            res_lines.append("-" * term_width)
            footnote_width = max((self.text_utility.visible_len(line) for line in footnote_wrapped), default=0)
            footnote_left_padding = max((term_width - footnote_width) // 2, 0) if center_footnotes else 0

            for line in footnote_wrapped:
                res_lines.append((" " * footnote_left_padding) + line)

        return self.pad_and_continue(lines=res_lines, back_enabled=back_enabled, skip_enabled=skip_enabled)

class StoryScreen:
    def __init__(
        self,
        lines: t.Union[t.List[str], str],
        footnote: t.Optional[t.Union[t.List[str], str]] = None,
        back_enabled: t.Optional[bool] = False,
        skip_enabled: t.Optional[bool] = False,
        tut_utility: t.Optional[TutorialUtility] = None,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
    ):
        self.lines = lines
        self.footnote = footnote
        self.back_enabled = back_enabled
        self.skip_enabled = skip_enabled
        self.debug = debug
        self.rng = rng or random.Random()
        
        self.tut_utility = tut_utility or TutorialUtility(debug=self.debug, rng=self.rng)

    def get_intro_step(
            self,
            func: t.Callable,
            text_utility: t.Optional[TextUtility] = TextUtility(),
            debug: t.Optional[bool] = False,
            rng: t.Optional[random.Random] = None,
        ) -> TutorialStep:
        return TutorialStep(
            level=None,
            func=func,
            text_utility=text_utility,
            debug=debug,
            rng=rng,
        )

    def get_func(self) -> t.Callable[[None], str]:
        def _res() -> str:
            return self.tut_utility.prose_screen(
                lines=self.lines,
                footnote_lines=self.footnote,
                back_enabled=self.back_enabled,
                skip_enabled=self.skip_enabled,
            )
        return _res

class TutorialStep:

    def __init__(
        self,
        level: TextLevel,
        func: t.Optional[t.Callable[[None], str]] = None,
        tut_utility: t.Optional[TutorialUtility] = None,
        text_utility: t.Optional[TextUtility] = None,
        requirement_verb: t.Optional[RequirementVerb] = None,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
    ):
        self.level = level
        self.func = func
        self.debug = debug
        self.rng = rng or random.Random()

        self.requirement_verb_idx = self.rng.randint(0, len(TextLevel.REQUIREMENT_VERBS))
        self.requirement_verb = requirement_verb or TextLevel.REQUIREMENT_VERBS[self.requirement_verb_idx % len(TextLevel.REQUIREMENT_VERBS)]

        self.tut_utility = tut_utility or TutorialUtility(requirement_verb=self.requirement_verb, rng=self.rng, debug=self.debug)
        self.text_utility = text_utility or TextUtility(rng=self.rng, debug=self.debug)

    def get_func(
        self,
        method: t.Callable[["TutorialStep"], str]
    ) -> t.Callable[[], str]:

        def _res() -> str:
            return method(self)

        return _res

    def play(self) -> str:
        try:
            return self.func()
        except Exception as e:
            print("TutorialStep crashed")
            print("func:", self.func)
            print("type:", type(e).__name__)
            print("error:", e)
            raise

# region Orpheus Tutorial Steps

    def ot_step1(self) -> str:
        self.text_utility.clear_screen()
        lvl_text = self.text_utility.center_text(lines=LEVEL_LINES)
        print(lvl_text)
        return self.tut_utility.pad_and_continue(lvl_text.split("\n"), back_enabled=False, skip_enabled=True)

    def ot_step3(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            NOTE_ID_LINES,
            LyreHighlightMode.NOTE_IDS,
            lyre_highlight_color=TextUtility.YELLOW
            )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum()
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step2(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            LYRE_LINES,
            LyreHighlightMode.HIGHLIGHT_ALL,
            lyre_highlight_color=TextUtility.YELLOW
            )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum()
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step4(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            NOTE_ID_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color=TextUtility.YELLOW
            )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum()
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step5(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            NOTE_NAME_LINES,
            LyreHighlightMode.NOTE_NAMES,
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum()
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step6(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            NOTE_VALUE_LINES,
            LyreHighlightMode.NOTE_VALUES,
            lyre_highlight_color=TextUtility.YELLOW
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum(
            highlight_color=TextUtility.CYAN,
            highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step7(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            NOTE_REMAINING_LINES,
            LyreHighlightMode.NOTE_COUNTS,
            lyre_highlight_color=TextUtility.YELLOW
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum()
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step8(self) -> str:
        self.text_utility.clear_screen()
        req_line = self.tut_utility.get_requirement(self.level)
        line1_to_add = TextUtility.cyan("you need") + ", shown after the line " 
        line2_to_add = TextUtility.cyan(req_line.split(":")[0]) + "\"."
        if len(TARGET_VALUE_LINES) == 4:
            TARGET_VALUE_LINES.insert(1, line2_to_add)
            TARGET_VALUE_LINES.insert(1, line1_to_add)
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            TARGET_VALUE_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color=""
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = TextUtility.cyan(req_line.split(":")[0]) + ":" + TextUtility.cyan(req_line.split(":")[1])
        ms = self.tut_utility.get_mock_sum(
            highlight_color="",
            highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

    def ot_step9(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            FINISHING_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum(
            highlight_color="",
            highlight_mode=SumHighlightMode.HIGHLIGHT_ALL,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_lines, ms], back_enabled=True, skip_enabled=True)

# endregion

# region deduction tutorial steps

    def dt_step1(self) -> str:
        deduction_tutorial_lines = [
            "You aren't the only one who is moved by your music.",
            "It has a tremendous power to persuade those around you.",
            f"Try and use it now to ask {TextUtility.cyan(self.level.challenge_name)}",
            "to help you."
        ]

        self.text_utility.clear_screen()
        ded_text = self.text_utility.center_text(lines=deduction_tutorial_lines)
        print(ded_text)
        return self.tut_utility.pad_and_continue(ded_text.split("\n"), back_enabled=False, skip_enabled=True)

    def dt_step2(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            DEDUCTION_SUM_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level).split(" ")
        req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines) - 1]) + " " + TextUtility.blue(req_lines[len(req_lines) - 1])
        ms = self.tut_utility.get_mock_sum(
            highlight_color="",
            highlight_mode=SumHighlightMode.SUM,
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)

    def dt_step3(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        req_lines = self.tut_utility.get_requirement(self.level).split(" ")
        req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines) - 1]) + " " + TextUtility.blue(req_lines[len(req_lines) - 1])
        #line_to_insert = "play the song " + req_line.split(":")[0] + "."
        # DEDUCTION_NOTE_POOL_LINES.insert(
        #     len(DEDUCTION_NOTE_POOL_LINES),
        #     line_to_insert,
        # )
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            DEDUCTION_NOTE_POOL_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        ms = self.tut_utility.get_mock_sum(
            highlight_color="",
            highlight_mode=SumHighlightMode.NO_HIGHLIGHT,
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)


    def dt_step4(self) -> str:
        deduction_addend_lines = [
            "However, you do know " + TextUtility.blue("how many notes"),
            f"{TextUtility.cyan(self.level.challenge_name)} wants to hear. Make sure your song",
            "includes that many notes before you finish",
            "playing."
        ]

        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            deduction_addend_lines,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level).split(" ")
        req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines)])
        ms = self.tut_utility.get_mock_sum(
            highlight_color=TextUtility.BLUE,
            highlight_mode=SumHighlightMode.ADDENDS,
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled = True, skip_enabled=True)

    def dt_step5(self) -> str:
        self.text_utility.clear_screen()
        req_line = self.tut_utility.get_requirement(self.level)
        line1_to_add = "Because you don't know the " + TextUtility.blue("song")
        line2_to_add = f" {TextUtility.cyan(req_line.split(":")[0])}, "
        if len(DEDUCTION_FAIL_LINES) == 3:
            DEDUCTION_FAIL_LINES.insert(0, line2_to_add)
            DEDUCTION_FAIL_LINES.insert(0, line1_to_add)
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            DEDUCTION_FAIL_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level).split(" ")
        req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines) - 1]) + " " + TextUtility.blue(req_lines[len(req_lines) - 1])
        ms = self.tut_utility.get_mock_sum(
            highlight_color="",
            highlight_mode=SumHighlightMode.SUM,
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)

    def dt_step6(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            DEDUCTION_DEDUCE_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_line = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum(
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)

    def dt_step7(self) -> str:
        thwart_lines = [
            "Sometimes, in the course of playing an",
            "incorrect song you will " + TextUtility.red("exhaust"),
            "a note needed for the correct song.",
            "",
            "In that case, the gods will have mercy",
            "on you and " + TextUtility.green("restore") + " the notes",
            "you need on your lyre. You will",
            "be notified when this happens.",
            "",
            "This information can also be used to",
            "deduce the song that " + TextUtility.cyan(self.level.challenge_name) + " wants to hear."
        ]

        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            thwart_lines,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_lines = self.tut_utility.get_requirement(self.level).split(" ")
        req_line = TextUtility.cyan(req_lines[0]) + " " + " ".join(req_lines[1:len(req_lines)])
        ms = self.tut_utility.get_mock_sum(
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)

    def dt_step8(self) -> str:
        self.text_utility.clear_screen()
        hdr = self.level.get_header(omit_description=True)
        lr = self.tut_utility.get_lyre_with_lines(
            self.level.level.lyre,
            TRY_LINES,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color="",
        )
        eq = ("=" * self.text_utility.get_term_width())
        req_line = self.tut_utility.get_requirement(self.level)
        ms = self.tut_utility.get_mock_sum(
            phase=TextLevel.Phase.DEDUCTION,
            level=self.level,
        )
        return self.tut_utility.pad_and_continue([hdr, lr, eq, req_line, ms], back_enabled=True, skip_enabled=True)

# endregion

class TutorialPlayer:
    def __init__(
        self,
        profile: Profile,
        text_utility: t.Optional[TextUtility] = TextUtility(),
        requirement_verb: t.Optional[RequirementVerb] = None,
        debug: t.Optional[bool] = False,
        rng: t.Optional[random.Random] = None,
        tut_data_dir: t.Optional[pathlib.Path] = None,
        presence: t.Optional[Presence] = None,
    ):
        self.profile = profile
        self.text_utility = text_utility

        self.tut_data_dir = tut_data_dir or pathlib.Path(DEFAULT_TUT_DATA_DIR)
        self.debug = debug
        self.rng = rng or random.Random()

        self.presence = None
        if presence:
            self.presence = presence
        
        self.requirement_verb_idx = self.rng.randint(0, len(TextLevel.REQUIREMENT_VERBS))
        self.requirement_verb = requirement_verb or TextLevel.REQUIREMENT_VERBS[self.requirement_verb_idx % len(TextLevel.REQUIREMENT_VERBS)]


# region consts


    INTRO_PAIRS: t.List[StoryScreen] = [
        StoryScreen(INTRO_LINES_1, back_enabled=False, skip_enabled=True),
        StoryScreen(INTRO_LINES_2, FOOTNOTES_2, back_enabled=True, skip_enabled=True),
        StoryScreen(INTRO_LINES_3, FOOTNOTES_3, back_enabled=True, skip_enabled=True),
        StoryScreen(INTRO_LINES_4, back_enabled=True, skip_enabled=True),
        StoryScreen(INTRO_LINES_5, back_enabled=True, skip_enabled=True),
        StoryScreen(INTRO_LINES_6, back_enabled=True, skip_enabled=True),
        StoryScreen(INTRO_LINES_7, back_enabled=True, skip_enabled=True),
    ]

    ORPHEUS_STEP_FUNCS: t.List[t.Callable] = [
        TutorialStep.ot_step1,
        TutorialStep.ot_step2,
        TutorialStep.ot_step3,
        TutorialStep.ot_step4,
        TutorialStep.ot_step5,
        TutorialStep.ot_step6,
        TutorialStep.ot_step7,
        TutorialStep.ot_step8,
        TutorialStep.ot_step9,
    ]

    DEDUCTION_STEP_FUNCS: t.List[t.Callable] = [
        TutorialStep.dt_step1,
        TutorialStep.dt_step2,
        TutorialStep.dt_step3,
        TutorialStep.dt_step4,
        TutorialStep.dt_step5,
        TutorialStep.dt_step6,
        TutorialStep.dt_step7,
        TutorialStep.dt_step8,
    ]

# endregion
    def load_tut_levels(self) -> t.List[TextLevel]:
        if not os.path.exists(self.tut_data_dir):
            raise FileNotFoundError(f"Unable to find tutorial directory {self.tut_data_dir}")

        files = []
        for _, _, filenames in os.walk(self.profile.level_data_dir):
            files.extend(filenames)

        tuts = [file for file in files if file.startswith("tut")]

        if len(tuts) == 0:
            raise FileNotFoundError(f"No tutorial levels found in tutorial directory {self.tut_data_dir}")

        if len(tuts) != 2:
            raise FileNotFoundError(f"Found wrong number of tutorial level definitions in {self.tut_data_dir}: {len(files)} (expected 2)")
        
        levels = []
        for f in tuts:
            tl = TextLevel.from_json(
                json_path=self.tut_data_dir.joinpath(f),
                debug=self.debug,
                presence=self.presence,
            )
            levels.append(tl)
        
        return sorted(levels)

    def get_intro_steps(self) -> t.Dict[int, TutorialStep]:
        res: t.Dict[int, TutorialStep] = {}

        for i, f in enumerate(TutorialPlayer.INTRO_PAIRS):
            ts = f.get_intro_step(
                text_utility=self.text_utility,
                func=f.get_func(),
                debug=self.debug,
                rng=self.rng,
            )
            res[i] = ts
        
        return res

    def get_orpheus_steps(
        self,
        level: TextLevel,
    ) -> t.Dict[int, TutorialStep]:
        res: t.Dict[int, TutorialStep] = {}

        for i, f in enumerate(TutorialPlayer.ORPHEUS_STEP_FUNCS):
            ts = TutorialStep(
                level=level,
                text_utility=self.text_utility,
                requirement_verb=self.requirement_verb,
                debug=self.debug,
                rng=self.rng,
            )
            ts.func = ts.get_func(f)
            res[i] = ts

        return res

    def get_deduction_steps(
        self,
        level: TextLevel,
    ) -> t.Dict[int, TutorialStep]:
        res: t.Dict[int, TutorialStep] = {}

        for i, f in enumerate(TutorialPlayer.DEDUCTION_STEP_FUNCS):
            ts = TutorialStep(
                level=level,
                text_utility=self.text_utility,
                requirement_verb=self.requirement_verb,
                debug=self.debug,
                rng=self.rng,
            )
            ts.func = ts.get_func(f)
            res[i] = ts

        return res
    
    def play(
        self,
        phase: TextLevel.TutorialPhase,
        level: t.Optional[TextLevel] = TextLevel(),
    ) -> bool:
        def _run_tut_steps() -> bool:
            i = 0

            try:
                while (i < len(steps)) and (i > -1):
                    ip = steps[i].play()
                    if (ip is None) or (len(ip) == 0):
                        i += 1
                        continue

                    if (ip.upper() == "Q"):
                        return False    
                    elif (ip.upper() == "S"):
                        break         
                    elif (ip.upper() == "B"):
                        i -= 1

                return True
            except KeyboardInterrupt:
                print("Goodbye")

                if self.presence:
                    self.presence.clear()
                    self.presence.close()

                time.sleep(0.5)
                SystemExit(0)       

        res = False
        steps: t.Dict[int, TutorialStep] = {}

        try:
            if phase == TextLevel.TutorialPhase.INTRO:
                if self.presence:
                    self.presence.update(state="Introduction")

                steps = self.get_intro_steps()
                res = _run_tut_steps()

            elif (phase == TextLevel.TutorialPhase.ORPHEUS_ONLY):
                if self.presence:
                    self.presence.update(state="Tutorial")

                steps = self.get_orpheus_steps(level)
                res = _run_tut_steps()

                if res:
                    res = level.run(tutorial_phase=phase)

            elif (phase == TextLevel.TutorialPhase.DEDUCTION_START):
                if self.presence:
                    self.presence.update(state="Tutorial")

                steps = self.get_deduction_steps(level)
                res = level.run(tutorial_phase=phase)
            
                if res:
                    cont = _run_tut_steps()

                    if cont:
                        res = res.run(tutorial_phase=TextLevel.TutorialPhase.DEDUCTION_END)
                    else:
                        res = False
            
            else:
                raise ValueError(f"Unexpected phase", phase)
        except KeyboardInterrupt:
            print("Goodbye.")

            if self.presence:
                self.presence.clear()
                self.presence.close()

            time.sleep(0.5)
            SystemExit(0)
        
        return res
    