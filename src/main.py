# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request, render_template, Response
import time
import subprocess

app = Flask(__name__)

def run_cpp_program(arg1, arg2, delay_ms):
    """Lance le programme C++ et renvoie sa sortie."""
    command = ['./daemon', str(arg1), str(arg2)]  # Assurez-vous que le programme C++ se trouve bien dans le chemin spécifié

    # Lancer le programme C++ avec subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    return process

@app.route('/')
def home():
    """Route pour afficher la page HTML."""
    return render_template('Main.html')

@app.route('/run', methods=['POST'])
def run():
    """Exécute le programme C++ via POST."""
    try:
        # Extraire les données JSON
        data = request.get_json()
        print("Données reçues :", data)  # Pour le débogage

        args = data.get("args", {})
        arg1 = int(args.get("arg1", 0))
        arg2 = int(args.get("arg2", 0))
        delay_ms = int(args.get("delay_ms", 100))

        if delay_ms <= 0:
            return jsonify({"error": "Le délai doit être un entier positif."}), 400

        # Exécuter le programme C++ en fond
        process = run_cpp_program(arg1, arg2, delay_ms)

        return jsonify({"message": u"Programme C++ lancé avec succès"})

    except Exception as e:
        return jsonify({"error": u"Erreur lors de l'exécution: {0}".format(str(e))}), 400


@app.route('/run_stream')
def run_stream():
    """Retourne un flux SSE avec les sorties du programme C++."""
    try:
        # Obtenez les arguments de la requête GET
        arg1 = request.args.get('arg1', type=int)
        arg2 = request.args.get('arg2', type=int)
        delay_ms = request.args.get('delay_ms', type=int)

        # Vérifiez que les arguments sont valides
        if arg1 is None or arg2 is None or delay_ms is None:
            return u"Tous les paramètres sont requis", 400

        # Lancer le programme C++ via subprocess
        process = run_cpp_program(arg1, arg2, delay_ms)

        def generate():
            """Génère un flux SSE avec la sortie du programme C++."""
            while True:
                output = process.stdout.readline()
                if output == b'' and process.poll() is not None:
                    break  # Fin du programme
                if output:
                    yield u"data: {0}\n\n".format(output.decode('utf-8').strip())
                time.sleep(delay_ms / 1000.0)  # Attente entre les sorties

            # En cas d'erreur, envoyez l'erreur stderr
            error_output = process.stderr.read()
            if error_output:
                yield u"data: Erreur: {0}\n\n".format(error_output.decode('utf-8').strip())

        # Retourner la réponse SSE
        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({"error": u"Erreur lors de la diffusion : {0}".format(str(e))}), 400


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)