import yaml
import feedparser
from django.contrib import admin
from django.db import models
from django.shortcuts import render, redirect
from nanodjango import Django

app = Django()

# --- MODELS ---
class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField(unique=True)
    summary = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default="Trending")
    published = models.DateTimeField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

@app.admin(NewsItem, list_display=("title", "category", "published"))
class NewsItemAdmin(admin.ModelAdmin):
    search_fields = ["title", "summary"]
    list_filter = ["category"]


# --- CONFIG (YAML) ---
RSS_CONFIG_YAML = """
sources:
  - name: "BBC Trending / World"
    url: "https://feeds.bbci.co.uk/news/world/rss.xml"
    category: "Trending"
  - name: "BBC Sports"
    url: "https://feeds.bbci.co.uk/sport/rss.xml"
    category: "Sports"
  - name: "BBC Politics"
    url: "https://feeds.bbci.co.uk/news/politics/rss.xml"
    category: "Politics"
  - name: "BBC Technology"
    url: "https://feeds.bbci.co.uk/news/technology/rss.xml"
    category: "Technology"
  - name: "BBC Business"
    url: "https://feeds.bbci.co.uk/news/business/rss.xml"
    category: "Business"
"""

@app.route("/refresh/")
def refresh_feeds(request):
    """Fetches items from YAML-defined BBC RSS feeds and saves them to the DB."""
    config = yaml.safe_load(RSS_CONFIG_YAML)
    
    for source in config.get("sources", []):
        feed_url = source["url"]
        category = source["category"]
        parsed_feed = feedparser.parse(feed_url)
        
        for entry in parsed_feed.entries:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", "")
            
            image_url = None
            if hasattr(entry, "enclosures") and entry.enclosures:
                image_url = entry.enclosures[0].get("href")
            
            if link:
                NewsItem.objects.update_or_create(
                    link=link,
                    defaults={
                        "title": title,
                        "summary": summary,
                        "category": category,
                        "image_url": image_url,
                    }
                )
    return redirect("/")


# --- VIEWS ---
@app.route("/")
def index(request):
    selected_category = request.GET.get("category", "Trending")
    search_query = request.GET.get("q", "")
    
    items = NewsItem.objects.all().order_by("-id")
    
    if selected_category and selected_category != "All":
        items = items.filter(category__iexact=selected_category)
        
    if search_query:
        items = items.filter(title__icontains=search_query)
        
    categories = ["Trending", "Sports", "Politics", "Technology", "Business"]
    
    return render(request, "index.html", {
        "items": items,
        "categories": categories,
        "selected_category": selected_category,
        "search_query": search_query
    })


# --- TEMPLATE ---
app.templates["index.html"] = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Paradox News Aggregator</title>
    <style>
        :root {
            --bg-main: #09090b;
            --bg-card: #18181b;
            --border-color: #27272a;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --accent: #f97316;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--bg-main);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        header {
            padding: 1rem;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            background-color: rgba(9, 9, 11, 0.85);
            backdrop-filter: blur(8px);
            z-index: 50;
        }

        .header-content, main, .bottom-nav {
            max-width: 480px;
            margin: 0 auto;
            width: 100%;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        h1 {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: 0.025em;
        }

        .btn-sync {
            background-color: var(--accent);
            color: white;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 500;
            text-decoration: none;
            transition: opacity 0.2s;
        }

        .btn-sync:hover {
            opacity: 0.9;
        }

        .admin-link {
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.875rem;
        }
        .admin-link:hover {
            color: var(--text-main);
        }

        main {
            padding: 1rem;
            flex-grow: 1;
            margin-bottom: 4rem;
        }

        /* Search Form */
        .search-form {
            position: relative;
            margin-bottom: 1.25rem;
        }

        .search-input {
            width: 100%;
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 9999px;
            padding: 0.75rem 3rem 0.75rem 1.25rem;
            font-size: 0.875rem;
            color: var(--text-main);
            outline: none;
            transition: border-color 0.2s;
        }

        .search-input:focus {
            border-color: var(--accent);
        }

        .search-btn {
            position: absolute;
            right: 1rem;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
        }

        /* Categories Scrollbar */
        .categories-nav {
            display: flex;
            gap: 1rem;
            overflow-x: auto;
            padding-bottom: 0.75rem;
            margin-bottom: 1rem;
            white-space: nowrap;
            scrollbar-width: none;
        }
        .categories-nav::-webkit-scrollbar {
            display: none;
        }

        .category-tab {
            font-size: 0.875rem;
            font-weight: 500;
            text-decoration: none;
            color: var(--text-muted);
            transition: color 0.2s;
            padding-bottom: 2px;
        }

        .category-tab:hover {
            color: var(--text-main);
        }

        .category-tab.active {
            color: var(--accent);
            border-bottom: 2px solid var(--accent);
        }

        /* Feed List */
        .feed-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .news-card {
            background-color: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 1rem;
            padding: 1rem;
            display: flex;
            gap: 1rem;
            align-items: center;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: border-color 0.2s;
        }

        .news-card:hover {
            border-color: #3f3f46;
        }

        .news-content {
            flex: 1;
        }

        .news-category-label {
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #fb923c;
            font-weight: 600;
            margin-bottom: 0.25rem;
            display: block;
        }

        .news-title {
            font-size: 0.875rem;
            font-weight: 500;
            line-height: 1.4;
            color: var(--text-main);
            text-decoration: none;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .news-title:hover {
            text-decoration: underline;
        }

        .news-thumb {
            width: 6rem;
            height: 5rem;
            object-fit: cover;
            border-radius: 0.75rem;
            background-color: var(--border-color);
            flex-shrink: 0;
        }

        .news-thumb-placeholder {
            width: 6rem;
            height: 5rem;
            background-color: var(--border-color);
            border-radius: 0.75rem;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #52525b;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .empty-state {
            text-align: center;
            padding: 3rem 0;
            color: var(--text-muted);
        }

        .empty-state a {
            color: var(--accent);
            text-decoration: underline;
        }

        /* Bottom Navbar */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color: var(--bg-card);
            border-top: 1px solid var(--border-color);
            padding: 0.75rem 1.5rem;
            z-index: 50;
        }

        .bottom-nav-content {
            max-width: 480px;
            margin: 0 auto;
            display: flex;
            justify-content: space-around;
            font-size: 0.75rem;
        }

        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            color: var(--text-muted);
            text-decoration: none;
            gap: 2px;
        }

        .nav-item.active {
            color: var(--accent);
        }

        .nav-item span:first-child {
            font-size: 1.1rem;
        }
    </style>
</head>
<body>

    <!-- Header -->
    <header>
        <div class="header-content">
            <h1>Paradox News</h1>
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <a href="/refresh/" class="btn-sync">Sync RSS</a>
                <a href="/admin/" class="admin-link">Admin</a>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main>
        <!-- Search bar -->
        <form method="GET" action="/" class="search-form">
            <input type="text" name="q" value="{{ search_query }}" placeholder="enter text..." class="search-input">
            <button type="submit" class="search-btn">🔍</button>
        </form>

        <!-- Categories -->
        <nav class="categories-nav">
            {% for cat in categories %}
                <a href="/?category={{ cat }}" class="category-tab {% if selected_category == cat %}active{% endif %}">
                    {{ cat }}
                </a>
            {% endfor %}
        </nav>

        <!-- Feed List -->
        <div class="feed-list">
            {% if items %}
                {% for item in items %}
                <article class="news-card">
                    <div class="news-content">
                        <span class="news-category-label">{{ item.category }}</span>
                        <a href="{{ item.link }}" target="_blank" class="news-title">
                            {{ item.title }}
                        </a>
                    </div>
                    {% if item.image_url %}
                        <img src="{{ item.image_url }}" alt="Thumbnail" class="news-thumb">
                    {% else %}
                        <div class="news-thumb-placeholder">BBC</div>
                    {% endif %}
                </article>
                {% endfor %}
            {% else %}
                <div class="empty-state">
                    <p style="margin-bottom: 0.5rem;">No news items found.</p>
                    <a href="/refresh/">Click here to sync feeds</a>
                </div>
            {% endif %}
        </div>
    </main>

    <!-- Bottom Navigation -->
    <nav class="bottom-nav">
        <div class="bottom-nav-content">
            <a href="/" class="nav-item active">
                <span>🏠</span>
                <span>Home</span>
            </a>
            <a href="/refresh/" class="nav-item">
                <span>⚡</span>
                <span>Sync</span>
            </a>
            <a href="/admin/" class="nav-item">
                <span>⚙️</span>
                <span>Admin</span>
            </a>
        </div>
    </nav>

</body>
</html>
"""

if __name__ == "__main__":
    app.run()
              
