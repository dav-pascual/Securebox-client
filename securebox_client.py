#!/usr/bin/python3
"""Cliente SecureBox
"""

import argparse
import config
import user
import cipher
import file


def main():
    """Funcion main. Procesado de parametros de entrada
       y flujo del programa
    """
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create_id", nargs=2, metavar=("nombre", "email"),
                        help="Crea una nueva identidad.")
    group.add_argument("--search_id", metavar="cadena",
                       help="Busca un usuario con nombre o correo. Uso: --search_id cadena")
    group.add_argument("--delete_id", metavar="id",
                       help="Borra la identidad con ID id.")
    group.add_argument("--upload", metavar="fichero",
                       help="Envia un fichero a usuario especificado con la opcion --dest_id.")
    group.add_argument("--list_files", action="store_true",
                       help="Lista todos los ficheros pertenecientes al usuario.")
    group.add_argument("--download", metavar="id_fichero",
                       help="Recupera un fichero con ID id_fichero y emisor especificado con la "
                            "opcion --source_id del sistema, verifica firma y descifra.")
    group.add_argument("--delete_file", metavar="id_fichero",
                       help="Borra un fichero del sistema con ID id_fichero.")
    group.add_argument("--encrypt", metavar="fichero",
                       help="Cifra un fichero, de forma que puede ser descifrado por otro usuario, cuyo ID es "
                            "especificado con la opción --dest_id.")
    group.add_argument("--sign", metavar="fichero", help="Firma un fichero.")
    group.add_argument("--enc_sign", metavar="fichero",
                       help="Cifra y firma un fichero, combinando funcionalmente las dos opciones anteriores "
                            "y recibiendo ID del fichero con la opcion --dest_id.")
    parser.add_argument("--dest_id", metavar="id",
                        help="ID del receptor del fichero.")
    parser.add_argument("--source_id", metavar="id",
                        help="ID del emisor del fichero.")
    args = parser.parse_args()

    if args.create_id:
        user.create_id(args.create_id[0], args.create_id[1])
    elif args.search_id:
        user.search_id(args.search_id)
    elif args.delete_id:
        user.delete_id(args.delete_id)
    elif args.upload:
        if args.dest_id:
            file.upload(args.upload, args.dest_id)
        else:
            parser.print_help()
    elif args.list_files:
        file.list_files()
    elif args.download:
        if args.source_id:
            file.download(args.download, args.source_id)
        else:
            parser.print_help()
    elif args.delete_file:
        file.delete_file(args.delete_file)
    elif args.encrypt:
        if args.dest_id:
            cipher.encrypt(args.encrypt, args.dest_id)
        else:
            parser.print_help()
    elif args.sign:
        cipher.sign(args.sign)
    elif args.enc_sign:
        if args.dest_id:
            cipher.sign(args.enc_sign)
            cipher.encrypt(config.SIGNED_PREFIX + args.enc_sign, args.dest_id)
        else:
            parser.print_help()


if __name__ == '__main__':
    main()
