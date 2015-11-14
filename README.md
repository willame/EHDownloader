# EHDownloader

You can download images in [e-hentai.org](http://e-hentai.org/) with this script.



## Environment
* Windows
* Mac
* Linux

In Windows, EXE file is available without Python.
In Linux or Mac, This script run in Python(2 or 3) environment.



## Python Version
* 3.0 ~ 3.5



## Basic Usage

### Start Execution
In command-line, just input like,

```
$ python main.py

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
http://g.e-hentai.org/s/foobar3/blurblur
```

And now, if you name this text-file `sample.txt`,
you should type like this,

```
$ python ehdownloader.py -f sample.txt
```

and, It's OK. But, this is example, in actual use,
please be careful about text-file path and your current directory.

If your current directory is `/user/home/Desktop`, script path is `/user/home/Desktop/EHDownloader/src`, and text-file path, `/user/home/Desktop/foo/input.txt`, you should input below,

```
$ python EHDownloader/ehdownloader.py -f foo/input.txt
```


## Options
* -i ...  show usage
* -h, --help ...  show this help message and exit

* -u [URL [URL ...]], --url [URL [URL ...]] ... Read URL of E-Hentai org
* -f [FILENAME [FILENAME ...]], --filename [FILENAME [FILENAME ...]] ...  Read URLs of E-Hentai org from text file
* --retry TIMES ...  Times of retry download (Default: 3 times)
* --sleep SECONDS ...  Sleep time until next retry (Default: 1800 sec)
* --interval SECONDS ...  Interval between downloads
* --no-resume ...  Ignore resume of downloads.
* --no-numbering ...  Download image without file-name numbering
* --no-filecheck ...  Download image without file-corruption check

