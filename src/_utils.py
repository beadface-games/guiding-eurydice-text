# -*- coding: utf-8 -*-
import json
import os
import pathlib
import random
import re
import shutil
import sys
import textwrap
import time
import typing as t

from colorama import just_fix_windows_console

APP_NAME = "GuidingEurydice"

OPTION_SELECT_STR = "Please enter the number of the option you wish to select and press <Enter>."
B_FOR_BACK_STR = "Enter B followed by <Enter> to go back to the previous menu."
Q_TO_QUIT_STR = "Enter Q followed by <Enter> to quit."
PROMPT_STR = ">"


class UserDataManager:
    def __init__(self):
        pass

    @staticmethod
    def get_user_data_dir(app_name: str = APP_NAME) -> pathlib.Path:
        if sys.platform == "win32":
            base = os.getenv("APPDATA")
            base = pathlib.Path(base) if base else pathlib.Path.home() / "AppData" / "Roaming"
        elif sys.platform == "darwin":
            base = pathlib.Path.home() / "Library" / "Application Support"
        else:
            base = os.getenv("XDG_DATA_HOME")
            base = pathlib.Path(base) if base else pathlib.Path.home() / ".local" / "share"

        app_dir = base / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir

    def resource_path(self, relative_path: str) -> pathlib.Path:

        if getattr(sys, "frozen", False):
            return pathlib.Path(sys._MEIPASS) / relative_path

        return pathlib.Path(__file__).resolve().parents[2] / relative_path
    
    def get_profiles_dir(self, app_name: str = APP_NAME) -> pathlib.Path:
        profiles_dir = UserDataManager.get_user_data_dir(app_name) / "profiles"
        profiles_dir.mkdir(parents=True, exist_ok=True)
        return profiles_dir
    
    def get_metadata_dir(self, app_name: str = APP_NAME) -> pathlib.Path:
        metadata_dir = UserDataManager.get_user_data_dir(app_name) / "metadata"
        metadata_dir.mkdir(parents=True, exist_ok=True)
        return metadata_dir

    def get_metadata_file(self) -> pathlib.Path:
        return self.get_metadata_dir() / "metadata.json"
    
udm = UserDataManager()
CONTINUE_PROMPT = "Press <Enter> to continue."
DEFAULT_LEVEL_DATA_DIR = "guiding_eurydice_levels/levels"

DATE_FORMAT_STR = "%Y-%m-%d %I:%M:%S %p"
DEFAULT_PROFILE_DATA_DIR = udm.get_profiles_dir()
DEFAULT_METADATA_DIR = udm.get_metadata_dir()
DEFAULT_METADATA_FILE = udm.get_metadata_file()

class RequirementVerb():
        def __init__(
            self,
            plural: str,
            singular: t.Optional[str] = "",
            preposition: t.Optional[str] = ""
        ):
            self.plural = plural
            self.singular = singular or plural + "s"
            self.preposition = preposition or ""

        def sing(self) -> str:
            if len(self.preposition) > 0:
                return self.singular + " " + self.preposition
            return self.singular

        def plur(self) -> str:
            if len(self.preposition) > 0:
                return self.plural + " " + self.preposition
            return self.plural

class TextUtility:
    ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

    def __init__():
        pass

    @staticmethod
    def is_probably_old_windows_console() -> bool:
        """
        Heuristic detection for old Windows console hosts.

        Returns True if we're probably running in:
        - old blue PowerShell
        - old cmd.exe host
        - legacy conhost

        Returns False for:
        - Windows Terminal
        - modern terminal environments
        - non-Windows systems
        """

        if os.name != "nt":
            return False

        # Windows Terminal sets this env var.
        if os.environ.get("WT_SESSION"):
            return False

        # VSCode terminal
        if os.environ.get("TERM_PROGRAM") == "vscode":
            return False

        # Some modern terminals expose TERM.
        term = os.environ.get("TERM", "").lower()
        if "xterm" in term or "ansi" in term:
            return False

        return True
    
    RESET = "\x1b[0m" 
    RED = "\x1b[91m" if is_probably_old_windows_console() else "\x1b[31m"
    GREEN = "\x1b[92m" if is_probably_old_windows_console() else "\x1b[32m"
    YELLOW = "\x1b[93m" if is_probably_old_windows_console() else "\x1b[33m"
    BLUE = "\x1b[94m" if is_probably_old_windows_console() else "\x1b[34m"
    MAGENTA = "\x1b[95m" if is_probably_old_windows_console() else "\x1b[35m"
    CYAN = "\x1b[96m" if is_probably_old_windows_console() else "\x1b[36m"
    BOLD = "1"
    
    @staticmethod
    def red(s: str) -> str:
        return TextUtility.RED + s + TextUtility.RESET

    @staticmethod
    def green(s: str) -> str:
        return TextUtility.GREEN + s + TextUtility.RESET
    
    @staticmethod
    def yellow(s: str) -> str:
        return TextUtility.YELLOW + s + TextUtility.RESET
    
    @staticmethod
    def blue(s: str) -> str:
        return TextUtility.BLUE + s + TextUtility.RESET
    
    @staticmethod
    def magenta(s: str) -> str:
        return TextUtility.MAGENTA + s + TextUtility.RESET

    @staticmethod
    def cyan(s: str) -> str:
        return TextUtility.CYAN + s + TextUtility.RESET
    
    @staticmethod
    def detect_and_warn_old_console():
        if TextUtility.is_probably_old_windows_console():
            just_fix_windows_console()

            if os.name == "nt":
                os.system("chcp 65001 > nul")

            if os.path.exists(DEFAULT_METADATA_FILE):
                with open(DEFAULT_METADATA_FILE, "r") as f:
                    data = json.load(f)
                    if ("has_viewed_old_console_warning" in data.keys()) and (isinstance(data["has_viewed_old_console_warning"], bool)) and data["has_viewed_old_console_warning"]:
                        return
                    
            try:
                print()
                print("ATTENTION: do the words below occur in the color they name?")
                print(
                    "\x1b[91mRED\x1b[0m",
                    "\x1b[93mYELLOW\x1b[0m",
                    "\x1b[92mGREEN\x1b[0m",
                    "\x1b[94mBLUE\x1b[0m",
                    "\x1b[95mMAGENTA\x1b[0m",
                    "\x1b[96mCYAN\x1b[0m"
                )
                print()
                print("If not, or if they are difficult to read, a modern terminal is recommended.")
                print("Windows Terminal is free from the Microsoft Store:")
                print("https://apps.microsoft.com/detail/9N0DX20HK701")
                print("After you install it, open it and run the following command:")
                print("cd <path\\to\GuidingEurydice.exe>")
                print("Then run this next command: .\GuidingEurydice.exe")
                print()
                print("It is NOT recommended to play on your current console.")
                print("If you proceed here, some text may be unreadable.")
                print("If you wish to proceed with your current setup, press <Enter>.")
                print("Otherwise, press Q to quit.")
                i = input("> ")
                if i.upper() == "Q":
                    print("Goodbye.")
                    raise SystemExit(0)
            except KeyboardInterrupt:
                raise SystemExit(0)
            
            d : t.Dict[str, t.Any] = {}
            d["has_viewed_old_console_warning"] = True

            with open(DEFAULT_METADATA_FILE, 'a') as f:
                json.dump(d, f, indent=2)            

    @staticmethod
    def set_utf_8_encoding():
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")

    @staticmethod
    def fix_formatting():
        TextUtility.detect_and_warn_old_console()
        TextUtility.set_utf_8_encoding()

    def __init__(
        self,
        rng: t.Optional[random.Random] = None,
        debug:t.Optional[bool]=False,
    ):
        self.rng = rng or random.Random()
        self.debug = debug        

    def get_term_width(self) -> int:
        return shutil.get_terminal_size(fallback=(80, 24)).columns

    def get_term_height(self) -> int:
        return shutil.get_terminal_size(fallback=(80, 24)).lines
    
    def visible_len(self, s: str) -> int:
        return len(self.ANSI_RE.sub("", s))

    def get_horizontal_padding(self, term_width: int, s: str) -> int:
        padding = (term_width - self.visible_len(s)) // 2
        return max(padding, 0)

    def wrap_lines(self, lines: t.List[str], width: int) -> t.List[str]:
        """
        Keep ANSI-colored lines intact. For now, don't wrap colored lines;
        just preserve them so centering doesn't break escape codes.
        """
        usable_width = max(width, 20)
        wrapped: t.List[str] = []

        for line in lines:
            if line == "":
                wrapped.append("")
            elif "\x1b[" in line:
                wrapped.append(line)
            else:
                wrapped.extend(textwrap.wrap(
                    line,
                    width=usable_width,
                    break_long_words=False,
                    break_on_hyphens=False,
                ) or [""])

        return wrapped
    
    def get_vertical_padding(
            self,
            term_height: int,
            lines: t.List[str],
            num_extra_lines: t.Optional[int]=0,
        ) -> int:
        actual_lines = num_extra_lines

        for line in lines:
            if len(line) > self.get_term_width():
                actual_lines += 2
            else:
                actual_lines += 1
        
        padding = int((term_height - actual_lines) // 2)
        if padding < 0:
            padding = 0

        return padding

    def get_longest_str(self, arr: t.List[str]) -> str:
        champ_i = 0
        champ_s = ""

        for s in arr:
            if len(s) > champ_i:
                champ_i = len(s)
                champ_s = s

        return champ_s

    def clear_screen(self):
        # ANSI clear screen + move cursor home. Works in modern Windows Terminal,
        # PowerShell, Git Bash, macOS Terminal, and most Linux terminals.
        if not self.debug:
            print("\033[2J\033[H", end="")

    def clear_lines(self, n: int):
      for _ in range(n):
        print("\033[F\033[K", end="")

    def get_content_width(
        self,
        max_width: t.Optional[int]=None,
    ) -> int:
        
        term_width = self.get_term_width()
        # Leave a little breathing room at the edges. This avoids awkward text
        # touching the terminal border in narrow windows.
        content_width = max_width or term_width - 4
        content_width = max(1, min(content_width, term_width))

        return content_width
    
    def print_padded_lines(
        self,
        lines: t.List[str],
        n: t.Optional[int] = 0,
    ):
      num_lines = self.get_all_but_last_n_lines_padding(lines, n=n)
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
    
    def center_text(
        self,
        line: t.Optional[str] = None,
        lines: t.Optional[t.List[str]] = None,
        multi_lines: t.Optional[t.List[t.List[str]]] = None,
        max_width: t.Optional[int] = None,
        horizontal: bool = True,
        vertical: bool = True,
    ) -> str:
        """
        Return text centered horizontally, and optionally vertically, in the terminal.

        - Pass either line="..." or lines=["...", "..."]
        - Long lines are wrapped before centering
        - Uses terminal-size fallback so redirected output/tests don't crash
        """
        if (line is not None and lines is not None) or \
            (line is not None and multi_lines is not None) or \
            (lines is not None and multi_lines is not None):
            raise ValueError("Pass either line or lines, not both.")

        if line is None and lines is None and multi_lines is None:
            return ""


        term_width = self.get_term_width()
        term_height = self.get_term_height()

        if line is not None or lines is not None:
            raw_lines = [line] if line is not None else list(lines or [])

            rendered_lines = self.wrap_lines(raw_lines, self.get_content_width(max_width))

            top_padding = self.get_vertical_padding(term_height, rendered_lines) if vertical else 0

            output_lines: t.List[str] = []
            output_lines.extend("" for _ in range(top_padding))

            for rendered_line in rendered_lines:
                left_padding = self.get_horizontal_padding(term_width, rendered_line) if horizontal else 0
                output_lines.append((" " * left_padding) + rendered_line)

            output_lines.extend("" for _ in range(top_padding))

            return "\n".join(output_lines)
        elif multi_lines is not None:
            rendered_line_groups = []
            total_height = 0

            for group in multi_lines:
                rendered_lines = self.wrap_lines(group, self.get_content_width(max_width))
                rendered_line_groups.append(rendered_lines)
                total_height += len(rendered_lines)

            gap_count = max(len(rendered_line_groups) - 1, 1)
            available_gap = max(term_height - total_height - 2, 1)
            in_between_padding = available_gap // gap_count

            output_lines: t.List[str] = []

            if vertical:
                top_padding = max((term_height - total_height - (in_between_padding * (len(rendered_line_groups) - 1))) // 2, 0)
                output_lines.extend("" for _ in range(top_padding))

            for i, group in enumerate(rendered_line_groups):
                for rendered_line in group:
                    left_padding = self.get_horizontal_padding(term_width, rendered_line) if horizontal else 0
                    output_lines.append((" " * left_padding) + rendered_line)

                if i < len(rendered_line_groups) - 1:
                    output_lines.extend("" for _ in range(in_between_padding))

            return "\n".join(output_lines)
        
    def get_all_but_last_n_lines_padding(
        self,
        lines: t.List[str],
        n: t.Optional[int] = 0,
    ) -> int:
        return self.get_term_height() - len(lines) - (5 + n)
    
    def boxify_lines(
        self,
        lines: t.List[str],
        max_width: t.Optional[int] = None,
    ) -> t.List[str]:
        wrapped_lines = self.wrap_lines(lines, self.get_content_width(max_width))
        longest_len = max((len(line) for line in wrapped_lines), default=0)

        res: t.List[str] = []
        res.append("-" * (longest_len + 4))

        for line in wrapped_lines:
            total_padding = longest_len - len(line)
            left_padding = total_padding // 2
            right_padding = total_padding - left_padding

            boxed_line = "| " + (" " * left_padding) + line + (" " * right_padding) + " |"
            res.append(boxed_line)

        res.append("-" * (longest_len + 4))

        return res

    def flash_msg(
        self,
        msg: str,
        time_in_s: float,
        iterations: int
    ):
        if not self.debug:
            for _ in range(iterations):
                self.clear_screen()
                print()
                time.sleep(time_in_s)
                print(msg)
                time.sleep(time_in_s)
        else:
            print(msg)

    def fade_msg(
        self,
        msg: str,
        max_time_in_ms_per_it: float,
        iterations: int,
        center_horizontally: bool=True,
        center_vertically: bool=True,
        min_time_in_ms_per_it: float=0.0,
    ):
        def _get_fade_msgs() -> t.Dict[str, float]:
            curr_str = msg
            letters_per_it = len(msg) // iterations
            indices = [n for n in range(0, len(msg))]
            self.rng.shuffle(indices)
            res : t.Dict[str, float] = {}

            while len(indices) > 0:
                ms = self.rng.randint(int(min_time_in_ms_per_it), int(max_time_in_ms_per_it)) / 1000

                for _ in range(letters_per_it):
                    if len(indices) > 0:
                        idx = indices.pop(0)
                        curr_str = curr_str[:idx] + " " + curr_str[idx + 1:]
                
                res[curr_str] = ms
            
            return res
        
        if not self.debug:
            self.clear_screen()
            fade_msgs = _get_fade_msgs()
            if center_horizontally:
                print(
                    self.center_text(
                        msg,
                        None,
                        None,
                        center_vertically,
                    )
                )
            else:
                print(msg)
            time.sleep(max_time_in_ms_per_it / 1000)

            for s, ms in fade_msgs.items():
                self.clear_screen()
                if center_horizontally:
                    print(
                        self.center_text(
                        s,
                        None,
                        None,
                        center_vertically,
                        )
                    )
                else:
                    print(s)
                time.sleep(ms)
        else:
            print(msg)
        
    def story_screen(
        self,
        top_lines: t.List[str],
        bottom_lines: t.Optional[t.List[str]] = None,
        max_width: int = 72,
    ):
        if not self.debug:
            self.clear_screen()

        groups = [top_lines]
        if bottom_lines:
            groups.append(bottom_lines)

        print(self.center_text(
            multi_lines=groups,
            max_width=max_width,
            horizontal=True,
            vertical=True,
        ))

        self.wait_for_enter()

    def prose_screen(
        self,
        lines: t.List[str],
        footnote_lines: t.Optional[t.List[str]] = None,
        center_footnotes: t.Optional[bool] = False,
        max_width: int = 64,
    ):
        if not self.debug:
            self.clear_screen()

        term_width = self.get_term_width()
        term_height = self.get_term_height()

        wrapped = self.wrap_lines(lines, max_width)
        footnote_wrapped = self.wrap_lines(footnote_lines or [], max_width)

        block_width = max((self.visible_len(line) for line in wrapped), default=0)
        left_padding = max((term_width - block_width) // 2, 0)

        top_padding = max((term_height - len(wrapped)) // 2 - 2, 0)
        print("\n" * top_padding, end="")

        for line in wrapped:
            print((" " * left_padding) + line)

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

        print("\n" * footnote_gap, end="")

        if footnote_wrapped:
            print("-" * term_width)
            footnote_width = max((self.visible_len(line) for line in footnote_wrapped), default=0)
            footnote_left_padding = max((term_width - footnote_width) // 2, 0) if center_footnotes else 0

            for line in footnote_wrapped:
                print((" " * footnote_left_padding) + line)

        self.wait_for_enter()

    def menu_screen(
        self,
        lines: t.List[str],
        footnote_lines: t.Optional[t.List[str]] = None,
        center_footnotes: t.Optional[bool] = False,
        max_width: int = 64,
        prompt: t.Optional[str] = None,
        additional_prompt: t.Optional[str] = None,
        is_submenu: t.Optional[bool] = False
    ) -> str:
        default_prompt_lines = [
            OPTION_SELECT_STR,
            Q_TO_QUIT_STR,
            PROMPT_STR,
        ]

        if is_submenu:
            default_prompt_lines.insert(
                1,
                B_FOR_BACK_STR,
            )

        if additional_prompt:
            default_prompt_lines.insert(
                0,
                additional_prompt
            )

        actual_prompt = prompt or "\n".join(default_prompt_lines)

        if not self.debug:
            self.clear_screen()

        term_width = self.get_term_width()
        term_height = self.get_term_height()

        wrapped = self.wrap_lines(lines, max_width)
        footnote_wrapped = self.wrap_lines(footnote_lines or [], max_width)

        block_width = max((self.visible_len(line) for line in wrapped), default=0)
        left_padding = max((term_width - block_width) // 2, 0)

        top_padding = max((term_height - len(wrapped)) // 2 - 2, 0)
        print("\n" * top_padding, end="")

        for line in wrapped:
            print((" " * left_padding) + line)

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

        print("\n" * footnote_gap, end="")

        if footnote_wrapped:
            footnote_width = max((self.visible_len(line) for line in footnote_wrapped), default=0)
            footnote_left_padding = max((term_width - footnote_width) // 2, 0) if center_footnotes else 0

            for line in footnote_wrapped:
                print((" " * footnote_left_padding) + line)

        return input(actual_prompt)