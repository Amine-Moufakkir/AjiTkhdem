
import logging

# Configuration : On décide d'écrire dans un fichier et de capturer dès le niveau DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='w' # 'w' pour écraser à chaque fois, 'a' pour ajouter à la suite
)