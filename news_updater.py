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

MAX_ARTICLES = 100


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
                    date = parsedate_to_datetime(pub_date)

                    if date.tzinfo is None:
                        date = date.replace(
                            tzinfo=timezone.utc
                        )

                except Exception:
                    date = datetime.now(timezone.utc)

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

    unique = {}

    for article in articles:
        unique[article["link"]] = article

    articles = list(unique.values())

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

        title = html.escape(article["title"])
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

            <div class="article-top">
                <span class="tag">STREAMER NEWS</span>
                <span class="date">{date}</span>
            </div>

            <h2>
                <a href="{link}"
                   target="_blank"
                   rel="noopener noreferrer">
                    {title}
                </a>
            </h2>

            <p>{description}</p>

            <a class="read"
               href="{link}"
               target="_blank"
               rel="noopener noreferrer">
                READ ORIGINAL ARTICLE
                <span>→</span>
            </a>

        </article>
        """

    return f"""<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<meta name="description"
      content="The latest streamer and streaming news.">

<title>Streamer News</title>

<style>

* {{
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    margin: 0;
    min-height: 100vh;

    background:
        radial-gradient(
            circle at top,
            #17112b 0%,
            #09090d 42%,
            #050507 100%
        );

    color: #f5f5f7;

    font-family:
        Arial,
        Helvetica,
        sans-serif;
}}

body::before {{
    content: "";
    position: fixed;
    inset: 0;

    background-image:
        linear-gradient(
            rgba(255,255,255,0.02) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(255,255,255,0.02) 1px,
            transparent 1px
        );

    background-size: 40px 40px;

    pointer-events: none;
}}

.container {{
    position: relative;
    max-width: 1000px;
    margin: auto;
    padding: 35px 18px 70px;
}}

.header {{
    text-align: center;
    margin-bottom: 42px;
}}

.logo {{
    font-size: clamp(32px, 7vw, 58px);
    font-weight: 900;
    letter-spacing: -2px;

    margin: 0;
}}

.logo span {{
    color: #9b6cff;
}}

.subtitle {{
    color: #9a9aa6;
    margin-top: 10px;
    font-size: 15px;
}}

.status {{
    display: inline-flex;
    align-items: center;
    gap: 8px;

    margin-top: 18px;
    padding: 7px 13px;

    border: 1px solid #252530;
    border-radius: 999px;

    background: rgba(255,255,255,0.03);

    color: #b9b9c4;
    font-size: 12px;
    font-weight: bold;
}}

.status-dot {{
    width: 7px;
    height: 7px;

    border-radius: 50%;
    background: #65e58b;

    box-shadow:
        0 0 10px #65e58b;
}}

.section-title {{
    display: flex;
    justify-content: space-between;
    align-items: center;

    margin-bottom: 16px;
}}

.section-title h1 {{
    font-size: 18px;
    margin: 0;
}}

.count {{
    color: #777784;
    font-size: 13px;
}}

.article {{
    position: relative;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,0.055),
            rgba(255,255,255,0.025)
        );

    border: 1px solid #252530;
    border-radius: 16px;

    padding: 22px;
    margin-bottom: 14px;

    transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        background 0.18s ease;
}}

.article:hover {{
    transform: translateY(-2px);

    border-color: #5d42a0;

    background:
        linear-gradient(
            145deg,
            rgba(155,108,255,0.10),
            rgba(255,255,255,0.03)
        );
}}

.article-top {{
    display: flex;
    justify-content: space-between;
    gap: 15px;

    margin-bottom: 12px;
}}

.tag {{
    color: #a982ff;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}}

.date {{
    color: #777784;
    font-size: 12px;
}}

.article h2 {{
    margin: 0;

    font-size: clamp(19px, 3vw, 25px);
    line-height: 1.25;
}}

.article h2 a {{
    color: #f4f4f7;
    text-decoration: none;
}}

.article h2 a:hover {{
    color: #b99aff;
}}

.article p {{
    color: #aaaab5;
    line-height: 1.55;
    font-size: 14px;
    margin: 13px 0 19px;
}}

.read {{
    color: #a982ff;
    text-decoration: none;

    font-size: 12px;
    font-weight: 900;
    letter-spacing: 0.7px;
}}

.read span {{
    margin-left: 5px;
}}

.empty {{
    padding: 50px 20px;
    text-align: center;

    color: #888895;

    border: 1px solid #252530;
    border-radius: 16px;
    background: rgba(255,255,255,0.025);
}}

.footer {{
    text-align: center;
    color: #555560;

    font-size: 12px;
    margin-top: 45px;
}}

@media (max-width: 600px) {{

    .container {{
        padding-top: 25px;
    }}

    .article {{
        padding: 18px;
    }}

    .article-top {{
        flex-direction: column;
        gap: 7px;
    }}

}}

</style>

</head>

<body>

<div class="container">

<header class="header">

    <h1 class="logo">
        STREAMER<span>NEWS</span>
    </h1>

    <div class="subtitle">
        The latest from the streaming world.
    </div>

    <div class="status">
        <span class="status-dot"></span>
        UPDATED AUTOMATICALLY
    </div>

</header>

<div class="section-title">

    <h1>LATEST NEWS</h1>

    <span class="count">
        {len(articles)} articles
    </span>

</div>

{cards}

<footer class="footer">
    Updated automatically every hour.
</footer>

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
