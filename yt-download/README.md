# yt-download

## How to build

- `./build.sh`
- `docker exec -it -u ubuntu yt-download /bin/bash`
- Run `yt-dlp` to download the videos.

## Examples

- Download a single file with custom output filename: `yt-dlp --merge-output-format mp4 -o "output-file-name-%(playlist_index)d.%(ext)s" "<URL>"`
- Download a whole play list with custom output filenames: `yt-dlp --merge-output-format mp4 -o "output-file-name-%(playlist_index)d.%(ext)s" "<URL>"`
