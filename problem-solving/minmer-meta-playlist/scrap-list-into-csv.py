#!/usr/bin/env python3
"""
YouTube Playlist Video Scraper
Extracts video names from a YouTube playlist and saves them to CSV format
Uses yt-dlp library to avoid API requirements
"""

import csv
import sys
from typing import List, Dict
import yt_dlp


def extract_playlist_videos(playlist_url: str) -> List[Dict[str, str]]:
    """
    Extract video information from YouTube playlist using yt-dlp
    
    Args:
        playlist_url: YouTube playlist URL
        
    Returns:
        List of dictionaries containing video information
    """
    
    # Extract just the playlist ID
    playlist_id = None
    if 'list=' in playlist_url:
        playlist_id = playlist_url.split('list=')[1].split('&')[0]
    
    # Try multiple URL formats
    urls_to_try = [
        f"https://www.youtube.com/playlist?list={playlist_id}" if playlist_id else playlist_url,
        playlist_url
    ]
    
    # Configure yt-dlp options
    ydl_opts = {
        'quiet': True,  # Suppress output
        'no_warnings': True,  # Suppress warnings
        'extract_flat': True,  # Only extract video metadata, don't download
        'ignoreerrors': True,  # Continue on download errors
    }
    
    videos = []
    
    for url in urls_to_try:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract playlist information
                playlist_info = ydl.extract_info(url, download=False)
                
                if playlist_info and 'entries' in playlist_info:
                    for entry in playlist_info['entries']:
                        if entry is not None and 'title' in entry:
                            # Generate YouTube URL from video ID
                            video_url = f"https://www.youtube.com/watch?v={entry['id']}" if 'id' in entry else entry.get('url', 'N/A')
                            videos.append({
                                'name': entry['title'],
                                'link': video_url,
                                'status': 'Not Started'
                            })
                    break  # Success, exit the loop
                        
        except Exception as e:
            print(f"Error with URL {url}: {str(e)}")
            continue
    
    print(f"Successfully extracted {len(videos)} videos from playlist")
    return videos


def save_to_csv(videos: List[Dict[str, str]], filename: str = "playlist_videos.csv") -> bool:
    """
    Save video list to CSV file
    
    Args:
        videos: List of video dictionaries
        filename: Output CSV filename
        
    Returns:
        True if successful, False otherwise
    """
    
    if not videos:
        print("No videos to save!")
        return False
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['name', 'link', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write video data
            for video in videos:
                writer.writerow(video)
                
        print(f"Successfully saved {len(videos)} videos to {filename}")
        return True
        
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")
        return False


def main():
    """Main function to run the playlist scraper"""
    
    # Default playlist URL (can be changed)
    playlist_url = "https://www.youtube.com/watch?v=OQcdKHIpKAk&list=PLtVcREFQDb6ZykTpgFhkQiPjLyrX1Y96D"
    
    # Allow custom URL via command line argument
    if len(sys.argv) > 1:
        playlist_url = sys.argv[1]
    
    print(f"Extracting videos from playlist: {playlist_url}")
    print("This may take a moment...")
    
    # Extract videos from playlist
    videos = extract_playlist_videos(playlist_url)
    
    if videos:
        # Save to CSV
        csv_filename = "playlist_videos.csv"
        if len(sys.argv) > 2:
            csv_filename = sys.argv[2]
            
        success = save_to_csv(videos, csv_filename)
        
        if success:
            print(f"\n✅ Process completed successfully!")
            print(f"📁 CSV file created: {csv_filename}")
            print(f"📊 Total videos: {len(videos)}")
            print(f"\nSample entries:")
            for i, video in enumerate(videos[:3]):  # Show first 3 entries
                print(f"  {i+1}. {video['name']}")
            if len(videos) > 3:
                print(f"  ... and {len(videos) - 3} more")
        else:
            print("❌ Failed to save CSV file")
            sys.exit(1)
    else:
        print("❌ Failed to extract videos from playlist")
        sys.exit(1)


if __name__ == "__main__":
    main()
