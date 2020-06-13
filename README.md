## About

W10-FaceMessenger is a forensic analysis tool designed to extract the most significant artifacts produced by the usage of the Windows Store application Messenger (Beta) by Facebook Inc.

As of now, W10-FaceMessenger is capable of extracting the following content:
- Contacts
- Messages
- Cached images (from user profile searches, messages, etc.)
- Deleted database records

These scripts are designed to work with Windows 10.

Support for other platforms is not planned for the near future.

## Requirements

For the time being, you must install [Python 3](https://www.python.org/) and run ```pip install -r requirements.txt```.

We will be providing binary packages soon.

## Authors

This software was developed by Osvaldo Rainha ([**@orainha**](https://github.com/orainha)) and Ricardo Lopes ([**@ricardoapl**](https://github.com/ricardoapl)) under the guidance of Miguel Frade and Patrício Domingues.

## License

This software is distributed under the MIT License.

Furthermore, it makes use of:

- [Axios](https://github.com/axios/axios)
- [Bootstrap](https://getbootstrap.com/)
- [Hindsight](https://github.com/obsidianforensics/hindsight)
- [Undark](https://pldaniels.com/undark)