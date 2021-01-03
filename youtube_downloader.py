#!/usr/bin/env python

import progressbar
import numpy as np
import urllib
import re
import pytube
import os
import sys
# os.system(f"{sys.executable} -m pip install -U progressbar")
# os.system(f"{sys.executable} -m pip install -U pytube")

version = 1.3
name = 'youtube_downloader.py'

pbar = None


def usage():
    sys.stderr.write(f"""
This is {name} version {version}, a tool to download video/audio from youtube of selected quality.\n\n
Usage: {name} -y url [-v resolution] [-a quality] [-h]\n\n
-h: Display help\n
-v: Provide the resolution you want to download ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']\n
-a: Provide the quality you want to download ['256kbps', '128kbps', '160kbps', '70kbps', '50kbps']\n
    """)


def show_progress(block_num, block_size, total_size):
    # https://stackoverflow.com/a/46825841/5734121
    global pbar
    if pbar is None:
        pbar = progressbar.ProgressBar(maxval=total_size)

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.start()
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None


def download_file(required_file, title, av_format, available_quality):
    file_name = title + "_" + available_quality  # +"."+file_extension
    print("File Size: "+str(round(required_file.filesize/1024/1024, 2))+" MB")
    file = required_file.download(filename=file_name)
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
    if av_format == 'video':
        required_file = download_type.filter(res=available_quality).first()
    if av_format == 'audio':
        required_file = download_type.filter(
            abr=available_quality).first()
    download_file(required_file, title, av_format, available_quality)


def single_video(url, av_format, resolution_to_download):
    video = pytube.YouTube(url)
    # video.register_on_progress_callback(show_progress_bar)
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


def main():
    url_input = input("Please provide the url you want to download: ")
    av_format = input('You want to download a video/audio (v/a)? ')
    av_format = 'video' if av_format.upper().find("V") >= 0 else 'audio'
    quality_dict = {'video': ['2160p', '1440p', '1080p', '720p', '480p', '360p',
                              '240p', '144p'], 'audio': ['256kbps', '128kbps', '160kbps', '70kbps', '50kbps']}
    resolution_to_download = input(
        f"Please enter the quality in which you want file to be downloaded, from the following: {quality_dict['video'] if av_format == 'video' else quality_dict['audio'] } ")

    if url_input.find('list') > 1:
        plalist_url(url_input, av_format, resolution_to_download)
    else:
        single_video(url_input, av_format, resolution_to_download)


if __name__ == "__main__":
    main()
