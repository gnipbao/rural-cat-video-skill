#!/usr/bin/env python3
"""Build UTF-8 SRT subtitles from a validated seconds-based JSON timeline."""

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import sys
import tempfile
import os


class InputError(ValueError):
    """A user-facing error which contains no file paths or caption contents."""


class SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, "Invalid command. Run build_srt.py --help for usage.\n")


def reject_constant(value):
    raise InputError("JSON numbers must be finite.")


def seconds(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise InputError(f"{label} must be a finite number in seconds.")
    number = Decimal(value)
    if not number.is_finite():
        raise InputError(f"{label} must be a finite number in seconds.")
    return number


def milliseconds(value):
    return int((value * 1000).to_integral_value(rounding=ROUND_HALF_UP))


def timestamp(value):
    hours, remainder = divmod(value, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def render(data):
    if not isinstance(data, dict):
        raise InputError("The JSON root must be an object.")
    duration = seconds(data.get("duration"), "duration")
    if duration <= 0:
        raise InputError("duration must be greater than zero.")
    captions = data.get("captions")
    if not isinstance(captions, list) or not captions:
        raise InputError("captions must be a non-empty array.")

    cues = []
    previous_end = Decimal(0)
    previous_end_ms = 0
    duration_ms = milliseconds(duration)
    for index, cue in enumerate(captions, 1):
        label = f"Caption {index}"
        if not isinstance(cue, dict):
            raise InputError(f"{label} must be an object.")
        start = seconds(cue.get("start"), f"{label} start")
        end = seconds(cue.get("end"), f"{label} end")
        if not (0 <= start < end <= duration):
            raise InputError(f"{label} requires 0 <= start < end <= duration.")
        if start < previous_end:
            raise InputError(f"{label} overlaps or is out of order.")

        start_ms, end_ms = milliseconds(start), milliseconds(end)
        if not (0 <= start_ms < end_ms <= duration_ms):
            raise InputError(f"{label} has no valid interval after millisecond rounding.")
        if start_ms < previous_end_ms:
            raise InputError(f"{label} overlaps after millisecond rounding.")

        text = cue.get("text")
        if not isinstance(text, str) or not text.strip():
            raise InputError(f"{label} requires non-empty text.")
        text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
        if any(not line.strip() for line in text.split("\n")):
            raise InputError(f"{label} cannot contain blank lines inside its text.")
        if any(ord(char) < 32 and char not in "\n\t" for char in text):
            raise InputError(f"{label} contains unsupported control characters.")

        cues.append(f"{index}\n{timestamp(start_ms)} --> {timestamp(end_ms)}\n{text}\n")
        previous_end, previous_end_ms = end, end_ms
    return "\n".join(cues) + "\n", len(cues)


def write_output(path, content, force):
    if not force:
        # Exclusive creation prevents accidental replacement, including symlinks.
        with path.open("x", encoding="utf-8", newline="\n") as output:
            output.write(content)
        return

    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=".srt-", suffix=".tmp", delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = SafeArgumentParser(
        prog="build_srt.py",
        description="Convert duration/captions JSON (seconds) into UTF-8 SRT."
    )
    parser.add_argument("input", type=Path, help="Input JSON file")
    parser.add_argument("--output", type=Path, required=True, help="Output SRT file")
    parser.add_argument("--force", action="store_true", help="Replace an existing output")
    args = parser.parse_args(argv)

    try:
        if args.input.resolve() == args.output.resolve():
            raise InputError("Input and output must be different files.")
        data = json.loads(
            args.input.read_text(encoding="utf-8-sig"),
            parse_float=Decimal, parse_constant=reject_constant
        )
        content, count = render(data)
        write_output(args.output, content, args.force)
    except FileExistsError:
        print("Output already exists. Choose another file or use --force.", file=sys.stderr)
        return 2
    except InputError as error:
        print(str(error), file=sys.stderr)
        return 2
    except (json.JSONDecodeError, UnicodeError):
        print("Input must be valid UTF-8 JSON.", file=sys.stderr)
        return 2
    except (ArithmeticError, ValueError):
        print("Input numbers or file arguments cannot be processed.", file=sys.stderr)
        return 2
    except OSError:
        print("Unable to read input or write output. Check paths and permissions.", file=sys.stderr)
        return 1

    print(f"Created SRT with {count} captions.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
