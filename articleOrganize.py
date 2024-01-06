from pathlib import Path
from shutil import copy, copytree
from bs4 import BeautifulSoup, Tag
import json
import datetime


# import all articles and save

articles = []
block_tags = [
    "img",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
]

# create new articles parsed directory
main = Path("./articles")
parsed = Path("./articles_parsed")
if (not parsed.exists()):
    parsed.mkdir()
if (not parsed.is_dir()):
    parsed.unlink()
    parsed.mkdir()

for file in main.iterdir():
    soup = BeautifulSoup((file / "main.html").read_text(), "html.parser")
    date = soup.find(name="head").find("date").attrs

    # keep a temp body as a buffer for each paragraph. When the temp_body encounters something that breaks a paragraph (block tag or double newline), it flushes to body_new as a p object.
    body = soup.find(name="body")
    body_new = ""
    temp_body = ""

    body_new += "<header>" + soup.find(name="head").decode_contents().replace(
        "\n", "") + "</header>"

    for child in body.contents:
        if isinstance(child, str):
            ctemp = child.split("\\n")
            lines = []
            for c in ctemp:
                lines += c.split("\n\n")
            for line in lines:
                if (line.strip() == ""):
                    continue
                line_new = line.strip().replace('\n', '')
                body_new += f"<p>{temp_body + line_new}</p>"
                temp_body = ""
        elif isinstance(child, Tag):
            if (child.has_attr("block") or child.name in block_tags):
                if (temp_body != ""):
                    body_new += f"<p>{temp_body}</p>"
                body_new += str(child)
                temp_body = ""
            else:
                temp_body += str(child)
    body_new += f"<p>{temp_body}</p>"
    # bodytemp = body.decode_contents().split("\\n")
    # body = []
    # for x in bodytemp:
    #     body += x.split("\n\n")
    # for line in body:
    #     line = line.strip()
    #     if (line == ""):
    #         continue
    #     linesoup = BeautifulSoup(line, "html.parser")
    #     lineparsed = ""
    #     hasText = False
    #     for child in linesoup.contents:
    #         if isinstance(child, str):
    #             hasText = True
    #             lineparsed += str(child).strip()
    #         elif isinstance(child, Tag):
    #             lineparsed += str(child)
    #     if (hasText):
    #         temp = lineparsed.strip().replace('\n', '').replace('\r', '')
    #         body_new = body_new + f"<p>{temp}</p>"
    #     else:
    #         body_new = body_new + lineparsed.strip().replace("\n",
    #                                                          "").replace("\r", "")

    # generate object
    articles.append({"title": soup.find(name="head").find("title").text,
                     # swap their parent directories
                     "cover": str((file.parents[1] / "articles_parsed" / file.name / soup.find(name="head").find("cover").attrs["src"])),
                     "main": str(file.parents[1] / "articles_parsed" / file.name / "main.html"),
                     "date": datetime.date(int(date["year"]),
                                           int(date["month"]),
                                           int(date["day"])),
                    "author": soup.find(name="head").find("author").text})
    # copy into parsed
    copytree(file, parsed / file.name, dirs_exist_ok=True)
    with open(parsed / file.name / "main.html", "w") as f:
        f.write(body_new)

# export into json


def key(element):
    return element["date"]


articles.sort(key=key, reverse=True)

# convert datetime into string representation
for i, article in enumerate(articles):
    temp = articles[i]
    temp["date"] = str(temp["date"])
    articles[i] = temp

jsonString = json.dumps(articles)

with open("articles.json", "w") as file:
    file.write(jsonString)
