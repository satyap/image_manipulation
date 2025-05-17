import argparse

import piexif
from PIL import Image

ANNOTATE_COMMAND = "ima-annotate"


def cli_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prefix", required=True)
    parser.add_argument("-x", "--xml", dest="xml", action="store_true")
    parser.add_argument("files", nargs="*")
    return parser.parse_args()


def annotation(file: str, prefix: str, xml: bool) -> str:
    """
    Returns CLI command to annotate this file. Command will put test in the image and in image metadata, and if needed,
    will print out an XML blob for the web site.
    :param file:
    :param prefix:
    :param xml:
    :return:
    """
    date, newfile = new_filename(file, prefix)
    out = f"""{ANNOTATE_COMMAND} \\
    -t " {date} - " \\
    -i {file} -o {newfile}
"""
    if xml:
        out += f"""cat <<EOT > {newfile}.xml
<?xml version="1.0" encoding="UTF-8"?><image><description>
      <field name="description"> </field>
      <field name="title"> </field>
      <field name="date"> {date} </field>
   </description> <bins> </bins> <exif> </exif> </image>
EOT
"""
    return out


def new_filename(file: str, prefix: str) -> tuple[str, str]:
    """
    Returns new file name. Drops the year because I place files in a folder by year. Names the new file by month, day,
    hour, and minute. I don't need seconds-precision. In case of name collision I can rename the files that are output.
    :param file:
    :param prefix:
    :return:
    """
    img = Image.open(file)
    exif_info = img.info.get("exif")
    if exif_info:
        exif_data = piexif.load(exif_info)
        datetime = exif_data["Exif"].get(piexif.ExifIFD.DateTimeOriginal)
        if not datetime:
            datetime = exif_data["0th"].get(piexif.ImageIFD.DateTime)
        datetime = datetime.decode()
    elif file.startswith("IMG-") and "-WA" in file:  # whatsapp image
        d = file.split("-")
        time = d[2][2:6]
        datetime = f"{d[1]} {time}"
    else:
        datetime = ""
    date, time = datetime.replace(":", "").split()
    short_date = date[4:]
    time = time[:4]
    newfile = f"{prefix}{short_date}{time}.jpg"
    return date, newfile


def main() -> None:
    args = cli_args()
    for file in args.files:
        print(annotation(file, args.prefix, args.xml))


if __name__ == "__main__":
    main()
