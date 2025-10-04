import random
import re
from time import sleep
import yt_dlp
import requests
import webvtt
import io
from os import path, listdir

class Subtitles():
    def __init__(self, url):
        self.url = url
        self._en_subs = []
        self._en_auto = []
        self.subtitle_exts = []
        self.automatic_captions_exts = []
        
        ydl_opts = {
            'skip_download': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            subtitles = info_dict.get('subtitles', {})
            automatic_captions = info_dict.get('automatic_captions', {})

            self._en_subs = subtitles.get('en', [])
            self._en_auto = automatic_captions.get('en', [])
            self.subtitle_exts = [sub['ext'] for sub in self._en_subs]
            self.automatic_captions_exts = [sub['ext'] for sub in self._en_auto]

    def get_subtitles(self):
        if self._en_subs:
            return self._en_subs
        elif self._en_auto:
            return self._en_auto
        else:
            return None

    def download_subtitles(self, url=None, format_preference="vtt"):
        """Download and return subtitle text (manual preferred, else auto)."""
        subs = None

        if url is None:
            url = self.url
            subs = self.get_subtitles()
        if not subs:
            return None

        # Pick the first available format if preferred is not found
        for sub in subs:
            if sub['ext'] == format_preference:
                sub_url = sub['url']
                break
        if not sub_url:
            sub_url = subs[0]['url']  # fallback to whatever is available

        # Download the file
        for i in range(5):  # Retry up to 5 times
            try:
                resp = requests.get(sub_url)
                resp.raise_for_status()
                return resp.text
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 429:
                    print(f"429 error, retrying in 1-2 seconds...")
                    sleep(random.uniform(1, 2))
                else:
                    raise e
            except requests.HTTPError as e:
                print(f"Failed to download subtitles: {e}")
                return None
    
    def download_vtt_text(self):
        """Return subtitles as plain text only (no timestamps)."""
        raw = self.download_subtitles(format_preference="vtt")
        if not raw:
            return None

        # Parse VTT content
        vtt = webvtt.read_buffer(io.StringIO(raw))
        
        transcript = ""
        lines = []
        for line in vtt:
            # Strip the newlines from the end of the text.
            # Split the string if it has a newline in the middle
            # Add the lines to an array
            lines.extend(line.text.strip().splitlines())

        # Remove repeated lines
        previous = None
        for line in lines:
            if line == previous:
                continue
            transcript += " " + line
            previous = line

        return transcript

def get_all_videos(channel_url):
    ydl_opts = {
        'extract_flat': True,  # Don't download videos, just get metadata
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        "external_downloader_args": ['-loglevel', 'panic'],
        'ratelimit': 1_000_000,       # limit download speed (bytes/sec)
        'sleep_interval_requests': 1, # sleep 1 second between requests
        'max_sleep_interval': 5,      # max random sleep interval
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        # info['entries'] is a generator of videos
        videos = [{ "url": f"https://www.youtube.com/watch?v={entry['id']}", "title": entry.get("title", "") } for entry in info['entries']]
        
        return videos

print("Fetching video list...")
videos = get_all_videos("https://www.youtube.com/@TheYardPodcast/videos")

# Skip first n videos (we already have these in the subtitles folder)
n = len(listdir("subtitles"))

videos = videos[n + 1:]

print(f"Found {len(videos)} videos")
if n > 0:
    print(f"Skipping {n} (already downloaded)...")

total_videos = len(videos) - n

def safe_filename(s):
    return re.sub(r'[\\/*?:"<>|]', "_", s)

if __name__ == "__main__":
    # stores plain text of all subtitles
    i = 1
    for video in videos:
        print(f"\nProcessing title #{i}: {video['title']}")
        sleep(random.uniform(1, 3))
        subs = Subtitles(video['url']).download_vtt_text()

        if subs:
            p = path.join("subtitles", safe_filename(video['title']) + ".txt")
            print(p)
            with open(p, "w", encoding="utf-8") as f:
                f.write(subs)
                f.close()

            print(f"Saved subtitles for {video['title']}")
            i += 1
        else:
            print(f"No subtitles found for {video['title']}")

    print(f"\nDone! successfully processed {i - 1} videos.")