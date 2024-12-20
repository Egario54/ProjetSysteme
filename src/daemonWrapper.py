#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import threading
import sys
import time


def run_cpp_program(arg1, arg2, delay_ms):
    """Lance le programme C++ en tant que sous-processus et redirige ses sorties."""
    try:
        # Commande pour exécuter le programme C++ avec les arguments
        command = ['./daemon', str(arg1), str(arg2)]

        # Lancer le sous-processus
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Variable pour stocker la dernière sortie lue
        last_line = None

        while True:
            # Lire une ligne dans la sortie standard
            line = process.stdout.readline()
            if line:  # Si une nouvelle ligne est disponible
                last_line = line.strip()  # Mise à jour de la dernière ligne
            if last_line:  # Afficher toujours la dernière ligne lue
                sys.stdout.write(last_line + '\n')
                sys.stdout.flush()
            time.sleep(delay_ms / 1000.0)  # Attendre le délai spécifié

            # Vérifier si le processus est terminé
            if process.poll() is not None:
                break

        # Récupérer et afficher les erreurs s'il y en a
        if process.returncode != 0:
            error_output = process.stderr.read()
            sys.stderr.write("Erreur : {}\n".format(error_output))
            sys.stderr.flush()

    except Exception as e:
        sys.stderr.write("Erreur lors de l'exécution : {}\n".format(e))
        sys.stderr.flush()


def main():
    """Point d'entrée principal."""
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: python run_daemon.py <arg1> <arg2> <delay_ms>\n")
        sys.exit(1)

    try:
        # Convertir les arguments en entiers
        arg1 = int(sys.argv[1])
        arg2 = int(sys.argv[2])
        delay_ms = int(sys.argv[3])
        if delay_ms <= 0:
            raise ValueError("Le délai doit être un entier positif.")
    except ValueError:
        sys.stderr.write("Les arguments doivent être des chiffres et le délai doit être positif.\n")
        sys.exit(1)

    # Lancer le thread pour exécuter le programme C++
    thread = threading.Thread(target=run_cpp_program, args=(arg1, arg2, delay_ms))
    thread.start()
    thread.join()


if __name__ == "__main__":
    main()