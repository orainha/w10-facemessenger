<p align="center">
  <img src="https://user-images.githubusercontent.com/48807108/85414813-7efba700-b564-11ea-85a6-2098fe48de87.png" width="64"/>
</p>

## About

W10-FaceMessenger is a forensic analysis tool designed to extract the most significant artifacts produced by the usage of the Windows Store application Messenger (Beta) by Facebook Inc.

This tool is currently capable of extracting the following content:
- Contacts
- Messages
- Cached images
- Deleted database records

## Supported platforms

W10-FaceMessenger is designed to work with Windows.

Support for other platforms is not planned for the near future.

## Requirements

For the time being, you must install [Python 3](https://www.python.org/) and run ```pip install -r requirements.txt```.

We will be providing binary packages soon.

## Usage

W10-FaceMessenger must point to a Windows user profile directory such as `C:\Users\ricardoapl`.

Example:

```
python3.exe .\w10-facemessenger\main.py
            --input C:\Users\ricardoapl
            --output C:\Users\ricardoapl\Desktop
            --format csv
            --delimiter :
```

## Authors

This software was originally developed by Osvaldo Rainha ([**@orainha**](https://github.com/orainha)) and Ricardo Lopes ([**@ricardoapl**](https://github.com/ricardoapl)) under the guidance of Miguel Frade ([**@mfrade**](https://github.com/mfrade)) and Patrício Domingues ([**@PatricioDomingues**](https://github.com/PatricioDomingues/)).

## License

W10-FaceMessenger is licensed under the MIT License.

Furthermore, it makes use of:

- [Axios](https://github.com/axios/axios)
- [Bootstrap](https://getbootstrap.com/)
- [Hindsight](https://github.com/obsidianforensics/hindsight)
- [Undark](https://pldaniels.com/undark)