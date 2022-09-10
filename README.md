# Send Steam purchase history to Splunk

## Requirements
- A Splunk server with HTTP Event Collector
  - Easily create an ephemeral one in Docker:
    ```shell
    docker run --rm -it -p 8000:8000 -p 8088:8088 -e SPLUNK_START_ARGS=--accept-license -e SPLUNK_PASSWORD=password --name splunk splunk/splunk
    ```
- Python 3 and Poetry
- Python dependencies (`poetry install --no-dev`)

## Download your Steam purchase history
1. Go to https://store.steampowered.com/account/history and log in.
2. Click "Load More Transactions" at the bottom until your full history is shown.
3. Hit Ctrl+S and save the page as an HTML document.
   - You can delete the directory full of CSS, JavaScript, and image files, you'll only need the HTML doc.

## Run the script
```shell
SPLUNK_HEC_TOKEN=<token> poetry run python main.py steam_history.html
```

Where `steam_history.html` is the file you downloaded from Steam.

## CLI options and defaults
```
Usage:
    main.py <html_file> [--hec-url=<url>] [--hec-token=<token>] [--index=<index>]

Options:
    -h --help           Show this help.
    -v --version        Show version.
    --hec-url=<url>     Splunk HTTP Event Collector URL [default: https://localhost:8088/services/collector/event].
    --hec-token=<token> Splunk HEC Token (if blank, pulled from SPLUNK_HEC_TOKEN environment variable).
    --index=<index>     Splunk index to send data to [default: steam].
```

## Example dashboard
See [dashboard.json](dashboard.json) - requires Dashboard Studio.
