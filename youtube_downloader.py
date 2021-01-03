import progressbar
import numpy as np
import urllib
import re
import pytube
import os
import sys
os.system(f"{sys.executable} -m pip install -U progressbar")
os.system(f"{sys.executable} -m pip install -U pytube")

version = 1.0
name = 'youtube_downloader.py'


def show_progress(block_num, block_size, total_size):
    # https://stackoverflow.com/a/46825841/5734121
    pbar = None
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
    url = required_file.url
    file_extension = 'mp3' if av_format == 'audio' else required_file.mime_type.split("/")[1]
    file_name = title.replace(" ", "_")+"_" + available_quality+"."+file_extension
    final_file_name = re.sub('[^A-Za-z0-9 _\-.]+', '', file_name)
    print(final_file_name)
    print("File Size: "+str(round(required_file.filesize/1024/1024, 2))+" MB")
    urllib.request.urlretrieve(url, final_file_name, show_progress)


def download_type(video, title, av_format, resolution_to_download):
    download_type = video.streams.filter(type=av_format, subtype='mp4')
    list_of_quality = np.unique(
        [i.resolution if av_format == 'video' else i.abr for i in download_type])
    numeric_quality = [int(re.split('p|kbps', i, 0)[0])
                       for i in list_of_quality]
    nearest_quality = (np.abs(np.asarray(numeric_quality) -
                              int(re.split('p|kbps', resolution_to_download, 0)[0]))).argmin()
    available_quality = list_of_quality[nearest_quality]
    if av_format == 'video':
        required_file = download_type.filter(
            res=available_quality).first()
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
