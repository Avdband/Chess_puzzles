import os
import json
import chess
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Путь к базе задач
PUZZLE_FILE = os.path.join("puzzles", "puzzles.json")

def load_puzzles():
    with open(PUZZLE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/puzzle/<int:idx>")
def get_puzzle(idx):
    puzzles = load_puzzles()
    if idx >= len(puzzles):
        return jsonify({"finished": True})
    p = puzzles[idx]
    return jsonify({"fen": p["fen"], "description": p["description"], "total": len(puzzles)})

@app.route("/api/validate", methods=["POST"])
def validate_move():
    data = request.json
    fen = data.get("fen")
    move_san = data.get("move")
    idx = data.get("idx")
    
    puzzles = load_puzzles()
    if idx >= len(puzzles):
        return jsonify({"success": False, "message": "Задачи закончились"})

    puzzle = puzzles[idx]
    board = chess.Board(fen)

    try:
        solution_move = board.parse_san(puzzle["solution_san"])
        user_move = board.parse_san(move_san)

        if user_move == solution_move:
            board.push(user_move)  # Применяем ход для получения нового FEN
            return jsonify({
                "success": True,
                "message": "✅ Верно!",
                "new_fen": board.fen()
            })
        else:
            return jsonify({"success": False, "message": "❌ Неверный ход. Попробуйте ещё раз."})
    except ValueError as e:
        return jsonify({"success": False, "message": f"⚠️ Ошибка: {str(e)}"})

if __name__ == "__main__":
    # Запуск сервера
    app.run(debug=True, host="127.0.0.1", port=5000)