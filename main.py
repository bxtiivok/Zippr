## Imports

from zipfile import ZipFile, ZIP_DEFLATED
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from pathlib import Path
from typing import TypedDict
from os import remove
from sys import version_info
from modules.palette import Palette

## Main

ver = [1, 0, 1]

class Formatter(RawDescriptionHelpFormatter):

    def __init__(self, prog, indent_increment=4, max_help_position=40, width=None, color=True):
        super().__init__(prog, indent_increment, max_help_position, width, color)

parser = ArgumentParser("Zippr",
    usage=f"{Palette.bold}{Palette.magenta}zippr{Palette.reset} {Palette.green}<folderpath>{Palette.reset} [{Palette.green}options{Palette.reset}]",
    description=
    """
    Creates a .zip archive, excluding items listed inside .zipignore files.

    .zipignore files behave the same way .gitignore files do: they allow you to
    filter out certain folders or files, making sure files you wouldn't share
    with others 
    """.replace("    ", ""),
    add_help=False,
    formatter_class=Formatter
    
)

# Arguments

parser.add_argument(
    "-h", "--help",
    help="Prints this help message",
    action="help",
)
parser.add_argument(
    "-v", "--version",
    help="Prints the version of the program",
    action="version",
    version=f"%(prog)s v{ver[0]}.{ver[1]}{'.' + str(ver[2]) if ver[2] != 0 else ''} on Python {version_info.major}.{version_info.minor}.{version_info.micro}",
)
parser.add_argument(
    "inpath",
    help="The relative or absolute path to a folder",
    metavar="<folderpath>",
    type=Path,
)
parser.add_argument(
    "-o", "--out",
    dest = "outpath",
    help="The output path (default: <folderpath>.zip)",
    metavar="<filepath>",
    default=None,
    type=Path,
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
    "-n", "--no-ignore",
    help="Don't parse .zipignore files",
    action="store_true",
)
parser.add_argument(
    "-g", "--git-ignore",
    help="Parse .gitignore files too",
    action="store_true",
)
parser.add_argument(
    "-r", "--remove",
    help="Remove the folder after creating the archive",
    action="store_true",
)

class Args(TypedDict):
    inpath: Path
    outpath: Path
    force: bool
    compression: int
    no_ignore: bool
    git_ignore: bool
    remove: bool

args: Args = vars(parser.parse_args())

# Checks & Resolves

args['inpath'] = args['inpath'].resolve()

if not args['inpath'].is_dir():
    parser.error(f"argument 1: path '{str(args['inpath'])}' doesn't point to a folder")

if not (0 <= args["compression"] <= 9):
    parser.error(f"argument -c/--compression: int value '{args['compression']}' out of range 0-9")

if args['outpath'] is None:
    args['outpath'] = args['inpath'].parent / f"{args['inpath'].name}.zip"
elif args['outpath'].is_dir():
    args['outpath'] = args['outpath'] / f"{args['inpath'].name}.zip"

if args['outpath'].exists() and not args['force']:
    parser.error(f"argument -o/--out: file '{str(args['outpath'])}' already exists")

if not args['outpath'].name.endswith(".zip"):
    args['outpath'] = args['outpath'].with_name(args['outpath'].name + ".zip")

args['outpath'] = args['outpath'].resolve()

# Filtering

def filter() -> list[Path]:

    # Collecting
    
    total = [f.resolve() for f in args['inpath'].rglob("*")]
    files = total.copy()
    
    for f in total:

        # Filter .zipignores & .gitignores (if enabled)

        if (not f.is_file()):
            continue
        if ((args['no_ignore']) or not f.name.endswith(".zipignore")) and ((not args['git_ignore']) or (not f.name.endswith(".gitignore"))):
            continue

        # Patterns

        root = f.parent
        lines = []
        for line in f.read_text().splitlines():
            if line.startswith("#") or (line.strip() == ""):
                continue
            lines.append(line.strip())
        
        # Remove matched files & folders

        for line in lines:
            for m in root.rglob(line):
                m = m.resolve()
                
                if m.is_file():
                    if m in files:
                        files.remove(m)
                    continue    
                if not m.is_dir():
                    continue
                
                for r in files.copy():
                    if (r not in files) or (not r.is_relative_to(m)):
                        continue
                    files.remove(r)
    
    return files

files = filter()

# Archiving

with ZipFile(args['outpath'], "w", compression=ZIP_DEFLATED, compresslevel=args['compression']) as z:
    
    for f in files:
        z.write(f, f.relative_to(args['inpath'].parent))
    
    if args['remove']:
        remove(args['inpath'])

# :3