import shutil
import random
import textwrap
import time
import typing as t

class TextUtility:
    def __init__(
        self,
        rng=random.Random,
    ):
        self.rng = rng

    def get_term_width(self) -> int:
        return shutil.get_terminal_size(fallback=(80, 24)).columns

    def get_term_height(self) -> int:
        return shutil.get_terminal_size(fallback=(80, 24)).lines
    
    def get_horizontal_padding(
            self,
            term_width: int,
            s: str
        ) -> int:
        padding = int((term_width - len(s)) // 2)
        if padding < 0:
            padding = 0
        return padding
    
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
        print("\033[2J\033[H", end="")

    def clear_lines(self, n: int):
      for _ in range(n):
        print("\033[F\033[K", end="")

    def wrap_lines(
        self,
        lines: t.List[str],
        width: int
    ) -> t.List[str]:
        """
        Wrap long lines so horizontal centering stays sane even in narrow terminals.
        Blank lines are preserved.
        """
        usable_width = max(width, 20)
        wrapped: t.List[str] = []

        print("wrapped")
        for line in lines:
            print(line)
            if line == "":
                wrapped.append("")
                continue

            wrapped.extend(
                textwrap.wrap(
                    line,
                    width=usable_width,
                    break_long_words=False,
                    break_on_hyphens=False,
                ) or [""]
            )

        return wrapped

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
    
    def center_text(
        self,
        line: t.Optional[str] = None,
        lines: t.Optional[t.List[str]] = None,
        max_width: t.Optional[int] = None,
        vertical: bool = True,
    ) -> str:
        """
        Return text centered horizontally, and optionally vertically, in the terminal.

        - Pass either line="..." or lines=["...", "..."]
        - Long lines are wrapped before centering
        - Uses terminal-size fallback so redirected output/tests don't crash
        """
        if line is not None and lines is not None:
            raise ValueError("Pass either line or lines, not both.")

        if line is None and lines is None:
            return ""

        raw_lines = [line] if line is not None else list(lines or [])

        term_width = self.get_term_width()
        term_height = self.get_term_height()

        rendered_lines = self.wrap_lines(raw_lines, self.get_content_width(max_width))

        top_padding = self.get_vertical_padding(term_height, rendered_lines) if vertical else 0

        output_lines: t.List[str] = []
        output_lines.extend("" for _ in range(top_padding))

        for rendered_line in rendered_lines:
            left_padding = self.get_horizontal_padding(term_width, rendered_line)
            output_lines.append((" " * left_padding) + rendered_line)

        output_lines.extend("" for _ in range(top_padding))

        return "\n".join(output_lines)
    
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
        for _ in range(iterations):
            self.clear_screen()
            print()
            time.sleep(time_in_s)
            print(msg)
            time.sleep(time_in_s)

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

