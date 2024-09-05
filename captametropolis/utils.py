import ctypes
import os
import shutil
import subprocess as sp
import sys
import winreg as wr

from fontTools.ttLib import TTFont
from lxml import etree as ET

_IMGMGCK_DOCTYPE = """
<!DOCTYPE typemap [
  <!ELEMENT typemap (type)+>
  <!ELEMENT type (#PCDATA)>
  <!ELEMENT include (#PCDATA)>
  <!ATTLIST type name CDATA #REQUIRED>
  <!ATTLIST type fullname CDATA #IMPLIED>
  <!ATTLIST type family CDATA #IMPLIED>
  <!ATTLIST type foundry CDATA #IMPLIED>
  <!ATTLIST type weight CDATA #IMPLIED>
  <!ATTLIST type style CDATA #IMPLIED>
  <!ATTLIST type stretch CDATA #IMPLIED>
  <!ATTLIST type format CDATA #IMPLIED>
  <!ATTLIST type metrics CDATA #IMPLIED>
  <!ATTLIST type glyphs CDATA #REQUIRED>
  <!ATTLIST type version CDATA #IMPLIED>
  <!ATTLIST include file CDATA #REQUIRED>
]>
"""


def is_admin():
    if os.name == "nt":
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    elif os.name == "posix":
        return os.getuid() == 0
    else:
        return False


def run_as_admin(verbose: bool = False):
    if verbose:
        print("Checking admin privileges...")
    if not is_admin():
        if verbose:
            print("WARNING: You need admin privileges to run this script.")
        if os.name == "posix":
            os.execvp("sudo", ["sudo", "python3"] + sys.argv)
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        sys.exit(0)
    else:
        if verbose:
            print("Admin privileges granted.")


def detect_local_whisper(print_info):
    try:
        import whisper

        use_local_whisper = True
        if print_info:
            print("Using local whisper model...")
    except ImportError:
        use_local_whisper = False
        if print_info:
            print("Using OpenAI Whisper API...")

    return use_local_whisper


def ffmpeg_installed() -> bool:
    return shutil.which("ffmpeg") is not None


def imagemagick_directory() -> str:
    binary = None
    if os.name == "nt":
        try:
            key = wr.OpenKey(wr.HKEY_LOCAL_MACHINE, "SOFTWARE\\ImageMagick\\Current")
            binary = wr.QueryValueEx(key, "BinPath")[0]
            key.Close()
            return binary
        except:
            return "unset"
    else:
        try:
            result = sp.run(
                ["which", "convert"],
                capture_output=True,
                text=True,
                check=True,
            )
            convert_path = result.stdout.strip()

            if convert_path:
                imagemagick_dir = os.path.dirname(convert_path)
                return imagemagick_dir
            else:
                return "unset"
        except sp.CalledProcessError:
            return "unset"


def imagemagick_binary() -> str:
    def try_cmd(cmd):
        try:
            popen_params = {
                "stdout": sp.PIPE,
                "stderr": sp.PIPE,
                "stdin": sp.DEVNULL,
            }

            if os.name == "nt":
                popen_params["creationflags"] = 0x08000000

            proc = sp.Popen(cmd, **popen_params)  # type: ignore
            proc.communicate()
        except Exception as err:
            return False, err
        else:
            return True, None

    if os.name == "nt":
        imgmgck_directory = imagemagick_directory()
        if imgmgck_directory == "unset":
            return "unset"
        imgmgck_executable = (
            "magick.exe" if "ImageMagick-7" in imgmgck_directory else "convert.exe"
        )
        imgmgck_binary = os.path.join(imgmgck_directory, imgmgck_executable)
        if os.path.exists(imgmgck_binary):
            return imgmgck_binary
        else:
            return "unset"
    elif try_cmd(["convert"])[0]:
        return "convert"
    else:
        return "unset"


def get_font_info(font_path: str) -> dict:
    font = TTFont(font_path)

    name_table = font["name"]
    font_info = {}

    name_id_map = {
        1: "Font Family",
        2: "Font Subfamily",
        4: "Full Font Name",
        5: "Version",
        6: "Postscript Name",
        7: "Italic Angle",
    }

    for record in name_table.names:  # type: ignore
        name_id = record.nameID
        if name_id in name_id_map:
            name_type = name_id_map[name_id]
            font_info[name_type] = record.toUnicode()

    if "OS/2" in font:
        os2_table = font["OS/2"]
        weight = os2_table.usWeightClass  # type: ignore
        stretch = os2_table.usWidthClass  # type: ignore

        font_info["Weight"] = weight
        stretch_map = {
            1: "UltraCondensed",
            2: "ExtraCondensed",
            3: "Condensed",
            4: "SemiCondensed",
            5: "Normal",
            6: "SemiExpanded",
            7: "Expanded",
            8: "ExtraExpanded",
            9: "UltraExpanded",
        }
        font_info["Stretch"] = stretch_map[stretch].lower()

    return font_info


def _inject_font_into_imagemagick(fontpath: str):
    if not os.path.exists(fontpath):
        raise FileNotFoundError(f"Font file not found: {fontpath}")

    font_container = os.path.join(imagemagick_directory(), "type-ghostscript.xml")
    if not os.path.exists(font_container):
        raise FileNotFoundError("Font container not found")

    font_info = get_font_info(fontpath)

    tree = ET.parse(font_container)
    root = tree.getroot()

    for font in root.findall("type"):
        if font.attrib["fullname"] == font_info["Full Font Name"]:
            return font_info["Full Font Name"]

    new_font_type = ET.Element(
        "type",
        {
            "name": font_info["Full Font Name"],
            "fullname": font_info["Full Font Name"],
            "family": font_info["Font Family"],
            "style": "normal",
            "weight": str(font_info["Weight"]),
            "stretch": font_info["Stretch"],
            "format": "type1",
            "metrics": fontpath,
            "glyphs": fontpath,
        },
    )
    root.append(new_font_type)
    tree.write(
        font_container, encoding="utf-8", xml_declaration=True, doctype=_IMGMGCK_DOCTYPE
    )

    return font_info["Full Font Name"]


def get_font_path(font) -> tuple[str, str]:
    if not font.endswith(".ttf"):
        raise ValueError("Only TrueType fonts are currently supported")

    if os.path.exists(font):
        injected_font_name = _inject_font_into_imagemagick(os.path.abspath(font))
        return os.path.abspath(font), injected_font_name

    dirname = os.path.dirname(__file__)
    font = os.path.join(dirname, "assets", "fonts", font)

    if not os.path.exists(font):
        raise FileNotFoundError(f"Font '{font}' not found")

    injected_font_name = _inject_font_into_imagemagick(os.path.abspath(font))
    return os.path.abspath(font), injected_font_name


def _detach_font_from_imagemagick(font_name: str) -> None:
    font_container = os.path.join(imagemagick_directory(), "type-ghostscript.xml")
    if not os.path.exists(font_container):
        raise FileNotFoundError("Font container not found")

    try:
        tree = ET.parse(font_container)
        root = tree.getroot()
        for font in root.findall("type"):
            if font.attrib["fullname"] == font_name:
                root.remove(font)
                break
        tree.write(
            font_container,
            encoding="utf-8",
            xml_declaration=True,
            doctype=_IMGMGCK_DOCTYPE,
        )
    except Exception as e:
        raise e
