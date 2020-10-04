## Overview

W10-FaceMessenger is a forensic analysis tool designed to extract the most significant artifacts produced by the usage of the Microsoft Store application [Messenger (Beta)](https://www.microsoft.com/en-us/p/messenger-beta/9nblggh2t5jk) by Facebook Inc.

This tool is currently capable of extracting the following content:

- Contacts
- Messages
- Cached images
- Deleted database records

## Installation

Clone this repository into your local machine and run ```pip install -r requirements.txt```.

As an alternative, you can use one of the self-contained executables we provide (see [Releases](https://github.com/ricardoapl/w10-facemessenger/releases)).

## Requirements

For the time being, you must run Microsoft Windows.

If you choose to run from source, you will need [Python 3](https://www.python.org/).

There's no need to install Python or any other software if you opt for the provided binary releases.

## Usage

W10-FaceMessenger must point to a Windows user profile directory such as `C:\Users\ricardoapl`.

Running `python.exe .\w10-facemessenger\main.py --help` should yield the following help message:

```
usage: main.py [-h] --input INPUT [--output OUTPUT] [--format {html,csv}] [--delimiter DELIMITER] [--depth {fast,complete}]

Windows 10 Messenger (Beta) forensic analysis tool

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT       set output directory for report (defaults to Desktop)
  --format {html,csv}   choose report format (defaults to "html")
  --delimiter DELIMITER
                        specify csv report delimiter (defaults to ",")
  --depth {fast,complete}
                        fast: no images, no internet required; complete: with images, internet required, slower

required arguments:
  --input INPUT         set path to user directory
```

## Known issues

The self-contained executables we provide are currently being flagged as malicious by some anti-malware solutions. In case of doubt, feel free to bundle the binaries yourself with PyInstaller and the provided ```pyinstaller.spec``` file.

## Support

Please use the [issue tracker](https://github.com/ricardoapl/w10-facemessenger/issues) to ask for help, request a new feature or report any bugs.

## Roadmap

Future work includes decoupling the ingest and report parts into separate tools, similar to what happens with other UNIX-like software.

Other planned changes:

- [ ] Add JSON and SQLite output formats
- [ ] Remove CSV and HTML output formats
- [ ] Parse other content type from cache (videos, text files, etc)
- [ ] Parse SQLite WAL files
- [ ] Parse RoamingState
- [ ] Add support for non-beta version of Messenger
- [ ] Add support for GNU/Linux and macOS

## Contributing

Have a look at the [contributing guidelines](https://github.com/ricardoapl/w10-facemessenger/blob/master/CONTRIBUTING.md) before submitting any pull request.

## Authors

This software was originally developed by Osvaldo Rainha ([**@orainha**](https://github.com/orainha)) and Ricardo Lopes ([**@ricardoapl**](https://github.com/ricardoapl)) under the guidance of Miguel Frade ([**@mfrade**](https://github.com/mfrade)) and Patrício Domingues ([**@PatricioDomingues**](https://github.com/PatricioDomingues/)).

## License

W10-FaceMessenger is available under the terms of the MIT License.

Furthermore, it makes use of:

- [Axios](https://github.com/axios/axios) (MIT License)
- [Bootstrap](https://getbootstrap.com/) (MIT License)
- [Hindsight](https://github.com/obsidianforensics/hindsight) (Apache-2.0 License)
- [Undark](https://pldaniels.com/undark) (Custom License)