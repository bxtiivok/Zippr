# Imports

from zipfile import ZipFile, ZIP_DEFLATED
from argparse import ArgumentParser, HelpFormatter
from pathlib import Path
from typing import Iterator, TypedDict
from glob import glob
from os import getcwd
from sys import version_info, exit
from modules.palette import Palette

# Main

ver = [0, 0, 0]

parser = ArgumentParser("zippr",
    usage=f"{Palette.bold}{Palette.magenta}zippr{Palette.reset} {Palette.green}<folderpath>{Palette.reset} [{Palette.green}options{Palette.reset}]",
    description="Creates a .zip archive, that excludes items listed in .zipignore files",
    add_help=False,
    formatter_class=lambda prog: HelpFormatter(prog, max_help_position=40)
)

parser.add_argument(
    "-h, --help",
    help="Prints this help message",
    action="help",
)
parser.add_argument(
    "-v", "--version",
    help="Prints the version of Zippr",
    action="version",
    version=f"Zippr v{ver[0]}.{ver[1]}{'.' + str(ver[2]) if ver[2] != 0 else ''} on Python {version_info.major}.{version_info.minor}.{version_info.micro}",
)
parser.add_argument(
    "inpath",
    help="The relative or absolute path to a folder",
    metavar="<folderpath>",
    type=Path
)
parser.add_argument(
    "-o", "--out",
    dest = "outpath",
    help="The output path (default: <folderpath>.zip)",
    metavar="<filepath>",
    default=None,
    type=Path
)
parser.add_argument(
    "-f", "--force",
    help="Overwrites existing files instead of raising an exception",
    action="store_true",
)
parser.add_argument(
    "-c", "--compression",
    help="The level of compression (default: 6)",
    metavar="<int 0-9>",
    default=6,
    type=int,
)
parser.add_argument(
    "-i", "--inclusive",
    help="Includes hidden files",
    action="store_true",
)
parser.add_argument(
    "-n", "--no-ignore",
    help="Doesn't parse .zipignore files",
    action="store_true",
)
parser.add_argument(
    "-g", "--git-ignore",
    help="Parses .gitignore files aswell",
    action="store_true",
)
parser.add_argument(
    "-q", "--quiet",
    help="Hides the output instead of printing it",
    action="store_true",
)

class Args(TypedDict):
    inpath: Path
    outpath: Path
    force: bool
    compression: int
    inclusive: bool
    no_ignore: bool
    git_ignore: bool
    quiet: bool

args: Args = vars(parser.parse_args())

if not args['inpath'].is_dir():
    parser.error(f"argument 1: invalid Path value: {str(args['inpath'])!r}")

if args['outpath'] is None:
    args['outpath'] = Path(f"{args['inpath'].name}.zip")

print(f"{Palette.magenta}args{Palette.reset}", str(args)
    .replace("{", f"{{\n    {Palette.green}",)
    .replace("}", f"\n{Palette.reset}}}")
    .replace(": ", f"{Palette.reset}: {Palette.red}")
    .replace(", ", f"{Palette.reset},\n    {Palette.green}")
    .replace("(", f"{Palette.reset}<{Palette.green}")
    .replace(")", f"{Palette.reset}>")
)