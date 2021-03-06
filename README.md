## dl - A Simple Downloader for Your Raspberry Pi

A simple downloader which takes request in file and spawns processes 
dependending upon the type of the request. It has plugin-ish way of
doing actual downloading. So e.g. normal web files are downloaded through wget 
plugin which as names suggest downloaded by `wget` <sup>[1](#1)</sup>, or youtube videos
are downloaded through youtube plugin which internally uses `youtube-dl` <sup>[2](#2)</sup>.

### Dependencies
1. simplejson <sup>[3](#3)</sup>
2. requests <sup>[4](#4)</sup>
3. wget plugin - wget 
4. youtube plugin - youtube-dl

### Configuration

To configure, you need to create following directory structure to submit 
appropriate requests to appropriate plugin and configure the parent directory 
in dlconfig file. You also need to create downloads directory where you want 
to keep downloaded file and configure it as well in the dlconfig file.

```
</home/joe/dl/requests>
    |
    +-- wget/ <-- This is where you will keep requests to download normal web files
    +-- youtube/ <-- This is where you will keep requests to download youtube videos


</home/joe/dl/downloads>
    |
    +-- wget/ <-- This is where normal web files will be downloaded
    +-- youtube/ <-- This is where youtube videos will be downloaded

In dlconfig file:
{
    "pidfile" : "/home/joe/dl/pidfile",
    "paths" : {
        "requests" : "/home/joe/dl/requests",
        "downloads" : "/home/joe/dl/downloads"
    },
    "downloaders" : {
        "wget" : "wget_wrapper",
        "youtube" : "youtube_dl_wrapper",
    }
}

```

### Usage
To run process do following. This will start downloader in background.

```
> dl.sh <dlconfig-path>
```

Once the request file is read, it is renamed to `<original-name>.done` file, so 
that it wont be picked up during the rerun. Note that, just after reading the 
file, it is renamed and not after actual content is downloaded. So it might happen 
that file is renamed but the content is partially downloaded. If such thing happens
just rename it backup to original name and it will be downloaded during next run.
Plugins like wget and youtube support resuming the download where it was previously left behind. 

You can also configure this utility in the crontab. So that it will be run
periodically. Sample crontab rule is as follows:

```
# m h  dom mon dow   command
# Run the downloader at the 3 AM in the morning everyday
0 3 * * * /home/joe/dl/dl.sh /home/joe/dl/.dlconfig
```

### License
Apache License

---
<sup><a href="1">1</a></sup>  `https://www.gnu.org/software/wget/`

<sup><a href="2">2</a></sup>  `http://rg3.github.io/youtube-dl/`

<sup><a href="3">3</a></sup>  `https://pypi.python.org/pypi/simplejson/`

<sup><a href="4">4</a></sup>  `https://pypi.python.org/pypi/requests/`

