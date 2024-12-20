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
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

@app.route('/run', methods=['POST'])
def run():
    try:
        data = request.get_json()
        print("TEST : ",request.get_json())
        if not data or 'args' not in data:
            return jsonify({"error": "Les donnees JSON sont manquantes ou incorrectes."}), 400

        args = data['args']
        arg1 = int(args.get("arg1", 0))
        arg2 = int(args.get("arg2", 0))
        delay_ms = int(args.get("delay_ms", 100))
        if delay_ms <= 0:
            raise ValueError("Le delai doit etre un entier positif.")

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    outputs = run_cpp_program(args)
    return jsonify({"outputs": outputs})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
