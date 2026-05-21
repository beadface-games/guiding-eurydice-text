import typing as t

from enum import Enum

from guiding_eurydice_core.src.lyre import Lyre, Note

from src.level import TextLevel
from src._utils import TextUtility

CONTINUE_PROMPT = "Press <Enter> to continue."

class LyreHighlightMode(Enum):
    NOTE_NAMES = 0
    NOTE_VALUES = 1
    NOTE_COUNT = 2
    HIGHLIGHT_ALL = 3
    NO_HIGHLIGHT = 4

class TutorialPlayer:
    def __init__(self):
        self.text_utility = TextUtility()

    def print_padded_lines(
        self,
        lines: t.List[str]
    ):
      num_lines = self.text_utility.get_all_but_last_line_padding(lines)
      for _ in range(0, num_lines):
          print()

    def pad_and_continue(
        self,
        lines: t.List[str]
    ):
        self.print_padded_lines(lines)
        _ = input(CONTINUE_PROMPT)

    def wait_for_enter(self):
        _ = input(CONTINUE_PROMPT)

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
        highlight_color: t.Optional[str] = ""):
        highlight_term = "\x1b[0m" if len(highlight_color) > 0 else ""
        print(highlight_color + "= 0" + highlight_term)

    def play_intro(self):
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

        self.text_utility.clear_screen()
        print(self.text_utility.center_text(lines=initial_wedding_lines, horizontal=False, vertical=False))
        self.pad_and_continue(initial_wedding_lines)
        
        self.text_utility.clear_screen()
        print(self.text_utility.center_text(multi_lines=[hymen_wedding_lines_top, hymen_wedding_lines_bottom], horizontal=False, vertical=False))
        _ = input(CONTINUE_PROMPT)
        
        self.text_utility.clear_screen()
        print(self.text_utility.center_text(multi_lines=[orpheus_wedding_lines_top, orpheus_wedding_lines_bottom], horizontal=False, vertical=False))
        _ = input(CONTINUE_PROMPT)

        self.text_utility.clear_screen()
        print(self.text_utility.center_text(lines=failed_torch_lines, horizontal=False, vertical=False))
        self.pad_and_continue(initial_wedding_lines)

        self.text_utility.clear_screen()
        print(self.text_utility.center_text(lines=death_lines, horizontal=False, vertical=False))
        self.pad_and_continue(initial_wedding_lines)

        self.text_utility.clear_screen()
        print(self.text_utility.center_text(line=death_line, horizontal=False, vertical=False))
        self.pad_and_continue(initial_wedding_lines)

        self.text_utility.clear_screen()
        print(self.text_utility.center_text(lines=mourning_lines, horizontal=False, vertical=False)) 
        self.pad_and_continue(initial_wedding_lines)

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
            "\x1b[31mbreak a string\x1b[0m."
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
            "How many times is too many? You won't know until \x1b[31m it's\x1b[0m",
            "\x1b[31mtoo late\x1b[0m."
        ]

        target_value_lines = [
            "You want to play notes that add up to the \x1b[34mtarget sum\x1b[0m",
            "You can play as many notes as you like",
            "to reach the \x1b[34msum\x1b[0m. Just make sure not to",
            "overplay exhausted notes.",
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

        self.text_utility.clear_screen()
        lvl_text = self.text_utility.center_text(lines=level_lines)
        print(lvl_text)
        self.pad_and_continue(lvl_text.split("\n"))

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
        self.wait_for_enter()

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
        self.wait_for_enter()
        
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
        self.print_mock_sum("\x1b[34m")
        self.wait_for_enter()

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
        self.wait_for_enter()

        self.text_utility.clear_screen()
        level.print_header(omit_description=True)
        req_line = self.get_requirement(level)
        line_to_add = f"shown after the line \"\x1b[32m{req_line.split(":")[0]}\x1b[0m\"."
        target_value_lines.insert(1, line_to_add)
        print(self.get_lyre_with_lines(
            level.level.lyre,
            target_value_lines,
            LyreHighlightMode.NO_HIGHLIGHT,
            lyre_highlight_color=""
        ))
        level.print_lyre_prompt(omit_phase=True)
        self.print_requirement(level, req_line, highlight_color="\x1b[32m")
        self.print_mock_sum("\x1b[34m")
        self.wait_for_enter()

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
        self.print_mock_sum("\x1b[34m")
        self.wait_for_enter()

        level.run(orpheus_tutorial=True)


    def play_tutorials(self, level: TextLevel):
        self.play_intro()
        self.play_orpheus_tutorial(level)
