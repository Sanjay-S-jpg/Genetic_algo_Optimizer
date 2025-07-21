from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import importlib
import shutil
import os
import json

app = Flask(__name__)
CORS(app)

PROBLEM_LIST = [
    {"id": "max_ones", "name": "Max Ones"},
    {"id": "tsp", "name": "Traveling Salesman Problem"},
    {"id": "knapsack", "name": "Knapsack Problem"},
    {"id": "bitstring_match", "name": "Bitstring Match"},
    {"id": "sudoku4x4", "name": "Sudoku 4x4"},
     {"id": "deceptive_trap", "name": "Deceptive Trap Function"},
    {"id": "noisy_onemax", "name": "Noisy OneMax"},
    {"id": "rastrigin", "name": "Rastrigin Function"},
    {"id": "royal_road", "name": "Royal Road Function"},
    {"id": "sphere", "name": "Sphere Function"},
    {"id": "multiobjective_schaffer", "name": "Multi-Objective Schaffer Function"},
    {"id": "csv_optimizer", "name": "CSV Optimizer"},
]

@app.route('/')
def index():
    return jsonify({"message": "Backend up!"})

CUSTOM_PROBLEM_DIR = "custom_problems"
if not os.path.exists(CUSTOM_PROBLEM_DIR):
    os.makedirs(CUSTOM_PROBLEM_DIR)

def import_custom_problem(problem_id):
    import importlib.util
    file_path = os.path.join(CUSTOM_PROBLEM_DIR, f"{problem_id}.py")
    spec = importlib.util.spec_from_file_location(f"custom_{problem_id}", file_path)
    if spec is None:
        raise ImportError(f"Cannot find custom problem {problem_id}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def load_problem_module(problem_id):
    if problem_id.startswith("custom:"):
        pid = problem_id.split("custom:")[1]
        return import_custom_problem(pid)
    else:
        return importlib.import_module(f'problems.{problem_id}')

@app.route('/api/problems', methods=['GET'])
def get_problems():
    all_probs = PROBLEM_LIST.copy()
    for fname in os.listdir(CUSTOM_PROBLEM_DIR):
        if fname.endswith(".py"):
            all_probs.append({"id": f"custom:{fname[:-3]}", "name": f"Custom: {fname[:-3]}"})
    return jsonify(all_probs)

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only .csv files allowed'}), 400
    safe_filename = file.filename.replace("/", "_").replace("\\", "_")
    save_path = os.path.join("uploaded_csvs", safe_filename)
    if not os.path.exists("uploaded_csvs"):
        os.makedirs("uploaded_csvs")
    file.save(save_path)
    # Optionally, read headers for preview
    import pandas as pd
    df = pd.read_csv(save_path, nrows=5)
    headers = list(df.columns)
    preview_data = df.to_dict(orient="records")
    return jsonify({'message': 'File uploaded', 'filename': safe_filename, 'headers': headers, 'preview': preview_data})



@app.route('/api/problem_params/<problem_id>', methods=['GET'])
def get_problem_params(problem_id):
    try:
        module = load_problem_module(problem_id)
        fields = module.get_param_fields()
        return jsonify(fields)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/run_problem/<problem_id>', methods=['POST'])
def run_problem(problem_id):
    try:
        module = load_problem_module(problem_id)
        params = request.json
        result, plot_path = module.run_problem(params)
        plot_filename = os.path.basename(plot_path)
        return jsonify({
            "result": result,
            "plotFilename": plot_filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/plot/<plot_filename>')
def get_plot(plot_filename):
    plot_path = os.path.join("plots", plot_filename)
    if os.path.exists(plot_path):
        # Serve as inline by default (for <img> display)
        if request.args.get("download") == "1":
            # For download: force as attachment with filename
            return send_file(plot_path, mimetype='image/png', as_attachment=True, attachment_filename=plot_filename)
        else:
            # For browser display: inline
            return send_file(plot_path, mimetype='image/png')
    else:
        return "No plot found", 404

@app.route('/api/download_solution/<problem_id>', methods=['POST'])
def download_solution(problem_id):
    try:
        module = load_problem_module(problem_id)
        params = request.json
        result, _ = module.run_problem(params)
        solution_json = json.dumps(result, indent=2)
        response = make_response(solution_json)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{problem_id}_solution.json"'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/upload_problem', methods=['POST'])
def upload_problem():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not file.filename.endswith('.py'):
        return jsonify({'error': 'Only .py files allowed'}), 400

    safe_filename = file.filename.replace("/", "_").replace("\\", "_")
    save_path = os.path.join(CUSTOM_PROBLEM_DIR, safe_filename)
    file.save(save_path)
    return jsonify({'message': 'File uploaded', 'filename': safe_filename})

@app.route('/api/custom_problems', methods=['GET'])
def list_custom_problems():
    files = []
    for fname in os.listdir(CUSTOM_PROBLEM_DIR):
        if fname.endswith(".py"):
            files.append({"id": fname[:-3], "name": fname})
    return jsonify(files)

if __name__ == "__main__":
    app.run(debug=True)