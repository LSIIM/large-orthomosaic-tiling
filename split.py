import argparse
import os
import cv2
from termcolor import colored
from tqdm import tqdm


os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(pow(2,40))

import tifffile as tifi

def split_image(image_path, tile_width, save_path):
    print(f"Processando {image_path} para cortes com largura de {tile_width} e salvando em {save_path}")
    
    # Verifica se a imagem de entrada existe
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"O arquivo {image_path} não foi encontrado.")

    # Verifica se o caminho de salvamento existe, senão cria
    if not os.path.exists(save_path):
        print(colored("Aviso: O diretório de salvamento não existe e será criado.", "yellow"))
        os.makedirs(save_path)

    try:
        # Carrega a imagem com OpenCV
        print("Lendo imagem original (isso pode levar um tempo e usar MUITA RAM)")
        image = tifi.imread(image_path)
        print("Dale@@ Terminei de carregar a grotescamente grande imagem original")
        # image = cv2.imread(image_path)
        img_height, img_width = image.shape[:2]
        tile_height = img_height // (img_width // tile_width)

        # Calcula quantas imagens serão criadas com base na largura e altura definidas
        w_tiles = img_width // tile_width
        if img_width % tile_width != 0:
            w_tiles += 1
        h_tiles = img_height // tile_height
        if img_height % tile_height != 0:
            h_tiles += 1

        n_tiles = w_tiles * h_tiles
        print(f"Criando {n_tiles} tiles para subdividir a imagem original ({w_tiles} na horizontal e {h_tiles} na vertical).\nTile: {tile_width}x{tile_height} | Original: {img_width}x{img_height}")
        
        # Cria e salva as imagens divididas
        tile_number = 0
        for y in range(0, img_height, tile_height):
            for x in range(0, img_width, tile_width):
                tile = image[y:y+tile_height, x:x+tile_width]
                tile_filename = f"{os.path.splitext(os.path.basename(image_path))[0]}_tile_{tile_number}.tif"
                cv2.imwrite(os.path.join(save_path, tile_filename), tile)
                tile_number += 1
                print(f"Cortando o tile {tile_number}")

    except Exception as e:
        print(colored(f"Ocorreu um erro durante o processamento: {e}", 'red'))
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Divide uma imagem .tif em várias partes.")
    parser.add_argument("input_image_path", type=str, help="Caminho da imagem .tif")
    parser.add_argument("tile_width", type=int, help="Largura de cada parte da imagem")
    parser.add_argument("save_path", type=str, help="Caminho para salvar as imagens divididas")

    args = parser.parse_args()
    split_image(args.input_image_path, args.tile_width, args.save_path)
