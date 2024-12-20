#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import os
import time
import tempfile

def run_cpp_program(arg1, arg2, delay_ms):
    """Lance le programme C++ en tant que sous-processus et redirige ses sorties vers un fichier temporaire."""
    try:
        # Commande pour exécuter le programme C++
        command = ['./daemon', str(arg1), str(arg2)]

        # Crée un fichier temporaire pour utiliser comme pipe
        with tempfile.NamedTemporaryFile(delete=False) as pipe:
            pipe_path = pipe.name

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        with open(pipe_path, 'w') as pipe:
            last_line = None
            while True:
                line = process.stdout.readline()
                if line:
                    last_line = line.strip()
                if last_line:
                    pipe.write(last_line + '\n')
                    pipe.flush()
                time.sleep(delay_ms / 1000.0)
                if process.poll() is not None:
                    break

            error_output = process.stderr.read()
            if error_output:
                pipe.write("Erreur : {}\n".format(error_output))
                pipe.flush()

        return pipe_path

    except Exception as e:
        with open(pipe_path, 'w') as pipe:
            pipe.write("Erreur lors de l'exécution : {}\n".format(e))
            pipe.flush()
        return None
