# EHDownloader

You can download images in [e-hentai.org](http://e-hentai.org/) with this script.



## Environment
* Windows
* Mac
* Linux

In Windows, EXE file is available without Python.
In Linux or Mac, This script run in Python(2 or 3) environment.



## Python Version
* 2.7
* 3.0 ~ 3.5



## Basic Usage

### Start Execution
In command-line, just input like,

```
$ python main.py
```

Python3 is also OK.

```
$ python3 main.py
```

### Input URL
Execution of script start and you will get output like below,

```
$ python main.py
[ E-Hentai Downloader ]
Please input URL of E-Hentai Page.
URL > 
```

And Input E-Hentai's URL like below, 

```
http://g.e-hentai.org/g/.../...
http://g.e-hentai.org/s/.../blurblur-1
http://g.e-hentai.org/s/.../blurblur-2
```

### Download
Input of URL is done, the script get all images in a gallery automatically!
Downloaded images are `E-Hentai_download` folder, and this folder is in 
`~/Pictures`, `~/Picture` or `~/ピクチャ` folder.



## For More Convenience

If you want to get many of images in more automated form,
You should make input within text-file.

First, type E-Hentai's URLs in text-file.

```
http://g.e-hentai.org/g/foobar1/blurblur
http://g.e-hentai.org/s/foobar2/blurblur
http://g.e-hentai.org/s/foobar3/blurblur-2
```

And now, if you name this text-file `sample.txt`,
You should type like this,

```
$ python main.py -f sample.txt
```

and, It's OK. But, this is example, in actual use,
please be careful about text-file path and your current directory.



## Options
* -i ... show usage
* -h ... show usage and optional arguments
* -u, --url [URL ...] ... input e-hentai's url
* -f, --file [FILE-PATH ...] ... input text-file path of e-hentai's url
* --retry [TIMES]... maximum retry (Default: 3 times)
* --sleep [SECONDS] ... sleep between download retry (Default: 900 sec)
* --interval [SECONDS]... interval between download
* --no-resume ... Ignore resume of downloads.
* --no-numbering ... Download image without file-name numbering


