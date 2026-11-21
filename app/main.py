name: Build
on:
  push:
    branches: [main]
    tags: ["v*"]
  pull_request:
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Syntax check
        run: python -m compileall app launcher.py
      - name: Read version
        id: v
        run: echo "version=$(cat VERSION)" >> $GITHUB_OUTPUT
      - name: Build Docker image
        run: docker build -t dark-audio-changer:${{ steps.v.outputs.version }} .
      - name: Package app
        run: |
          mkdir -p dist/DarkAudioChanger
          rsync -a --exclude='.git' --exclude='.github' --exclude='dist' --exclude='data/*' ./ dist/DarkAudioChanger/
          mkdir -p dist/DarkAudioChanger/data && touch dist/DarkAudioChanger/data/.gitkeep
          cd dist && zip -r DarkAudioChanger-v${{ steps.v.outputs.version }}.zip DarkAudioChanger
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: DarkAudioChanger-v${{ steps.v.outputs.version }}
          path: dist/DarkAudioChanger-v${{ steps.v.outputs.version }}.zip
      - name: Release (tag push)
        if: startsWith(github.ref, 'refs/tags/v')
        uses: softprops/action-gh-release@v2
        with:
          files: dist/DarkAudioChanger-v${{ steps.v.outputs.version }}.zip
