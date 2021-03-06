#!/usr/bin/python3
"""Module in charge of the management of uploading and downloading files.
"""
import requests
import config
import os
import sys
import cipher
import re


def upload(fichero, dest_id):
    """Envia un fichero a un usuario subiendolo al servidor,
       firmandolo y encriptandolo de antemano.
       IN:
            - fichero: nombre del fichero que se desea subir a SecureBox
            - dest_id: ID del usuario a quien lo queremos enviar
    """
    # Firma y encriptacion del fichero
    print("Solicitado envio de fichero a SecureBox")
    cipher.sign(fichero)
    cipher.encrypt(config.SIGNED_PREFIX + fichero, dest_id)

    url = config.API_URL + config.ENDPOINT['upload']
    filepath = os.path.abspath(os.path.join(config.FILES_DIR, config.ENC_PREFIX + config.SIGNED_PREFIX + fichero))

    # LLamada al API Rest
    headers = {"Authorization": "Bearer " + config.TOKEN}
    files = {'ufile': (fichero, open(filepath, "rb"))}
    r = requests.post(url, files=files, headers=headers)
    if not r.ok:
        print("\n-> Error al subir archivo {}\n"
              "\t- Codigo: {}\n\t- Info: {}".format(fichero, r.json()['http_error_code'], r.json()['description']))
        sys.exit()
    else:
        print("-> Subiendo fichero a servidor...OK")
        print("Subida realizada correctamente, ID del fichero: {}".format(r.json()['file_id']))


def download(file_id, source_id):
    """Recupera un fichero de SecureBox, lo descifra y verifica su firma
       IN:
            - file_id: id del fichero que se desea descargar de SecureBox
            - source_id: ID del usuario que nos lo envia
    """
    url = config.API_URL + config.ENDPOINT['download']
    # LLamada al API Rest
    headers = {"Authorization": "Bearer " + config.TOKEN}
    args = {'file_id': file_id}
    r = requests.post(url, json=args, headers=headers)
    if not r.ok:
        print("\n-> Error al descargar fichero con ID {}\n"
              "\t- Codigo: {}\n\t- Info: {}".format(file_id, r.json()['http_error_code'], r.json()['description']))
        sys.exit()
    else:
        print("-> Descargando fichero de SecureBox...OK")
        print("-> {} bytes descargados correctamente".format(r.headers['Content-Length']))
        iv = r.content[:16]
        enc_s_key = r.content[16:272]
        enc_msg = r.content[272:]
        s_key = cipher.decrypt_s_key(enc_s_key)             # Descifrar clave simetrica con RSA
        msg = cipher.decrypt_msg(enc_msg, iv, s_key)        # Descifrar mensaje con AES
        payload = cipher.verify_sign(msg, source_id)        # Verificar firma
        d = r.headers['content-disposition']                # Obtener nombre del fichero
        fname = re.findall("filename=(.+)", d)[0]
        fname = fname.replace('"', '')
        filepath = os.path.abspath(os.path.join(config.FILES_DIR, fname))
        with open(filepath, "wb") as file:
            file.write(payload)                             # Guardar fichero
        print("Fichero {} descargado y verificado correctamente".format(fname))


def list_files():
    """Lista todos los ficheros del usuario con token almacenado
       en el fichero de configuracion.
    """
    url = config.API_URL + config.ENDPOINT['list']
    # LLamada al API Rest
    headers = {"Authorization": "Bearer " + config.TOKEN}
    r = requests.post(url, headers=headers)
    if not r.ok:
        print("\n-> Error al listar ficheros\n"
              "\t- Codigo: {}\n\t- Info: {}".format(r.json()['http_error_code'], r.json()['description']))
        sys.exit()
    else:
        files = r.json()['files_list']
        if r.json()['num_files'] > 0:
            print("{} ficheros encontrados:".format(r.json()['num_files']))
            for index, file in enumerate(files):
                print("[{}] ID del fichero: {}".format(index + 1, file))
        else:
            print("No se han encontrado ficheros para el usuario con este token.")


def delete_file(file_id):
    """Borra un fichero con el ID especificado del sistema.
       IN:
            - file_id: id del fichero que se desea borrar de SecureBox
    """
    url = config.API_URL + config.ENDPOINT['delete_file']
    # LLamada al API Rest
    headers = {"Authorization": "Bearer " + config.TOKEN}
    args = {'file_id': file_id}
    r = requests.post(url, json=args, headers=headers)
    if not r.ok:
        print("\n-> Error al eliminar fichero con ID {}\n"
              "\t- Codigo: {}\n\t- Info: {}".format(file_id, r.json()['http_error_code'], r.json()['description']))
        sys.exit()
    else:
        print("-> Borrando fichero...OK")
        print("El fichero con ID {} ha sido borrado.".format(file_id))
