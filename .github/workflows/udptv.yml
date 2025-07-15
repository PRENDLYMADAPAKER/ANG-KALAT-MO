name: 🔄 Update UDPTV Playlist

on:
  schedule:
    - cron: '*/5 * * * *'  # ⏱ Auto update every 5 minutes
  workflow_dispatch:        # ✅ Manual trigger stays

permissions:
  contents: write           # ✅ Required to push changes from Actions

jobs:
  update-playlist:
    runs-on: ubuntu-latest

    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v3
        with:
          ref: main

      - name: 🐍 Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: 📦 Install dependencies
        run: pip install requests

      - name: 🔄 Run UDPTV playlist update script
        run: python udptv.py

      - name: 🕒 Force-inject timestamp (ensures commit even if only URL changes)
        run: |
          echo "# Updated at $(date -u '+%Y-%m-%dT%H:%M:%SZ')" >> UDPTV.m3u

      - name: 💾 Commit and push updated playlist
        run: |
          git config user.name "github-actions"
          git config user.email "github-actions@users.noreply.github.com"
          git add UDPTV.m3u
          git commit -m "Force update UDPTV.m3u with timestamp" || echo "No changes to commit"
          git push origin main
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
