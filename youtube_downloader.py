#!/usr/bin/env python

import os
import sys
import re
import pytube
from pytube.cli import on_progress
import getopt
import numpy as np

version = 1.5
name = 'youtube_downloader.py'


def usage():
    sys.stderr.write(f"""
This is {name} version {version}, a tool to download video/audio from youtube of selected quality.\n
Usage: {name} [url] [-v] [-a] [-q quality] [-h]\n
Positional Parameters:
url: The YouTube /watch or /playlist url
-v: Provide the resolution you want to download ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
-a: Provide the quality you want to download ['256kbps', '128kbps', '160kbps', '70kbps', '50kbps']
-h: Display help
    """)


def download_file(required_file, title, av_format, available_quality):
    file_name = title + "_" + available_quality  # +"."+file_extension
    file_size = required_file.filesize
    print("File Size: "+str(round(file_size/1024/1024, 2))+" MB")
    file = required_file.download(
        filename=file_name, output_path="./downloads/")
    file_without_ext, file_ext = os.path.splitext(file)
    os.rename(file.replace("\\", r"\\"), file_without_ext +
              ".mp3" if av_format == 'audio' and file_ext == '.mp4' else file_without_ext+file_ext)


def download_type(video, title, av_format, resolution_to_download):
    download_type = video.streams.filter(
        type=av_format)  # , subtype='mp4'
    list_of_quality = np.unique(
        [i.resolution if av_format == 'video' else i.abr for i in download_type])
    numeric_quality = [int(re.split('p|kbps', i, 0)[0])
                       for i in list_of_quality]
    nearest_quality = (np.abs(np.asarray(numeric_quality) -
                              int(re.split('p|kbps', resolution_to_download, 0)[0]))).argmin()
    available_quality = list_of_quality[nearest_quality]
    print("Available Quality closet to your selection: ", available_quality)
    if av_format == 'video':
        required_file = download_type.filter(res=available_quality).first()
    if av_format == 'audio':
        required_file = download_type.filter(
            abr=available_quality).first()
    download_file(required_file, title, av_format, available_quality)


def single_video(url, av_format, resolution_to_download):
    video = pytube.YouTube(url, on_progress_callback=on_progress)
    title = video.title
    video_id = video.video_id
    watch_url = video.watch_url
    length = video.length
    print("url: ", watch_url)
    print("ID: ", video_id)
    print("Title: ", title)
    print("Length (secs): ", length)
    download_type(video, title, av_format, resolution_to_download)


def plalist_url(url, av_format, resolution_to_download):
    playlist = pytube.Playlist(url)
    for video in playlist.video_urls:
        single_video(video, av_format, resolution_to_download)


def main(url_input, av_format, download_quality):
    if url_input.find('list') > 1:
        plalist_url(url_input, av_format, download_quality)
    else:
        single_video(url_input, av_format, download_quality)


def input():
    download_quality = None
    argv = sys.argv[1:]

    if len(argv) == 0:
        usage()
        sys.exit(2)

    try:
        re.search('youtu\\.be|youtube', argv[0]).start()
        url_input = argv[0]
    except Exception:
        sys.stderr.write("Please provide a valid youtube link")

    if argv[1] == '-v':
        av_format = 'video'
    if argv[1] == '-a':
        av_format = 'audio'

    try:
        opts, args = getopt.getopt(argv[2:], 'q:h:avqh')
    except Exception:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            usage()
            sys.exit(0)
        if opt == '-q':
            download_quality = arg

    main(url_input, av_format, download_quality)


if __name__ == "__main__":
    input()
