from flask import Flask, request, jsonify, render_template
import subprocess
import threading
import time
import sys

app = Flask(__name__)

def run_cpp_program(args):
    try:
        command = ['./daemon', str(args['arg1']), str(args['arg2'])]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        outputs = []
        last_line = None

        while True:
            line = process.stdout.readline()
            if line:
                last_line = line.strip()
                outputs.append(last_line)
            elif last_line:
                outputs.append(last_line)
            time.sleep(args['delay_ms'] / 1000.0)

            if process.poll() is not None:
                break

        if process.returncode != 0:
            error_output = process.stderr.read()
            outputs.append("Erreur : {}".format(error_output))

        return outputs

    except Exception as e:
        return ["Erreur lors de l'execution : {}".format(e)]

@app.route('/')
def home():
    return render_template('Main.html')

@app.route('/run', methods=['POST'])
def run():
    data = request.json  # Recuperer le JSON envoye par le client
    if not data:
        return jsonify({"error": "No JSON data received."}), 400

    try:
        # Extraire les arguments attendus
        arg1 = int(data.get("arg1"))
        arg2 = int(data.get("arg2"))
        delay_ms = int(data.get("delay_ms"))
    except (TypeError, ValueError) as e:
        return jsonify({"error": "Invalid parameter type or missing parameters."}), 400

    # Appeler la fonction avec les arguments
    outputs = run_cpp_program({"arg1": arg1, "arg2": arg2, "delay_ms": delay_ms})
    return jsonify({"outputs": outputs})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
