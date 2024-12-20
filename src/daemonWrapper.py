#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import sys

def run_cpp_program(arg1, arg2, delay_ms):
    """Lance le programme C++ en tant que sous-processus et capte sa sortie en temps réel,
       avec un délai configurable entre chaque ligne de sortie."""
    try:
        # Convertir les arguments en chaînes
        arg1_str = str(arg1)
        arg2_str = str(arg2)

        print "Lancement de la commande avec arguments : {}, {}, délai : {} ms".format(arg1_str, arg2_str, delay_ms)

        # Commande pour exécuter le programme C++ avec les arguments
        command = ['./daemon', arg1_str, arg2_str]

        # Lance le programme C++ en tant que sous-processus avec redirection vers stdout
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1, universal_newlines=True)

        # Dernière ligne lue (initialement vide)
        last_line = ""

        # Lire la sortie ligne par ligne en temps réel
        while True:
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break  # Fin du processus

            if line:
                # Si une nouvelle ligne est disponible, la mettre à jour
                last_line = line.strip()

            # Afficher la dernière ligne disponible
            if last_line:
                print "Dernière sortie : {}".format(last_line)

            # Attendre avant de lire à nouveau selon le délai spécifié
            time.sleep(delay_ms / 1000.0)

        # Vérification des erreurs
        stderr = process.stderr.read()
        if stderr:
            print "Erreur : {}".format(stderr)

        process.stdout.close()
        process.stderr.close()
        process.wait()

    except Exception as e:
        print "Erreur lors de l'exécution : {}".format(e)

if __name__ == "__main__":
    # Vérifier les arguments passés à la ligne de commande
    if len(sys.argv) != 4:
        print "Usage: python2 daemonWrapper.py <arg1> <arg2> <delay_ms>"
        sys.exit(1)

    # Récupérer les arguments de ligne de commande
    arg1 = int(sys.argv[1])
    arg2 = int(sys.argv[2])
    delay_ms = int(sys.argv[3])

    # Appeler la fonction avec les arguments passés
    run_cpp_program(arg1, arg2, delay_ms)