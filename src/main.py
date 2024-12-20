#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
import subprocess
import threading
import time

app = Flask(__name__)


def run_cpp_program(arg1, arg2, delay_ms):
    """Exécute le programme C++ avec les arguments donnés."""
    try:
        # Commande pour exécuter le programme C++
        command = ['./daemon', str(arg1), str(arg2)]

        # Lancer le programme en tant que sous-processus
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Stocker les sorties
        outputs = []
        last_line = None

        while True:
            line = process.stdout.readline()
            if line:  # Si une nouvelle ligne est disponible
                last_line = line.strip()
                outputs.append(last_line)
            elif last_line:  # Répéter la dernière ligne si aucune nouvelle donnée
                outputs.append(last_line)
            time.sleep(delay_ms / 1000.0)  # Pause entre les affichages

            # Vérifier si le processus est terminé
            if process.poll() is not None:
                break

        # Ajouter les erreurs éventuelles
        if process.returncode != 0:
            error_output = process.stderr.read()
            outputs.append("Erreur : {}".format(error_output))

        return outputs

    except Exception as e:
        return ["Erreur lors de l'exécution : {}".format(e)]


@app.route('/run', methods=['POST'])
def run():
    """Point de terminaison pour lancer le programme."""
    # Récupérer les paramètres de la requête
    data = request.json
    if not data:
        return jsonify({"error": "Requête invalide. Donnez les paramètres arg1, arg2, delay_ms."}), 400

    try:
        arg1 = int(data.get("arg1", 0))
        arg2 = int(data.get("arg2", 0))
        delay_ms = int(data.get("delay_ms", 100))
        if delay_ms <= 0:
            raise ValueError("Le délai doit être un entier positif.")
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Lancer le programme et collecter les sorties
    outputs = run_cpp_program(arg1, arg2, delay_ms)
    return jsonify({"outputs": outputs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)