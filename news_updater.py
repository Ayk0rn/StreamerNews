import urllib.request
import xml.etree.ElementTree as ET
import html
from datetime import datetime
from email.utils import parsedate_to_datetime

FEEDS = [
    "https://www.twitch.tv/blog/feed/",
]

KEYWORDS = [
    "streamer",
    "streaming",
    "twitch",
    "youtube",
    "kick",
    "creator",
    "livestream",
]

MAX_ARTICLES = 20


def get_feed(url):
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "StreamerNews/1.0"}
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def clean_text(text):
    if not text:
        return ""
    return html.unescape(text).strip()


def get_articles():
    articles = []

    for feed_url in FEEDS:
        try:
            data = get_feed(feed_url)
            root = ET.fromstring(data)

            for item in root.findall(".//item"):
                title = item.findtext("title", "")
                link = item.findtext("link", "")
                description = item.findtext("description", "")
                pub_date = item.findtext("pubDate", "")

                title = clean_text(title)
                link = clean_text(link)
                description = clean_text(description)

                text = (title + " " + description).lower()

                if not any(keyword in text for keyword in KEYWORDS):
                    continue

                try:
                    date = parsedate_to_datetime(pub_date)
                except Exception:
                    date = datetime.now().astimezone()

                articles.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "date": date,
                })

        except Exception as error:
            print(f"Could not read {feed_url}: {error}")

    # Remove duplicate links
    unique = {}

    for article in articles:
        unique[article["link"]] = article

    articles = list(unique.values())

    # Newest first
    articles.sort(
        key=lambda article: article["date"],
        reverse=True
    )

    return articles[:MAX_ARTICLES]


def make_page(articles):
    cards = ""

    for article in articles:
        title = html.escape(article["title"])
        link = html.escape(article["link"], quote=True)
        description = html.escape(article["description"][:250])

        date = article["date"].strftime("%d %b %Y, %H:%M")

        cards += f"""
        <article class="article">
            <h2>
                <a href="{link}" target="_blank" rel="noopener noreferrer">
                    {title}
                </a>
            </h2>

            <p class="date">{date}</p>

            <p>{description}</p>

            <a class="read" href="{link}" target="_blank"
               rel="noopener noreferrer">
                Read original article →
            </a>
        </article>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <title>Latest Streamer News</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: auto;
            padding: 30px 20px;
            background: #f4f4f4;
        }}

        h1 {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .article {{
            background: white;
            padding: 22px;
            margin-bottom: 18px;
            border-radius: 12px;
        }}

        .article h2 {{
            margin-top: 0;
        }}

        .article h2 a {{
            color: #111;
            text-decoration: none;
        }}

        .article h2 a:hover {{
            text-decoration: underline;
        }}

        .date {{
            color: #777;
            font-size: 14px;
        }}

        .read {{
            font-weight: bold;
            text-decoration: none;
        }}
    </style>
</head>

<body>

<h1>Latest Streamer News</h1>

{cards}

</body>
</html>
"""


if __name__ == "__main__":
    articles = get_articles()

    page = make_page(articles)

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(page)

    print(f"Updated site with {len(articles)} articles.")
