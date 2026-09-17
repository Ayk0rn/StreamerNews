import urllib.request
import xml.etree.ElementTree as ET
import html
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = [
    "https://streamer.guide/rss.xml",
]

KEYWORDS = [
    "streamer",
    "streaming",
    "twitch",
    "youtube",
    "kick",
    "creator",
    "livestream",
    "live stream",
    "content creator",
]

MAX_ARTICLES = 20


def get_feed(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 StreamerNews/1.0"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def clean_text(text):
    if not text:
        return ""

    return html.unescape(text).strip()


def get_articles():
    articles = []

    for feed_url in FEEDS:
        print(f"Reading: {feed_url}")

        try:
            data = get_feed(feed_url)
            root = ET.fromstring(data)

            for item in root.findall(".//item"):
                title = clean_text(
                    item.findtext("title", "")
                )

                link = clean_text(
                    item.findtext("link", "")
                )

                description = clean_text(
                    item.findtext("description", "")
                )

                pub_date = clean_text(
                    item.findtext("pubDate", "")
                )

                text = (
                    title + " " + description
                ).lower()

                if not any(
                    keyword in text
                    for keyword in KEYWORDS
                ):
                    continue

                try:
                    date = parsedate_to_datetime(
                        pub_date
                    )

                    if date.tzinfo is None:
                        date = date.replace(
                            tzinfo=timezone.utc
                        )

                except Exception:
                    date = datetime.now(
                        timezone.utc
                    )

                if title and link:
                    articles.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "date": date,
                    })

        except Exception as error:
            print(
                f"Could not read {feed_url}: {error}"
            )

    # Remove duplicate URLs
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

    if not articles:
        cards = """
        <div class="empty">
            No recent streamer news found.
        </div>
        """

    for article in articles:

        title = html.escape(
            article["title"]
        )

        link = html.escape(
            article["link"],
            quote=True
        )

        description = html.escape(
            article["description"][:300]
        )

        date = article["date"].strftime(
            "%d %b %Y · %H:%M"
        )

        cards += f"""
        <article class="article">

            <h2>
                <a href="{link}"
                   target="_blank"
                   rel="noopener noreferrer">
                    {title}
                </a>
            </h2>

            <div class="date">
                {date}
            </div>

            <p>
                {description}
            </p>

            <a class="read"
               href="{link}"
               target="_blank"
               rel="noopener noreferrer">
                Read original article →
            </a>

        </article>
        """

    return f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Latest Streamer News</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    padding: 30px 20px;
    background: #f4f4f4;
    font-family: Arial, sans-serif;
}}

.container {{
    max-width: 900px;
    margin: auto;
}}

h1 {{
    text-align: center;
    margin-bottom: 35px;
}}

.article {{
    background: white;
    padding: 24px;
    margin-bottom: 18px;
    border-radius: 14px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}}

.article h2 {{
    margin: 0 0 8px;
    font-size: 22px;
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
    margin-bottom: 15px;
}}

.article p {{
    line-height: 1.5;
}}

.read {{
    font-weight: bold;
    text-decoration: none;
}}

.empty {{
    background: white;
    padding: 30px;
    border-radius: 14px;
    text-align: center;
}}

</style>

</head>

<body>

<div class="container">

<h1>Latest Streamer News</h1>

{cards}

</div>

</body>

</html>
"""


if __name__ == "__main__":

    articles = get_articles()

    print(
        f"Found {len(articles)} matching articles."
    )

    page = make_page(articles)

    with open(
        "index.html",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(page)

    print(
        f"Updated site with {len(articles)} articles."
    )
