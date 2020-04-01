import sys
import requests

IMG_URL = "https://scontent.flis9-1.fna.fbcdn.net/v/t1.0-1/c28.28.343.344a/s200x200/429402_331194530255815_181581311_n.jpg?_nc_cat=108&_nc_sid=dbb9e7&_nc_ohc=3bCljBHgOSYAX89Fa6D&_nc_ad=z-m&_nc_cid=0&_nc_zor=9&_nc_ht=scontent.flis9-1.fna&oh=6e26696f72e0d4fc27285c95f3b066f8&oe=5EA3D1B4"
req = requests.get(IMG_URL)

if req.status_code == requests.codes.ok:
    try:
        ficheiro_imagem = "img_0.png"
        file_write = open(ficheiro_imagem, 'wb+')
        file_write.write(req.content)
    except IOError as error:
        print(error)
