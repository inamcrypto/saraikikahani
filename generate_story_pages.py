import json
import html
import re
from pathlib import Path

root = Path(__file__).resolve().parent
SITE_URL = "https://www.saraikikids.pk"
index_html = (root / "index.html").read_text(encoding="utf-8-sig")
stories_match = re.search(
    r'<script id="storiesData" type="application/json">\s*(\{.*?\})\s*</script>',
    index_html,
    re.DOTALL,
)
if not stories_match:
    raise RuntimeError("Could not find inline storiesData in index.html")

stories = json.loads(stories_match.group(1))["stories"]

category_labels = {
    "animal": "\u062c\u0627\u0646\u0648\u0631",
    "moral": "\u0627\u062e\u0644\u0627\u0642",
    "folk": "\u0644\u0648\u06a9 \u06a9\u06c1\u0627\u0646\u06cc",
}

labels = {
    "site_name": "\u06a9\u06c1\u0627\u0768\u06cc \u0622\u0646\u06af\u0768",
    "home": "\u067e\u06c1\u0644\u0627 \u0635\u0641\u062d\u06c1",
    "more_stories": "\u06c1\u0648\u0631 \u06a9\u06c1\u0627\u0646\u06cc\u0627\u06ba",
    "story_read": "\u06a9\u06c1\u0627\u0646\u06cc \u067e\u0691\u06be\u0648",
    "page": "\u0635\u0641\u062d\u06c1",
    "about_story": "\u0627\u06cc\u06c1\u06c1 \u06a9\u06c1\u0627\u0646\u06cc \u0628\u0627\u0631\u06d2",
    "read_more": "\u06c1\u0648\u0631 \u067e\u0691\u06be\u0648",
    "all_stories": "\u0633\u0628 \u06a9\u06c1\u0627\u0646\u06cc\u0627\u06ba \u0648\u06cc\u06a9\u06be\u0648",
    "for_families": "\u0628\u0686\u06cc\u06ba \u062a\u06d2 \u0648\u0627\u0644\u062f\u06cc\u0646 \u0644\u0626\u06cc",
    "pages_suffix": "\u0635\u0641\u062d\u06d2",
    "story_library": "\u06a9\u06c1\u0627\u0646\u06cc \u0644\u0627\u0626\u0628\u0631\u06cc\u0631\u06cc",
    "library_title": "\u0633\u0627\u0631\u06cc\u0627\u06ba \u06a9\u06c1\u0627\u0646\u06cc\u0627\u06ba",
    "library_desc": "\u0627\u06cc\u06c1\u062a\u06be\u0648\u06ba \u06c1\u0631 \u0633\u0631\u0627\u0626\u06cc\u06a9\u06cc \u06a9\u06c1\u0627\u0646\u06cc \u0627\u067e\u0646\u06d2 \u0627\u0644\u06af \u0635\u0641\u062d\u06d2 \u0646\u0627\u0644 \u06a9\u06be\u0644\u062f\u06cc \u0627\u06d2 \u062a\u0627\u06a9\u06c1 \u067e\u0691\u06be\u0646\u0627 \u062a\u06d2 \u0633\u0631\u0686 \u0648\u0686 \u0644\u0628\u06be\u0646\u0627 \u062f\u0648\u0627\u06ba \u0622\u0633\u0627\u0646 \u06c1\u0648\u0633\u0646\u06d4",
    "library_pages": "\u06a9\u06c1\u0627\u0646\u06cc \u062f\u06d2 \u0635\u0641\u062d\u06d2",
    "seo_benefit": "SEO \u0641\u0627\u0626\u062f\u06c1",
    "seo_desc": "\u06c1\u0631 \u06a9\u06c1\u0627\u0646\u06cc \u06c1\u0646 \u0627\u067e\u0646\u06d2 \u06cc\u0648 \u0622\u0631 \u0627\u06cc\u0644\u060c \u0639\u0646\u0648\u0627\u0646\u060c \u0645\u06cc\u0679\u0627 \u0688\u0633\u06a9\u0631\u067e\u0634\u0646 \u062a\u06d2 \u0627\u0646\u062f\u0631\u0648\u0646\u06cc \u0644\u0646\u06a9\u0633 \u0646\u0627\u0644 \u0645\u0648\u062c\u0648\u062f \u0627\u06d2\u06d4",
    "back_home": "\u06c1\u0648\u0645 \u062a\u06d2 \u0648\u0627\u067e\u0633",
    "copyright": "\u00a9 2026 \u06a9\u06c1\u0627\u0768\u06cc \u0622\u0646\u06af\u0768",
}

ICON_BOOK = "&#128218;"
ARROW_LEFT = "&larr;"
ARROW_RIGHT = "&rarr;"


def format_story_text(text: str) -> str:
    encoded = html.escape(text)
    encoded = encoded.replace("**", "\u0000")
    parts = encoded.split("\u0000")
    for i in range(1, len(parts), 2):
        parts[i] = f"<strong>{parts[i]}</strong>"
    return "".join(parts).replace("\n", "<br>")


for idx, story in enumerate(stories):
    story_dir = root / "stories" / story["slug"]
    story_dir.mkdir(parents=True, exist_ok=True)
    related = sorted(
        [s for s in stories if s["id"] != story["id"]],
        key=lambda s: (s["category"] != story["category"], s["title"]),
    )[:3]

    blocks = []
    for i, paragraph in enumerate(story["content"]):
        image_markup = ""
        page_images = story.get("pageImages") or []
        if i < len(page_images):
            image = page_images[i]
            src = "../../" + image["src"].replace(" ", "%20")
            alt = html.escape(image["alt"])
            image_markup = (
                f'\n    <figure>\n        <img src="{src}" alt="{alt}" loading="lazy">\n    </figure>'
            )
        body = format_story_text(paragraph)
        blocks.append(
            f"""<section class="story-block">
    <h3>{labels["page"]} {i + 1}</h3>{image_markup}
    <p>{body}</p>
</section>"""
        )

    story_url = f"{SITE_URL}/stories/{story['slug']}/"

    related_markup = "\n".join(
        f"""<li>
    <a href="../{item["slug"]}/index.html">
        <strong>{html.escape(item["title"])}</strong>
        <span>{html.escape(item["description"])}</span>
    </a>
</li>"""
        for item in related
    )

    prev_markup = (
        f'<a href="../{stories[idx - 1]["slug"]}/index.html">{ARROW_LEFT} {html.escape(stories[idx - 1]["title"])}</a>'
        if idx > 0
        else f'<a href="../../index.html">{ARROW_LEFT} {labels["home"]}</a>'
    )
    next_markup = (
        f'<a href="../{stories[idx + 1]["slug"]}/index.html">{html.escape(stories[idx + 1]["title"])} {ARROW_RIGHT}</a>'
        if idx < len(stories) - 1
        else f'<a href="../../index.html">{labels["home"]} {ARROW_RIGHT}</a>'
    )

    title = html.escape(story["title"])
    description = html.escape(story["description"])
    category = category_labels[story["category"]]
    meta_description = html.escape(
        f'Read {story["title"]}, a Saraiki kids story from Kahani Angan. {story["description"]}'
    )
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "CreativeWork",
            "name": story["title"],
            "description": story["description"],
            "inLanguage": "skr",
            "genre": category,
            "isPartOf": {
                "@type": "CollectionPage",
                "name": "Saraiki Kids Stories | Kahani Angan",
            },
        },
        ensure_ascii=False,
        indent=4,
    )

    page = f"""<!DOCTYPE html>
<html lang="skr" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Saraiki Kids Story | Kahani Angan</title>
    <meta name="description" content="{meta_description}">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title} | Kahani Angan">
    <meta property="og:description" content="{description}">
    <meta property="og:site_name" content="Kahani Angan">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title} | Kahani Angan">
    <meta name="twitter:description" content="{description}">
    <link rel="canonical" href="{story_url}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../../story-page.css">
    <script type="application/ld+json">
{json_ld}
    </script>
</head>
<body style="--story-color: {story["color"]};">
    <nav class="navbar">
        <div class="nav-container">
            <a href="../../index.html" class="logo">
                <span class="logo-icon">{ICON_BOOK}</span>
                <span class="logo-text">{labels["site_name"]}</span>
            </a>
            <ul class="nav-links">
                <li><a href="../../index.html">{labels["home"]}</a></li>
                <li><a href="../../index.html#stories" class="active">{labels["more_stories"]}</a></li>
            </ul>
        </div>
    </nav>

    <main>
        <section class="story-hero">
            <div class="container">
                <div class="story-hero-card">
                    <div>
                        <p class="story-badge">Saraiki kids story</p>
                        <h1 class="story-title">{title}</h1>
                        <p class="story-description">{description}</p>
                        <div class="story-meta">
                            <span class="story-chip">{category}</span>
                            <span class="story-chip">{len(story["content"])} {labels["pages_suffix"]}</span>
                            <span class="story-chip">{labels["for_families"]}</span>
                        </div>
                    </div>
                    <div class="story-cover-panel" aria-hidden="true">
                        <div class="story-cover-emoji">{story["emoji"]}</div>
                    </div>
                </div>
            </div>
        </section>

        <section class="story-layout">
            <div class="container">
                <article class="story-article">
                    <h2>{labels["story_read"]}</h2>
                    {"\n".join(blocks)}
                    <nav class="story-nav" aria-label="Story navigation">
                        {prev_markup}
                        {next_markup}
                    </nav>
                </article>

                <aside class="story-sidebar">
                    <div class="sidebar-card">
                        <h2>{labels["about_story"]}</h2>
                        <p>{description}</p>
                    </div>
                    <div class="sidebar-card">
                        <h3>{labels["read_more"]}</h3>
                        <ul class="story-list">
                            {related_markup}
                        </ul>
                    </div>
                    <div class="sidebar-card">
                        <a class="home-link" href="../../index.html#stories">{ARROW_LEFT} {labels["all_stories"]}</a>
                    </div>
                </aside>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <div class="footer-logo">
                <span class="logo-icon">{ICON_BOOK}</span>
                <span>{labels["site_name"]}</span>
            </div>
            <p>Saraiki kids stories, bedtime stories, and moral stories for children.</p>
            <p>{labels["copyright"]}</p>
        </div>
    </footer>
</body>
</html>
"""
    (story_dir / "index.html").write_text(page, encoding="utf-8")

items = "\n".join(
    f"""<li>
    <a href="{story["slug"]}/index.html">
        <strong>{html.escape(story["title"])}</strong>
        <span>{html.escape(story["description"])}</span>
        <em>{category_labels[story["category"]]}</em>
    </a>
</li>"""
    for story in stories
)

library_page = f"""<!DOCTYPE html>
<html lang="skr" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saraiki Story Library | Kahani Angan</title>
    <meta name="description" content="Browse all Saraiki kids story pages on Kahani Angan, including bedtime, moral, and folk stories for children.">
    <meta name="robots" content="index, follow, max-image-preview:large">
    <link rel="canonical" href="{SITE_URL}/stories/">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;700&family=Noto+Sans+Arabic:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../story-page.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <a href="../index.html" class="logo">
                <span class="logo-icon">{ICON_BOOK}</span>
                <span class="logo-text">{labels["site_name"]}</span>
            </a>
            <ul class="nav-links">
                <li><a href="../index.html">{labels["home"]}</a></li>
                <li><a href="./index.html" class="active">{labels["story_library"]}</a></li>
            </ul>
        </div>
    </nav>

    <main>
        <section class="story-hero">
            <div class="container">
                <div class="story-hero-card">
                    <div>
                        <p class="story-badge">Story library</p>
                        <h1 class="story-title">{labels["library_title"]}</h1>
                        <p class="story-description">{labels["library_desc"]}</p>
                    </div>
                    <div class="story-cover-panel" aria-hidden="true">
                        <div class="story-cover-emoji">{ICON_BOOK}</div>
                    </div>
                </div>
            </div>
        </section>

        <section class="story-layout">
            <div class="container">
                <article class="story-article">
                    <h2>{labels["library_pages"]}</h2>
                    <ul class="story-list">
                        {items}
                    </ul>
                </article>

                <aside class="story-sidebar">
                    <div class="sidebar-card">
                        <h2>{labels["seo_benefit"]}</h2>
                        <p>{labels["seo_desc"]}</p>
                    </div>
                    <div class="sidebar-card">
                        <a class="home-link" href="../index.html#stories">{ARROW_LEFT} {labels["back_home"]}</a>
                    </div>
                </aside>
            </div>
        </section>
    </main>

    <footer class="footer">
        <div class="footer-content">
            <div class="footer-logo">
                <span class="logo-icon">{ICON_BOOK}</span>
                <span>{labels["site_name"]}</span>
            </div>
            <p>Saraiki kids stories, bedtime stories, and moral stories for children.</p>
        </div>
    </footer>
</body>
</html>
"""
(root / "stories" / "index.html").write_text(library_page, encoding="utf-8")
