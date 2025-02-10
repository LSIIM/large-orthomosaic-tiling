import os
import cv2
import argparse
import numpy as np
from termcolor import colored
import rasterio
from rasterio.windows import Window

def split_image(image_path, tile_width, save_path, project_name):
    print(f"Processando {image_path} para cortes com largura de {tile_width} e salvando em {save_path}")

    # Verifica se o arquivo de entrada existe
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"O arquivo {image_path} não foi encontrado.")

    # Verifica se o diretório de salvamento existe, senão cria
    if not os.path.exists(save_path):
        print(colored("Aviso: O diretório de salvamento não existe e será criado.", "yellow"))
        os.makedirs(save_path)

    try:
        with rasterio.open(image_path) as src:
            img_width = src.width
            img_height = src.height

            # Define a altura do tile igual à largura (tiles quadrados)
            tile_height = tile_width

            # Calcula a quantidade de tiles horizontal e verticalmente
            w_tiles = (img_width + tile_width - 1) // tile_width
            h_tiles = (img_height + tile_height - 1) // tile_height

            n_tiles = w_tiles * h_tiles
            print(f"Criando {n_tiles} tiles ({w_tiles} na horizontal e {h_tiles} na vertical).")

            tile_number = 0
            for i in range(h_tiles):
                for j in range(w_tiles):
                    # Define os limites da janela para o tile
                    x = j * tile_width
                    y = i * tile_height
                    width = min(tile_width, img_width - x)
                    height = min(tile_height, img_height - y)
                    window = Window(x, y, width, height)

                    # Lê somente a janela definida (retornando um array no formato: (bands, height, width))
                    tile = src.read(window=window)

                    # Se a imagem tiver mais de um canal, transpõe para (height, width, channels)
                    if tile.shape[0] > 1:
                        tile = np.transpose(tile, (1, 2, 0))
                    else:
                        tile = tile[0]

                    # Verifica se o tile contém alguma informação (pelo menos um pixel diferente de zero)
                    if not np.all(tile == 0):
                        tile_filename = f"{project_name}_tile_{tile_number}.png"
                        output_path = os.path.join(save_path, tile_filename)
                        cv2.imwrite(output_path, tile)
                        print(f"Tile {tile_number} salvo em {output_path}")
                    else:
                        print(f"Tile {tile_number} vazio, ignorado.")

                    tile_number += 1

    except Exception as e:
        print(colored(f"Ocorreu um erro durante o processamento: {e}", 'red'))
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Divide uma imagem .tif em tiles sem carregar a imagem inteira na memória."
    )
    parser.add_argument("input_image_path", type=str, help="Caminho da imagem .tif")
    parser.add_argument("tile_width", type=int, help="Largura (e altura) de cada tile")
    parser.add_argument("save_path", type=str, help="Caminho para salvar os tiles")
    parser.add_argument("project_name", type=str, help="Nome do projeto")
    args = parser.parse_args()
    split_image(args.input_image_path, args.tile_width, args.save_path, args.project_name)
