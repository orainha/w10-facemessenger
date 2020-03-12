import sys
import requests

img_url = "https://scontent.flis9-1.fna.fbcdn.net/v/t1.15752-9/84761297_116424783138307_5346558350156890112_n.jpg?_nc_cat=106&_nc_ohc=TUM_0ii8rCcAX-bY-cv&_nc_ht=scontent.flis9-1.fna&oh=851647b5596fb87828ed0fabf8d532d9&oe=5E51A645"
req = requests.get(img_url)

if req.status_code == requests.codes.ok:
   try:
    #open file stream
     ficheiro_imagem = "img_0.png"
     file_write = open(ficheiro_imagem, 'wb+')
     file_write.write(req.content)
   except IOError as error:
     print (error)

#print (req.content)
#
#ficheiro_imagens = "C:\\Users\\user\\Desktop\\python\\imagens\\img_"+counter+".png"
#counter = counter + 1
#try:
# open file stream
 #  file_write = open(ficheiro_imagens, 'w+')

    
