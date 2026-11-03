# Paradox-News-news-aggregator-app.
Paradox News: Sleek, Serverless-Style RSS Aggregator
Paradox News is a minimalist, mobile-optimized news aggregator built as a single-file Python application using NanoDjango. Designed with a dark-mode-first aesthetic and a native app feel, it automatically syncs, categorizes, and serves live feeds from multiple sources into a lightning-fast, searchable interface.
Key Features:
Single-File Architecture: The entire app logic, models, admin registration, YAML configuration, views, and frontend template are packaged into one clean, portable file.
YAML-Driven Feed Configuration: Easily add, remove, or modify RSS sources (such as BBC World, Sports, Technology, and Business) cleanly via an integrated YAML config block.
Smart Content Syncing: Uses feedparser to parse incoming RSS entries and update_or_create database logic to seamlessly pull new items without duplicates.
Mobile-First UI/UX: Styled with custom CSS variables, sticky navigation, horizontal scrolling category tabs, and an intuitive bottom app bar optimized for mobile viewports.
Integrated Admin Panel: Out-of-the-box Django admin integration allowing you to manage news items, search titles, and filter by categories effortlessly.
