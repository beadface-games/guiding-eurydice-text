import os
import time
import typing as t

class TextUtility:
    def __init__(self):
        pass

    def get_term_width(self) -> int:
                return os.get_terminal_size().columns

    def get_term_height(self) -> int:
        return os.get_terminal_size().lines
    
    def get_horizontal_padding(
            self,
            term_width: int,
            s: str
        ) -> int:
        padding = int((term_width - len(s)) / 2)
        if padding < 0:
            padding = 0
        return int(padding * 0.9)
    
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
        
        padding = int((term_height - actual_lines) / 2)
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

    
    def center_text(
        self,
        line: t.Optional[str]=None,
        lines: t.Optional[t.List[str]]=None,
    ) -> str:
        res = ""
        
        if line and (not lines):
            horizontal_padding = self.get_horizontal_padding(self.get_term_width(), line)
            vertical_padding = self.get_vertical_padding(self.get_term_height(), [line])

            res = (
                "\n" * vertical_padding +
                " " * horizontal_padding +
                line +
                " " * horizontal_padding +
                "\n" * vertical_padding
            )
        elif lines and (not line):
            longest_line = self.get_longest_str(lines)
            horizontal_padding = self.get_horizontal_padding(self.get_term_width(), longest_line)
            vertical_padding = self.get_vertical_padding(self.get_term_height(), lines)

            res =  ("\n" * vertical_padding) + (" " * horizontal_padding)

            for line in lines:
                res += (" " * horizontal_padding) + (" " * int((len(longest_line) - len(line)) / 2)) + line + "\n"
            
            res += (" " * horizontal_padding) + ("\n" * vertical_padding)
        
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