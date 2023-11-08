import os
import pandas as pd
import requests
import json
from PIL import Image
from io import BytesIO

# Reemplaza 'tu_archivo.xlsx' con la ruta al archivo Excel que contiene las URLs de las imágenes
excel_path = 'train.xlsx'
# Reemplaza 'Columna_URL' con el nombre de la columna que contiene las URLs de las imágenes en el archivo Excel
url_column_name = 'image_url'
# Columnas adicionales para incluir en el JSON
_column = 'Title'
label_column = 'label'
# Reemplaza 'imagenes' con la ruta de la carpeta donde deseas guardar las imágenes descargadas
images_dir = 'imagenes'
# Nombre del archivo JSON para guardar los registros de imágenes descargadas
json_file = 'imagenes_descargadas.json'
# Nombre del archivo Excel para guardar los registros de fallas
error_file = 'errores_descarga.xlsx'

# Crear directorio para las imágenes si no existe
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Carga el archivo Excel
df = pd.read_excel(excel_path)

# Listas para almacenar las filas procesadas
descargados = []
errores = []

# Función para descargar y guardar una imagen
def download_image(row, directory):
    url = row[url_column_name]
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verificar que la solicitud fue exitosa
        image = Image.open(BytesIO(response.content))
        # El nombre del archivo se basa en la última parte de la URL
        filename = os.path.basename(url)
        image.save(os.path.join(directory, filename))
        print(f"Descargada y guardada {filename}")
        return filename  # Retorna el nombre del archivo si la descarga fue exitosa
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"Otro error ocurrió: {e}")
        return None  # Retorna None si ocurrió un error

# Itera sobre las filas del DataFrame y descarga las imágenes
for index, row in df.iterrows():
    filename = download_image(row, images_dir)
    if filename:  # Si la descarga fue exitosa y se retorna un nombre de archivo
        descargados.append({
            title_column: row[title_column],
            'nombre_archivo': filename,
            label_column: row[label_column]
        })
    else:  # Si hubo un error, agrega la fila completa a la lista de errores
        errores.append(row)

# Convertir la lista de descargados en un JSON y guardarlo
with open(json_file, 'w') as f:
    json.dump(descargados, f, indent=4)
print(f"Se ha creado el archivo JSON '{json_file}' con los registros de las imágenes descargadas correctamente.")

# Convertir la lista de errores en un DataFrame y guardarlo en Excel
if errores:
    errores_df = pd.DataFrame(errores)
    errores_df.to_excel(error_file, index=False)
    print(f"Se ha creado el archivo Excel '{error_file}' con los registros de las imágenes que tuvieron errores de descarga.")
