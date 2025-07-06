# YouTube Playlist to CSV Scraper

This script extracts video names from a YouTube playlist and saves them to a CSV file with tracking status.

## Features

- ✅ Extracts all video titles from any public YouTube playlist
- ✅ Creates CSV with `name`, `link`, and `status` columns
- ✅ Sets all entries to "Not Started" status
- ✅ No API key required
- ✅ Handles errors gracefully
- ✅ UTF-8 encoding support for international characters

## Prerequisites

You need Python 3.6+ installed on your system.

## Installation

1. Install the required dependency:

```bash
pip install yt-dlp
```

Or install from requirements file:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage (Default Playlist)

The script has your playlist URL pre-configured:

```bash
python scrap-list-into-csv.py
```

### Custom Playlist URL

```bash
python scrap-list-into-csv.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID"
```

### Custom Output Filename

```bash
python scrap-list-into-csv.py "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID" "my_playlist.csv"
```

## Output

The script creates a CSV file with the following structure:

```csv
name,link,status
"Video Title 1","https://www.youtube.com/watch?v=VIDEO_ID1","Not Started"
"Video Title 2","https://www.youtube.com/watch?v=VIDEO_ID2","Not Started"
"Video Title 3","https://www.youtube.com/watch?v=VIDEO_ID3","Not Started"
...
```

## Example Output

```
Extracting videos from playlist: https://www.youtube.com/watch?v=OQcdKHIpKAk&list=PLtVcREFQDb6ZykTpgFhkQiPjLyrX1Y96D
This may take a moment...
Successfully extracted 25 videos from playlist
Successfully saved 25 videos to playlist_videos.csv

✅ Process completed successfully!
📁 CSV file created: playlist_videos.csv
📊 Total videos: 25

Sample entries:
  1. Introduction to Data Structures
  2. Arrays and Linked Lists
  3. Stacks and Queues
  ... and 22 more
```

## Troubleshooting

### Common Issues

1. **"No module named 'yt_dlp'"**

   - Solution: Install yt-dlp using `pip install yt-dlp`

2. **"Unable to extract playlist"**

   - Check if the playlist URL is correct
   - Ensure the playlist is public (not private)
   - Try again later if YouTube is temporarily blocking requests

3. **"Permission denied" when writing CSV**
   - Make sure you have write permissions in the current directory
   - Try running with different filename or in different directory

### Getting Playlist URL

To get the correct playlist URL:

1. Go to YouTube and open the playlist
2. Copy the URL from the address bar
3. The URL should contain `list=` parameter

## Notes

- The script uses `yt-dlp` which is actively maintained and handles YouTube's changes
- No downloading occurs - only metadata extraction
- The script respects YouTube's terms of service
- Private or restricted playlists cannot be accessed
