from flask import Flask, render_template, jsonify
import json
import os
import random

app = Flask(__name__)

def load_questions():
    path = os.path.join(os.path.dirname(__file__), 'questions.json')
    if not os.path.exists(path): return {"choice": [], "fill_in": [], "true_false": []}
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/exam/<paper_id>')
def exam(paper_id):
    data = load_questions()
    # 筛选该试卷的所有题目
    exam_data = {
        "choice": [q for q in data['choice'] if q['paper_id'] == paper_id],
        "true_false": [q for q in data['true_false'] if q['paper_id'] == paper_id],
        "fill_in": [q for q in data['fill_in'] if q['paper_id'] == paper_id]
    }
    return render_template('exam.html', paper_id=paper_id, paper=exam_data)

@app.route('/endless')
def endless_mode():
    return render_template('endless.html')

@app.route('/api/all_questions')
def get_all_questions():
    """返回所有题目用于无尽模式"""
    data = load_questions()
    all_q = []
    # 统一格式化
    for q in data['choice']:
        all_q.append({**q, "category": "单选题"})
    for q in data['true_false']:
        all_q.append({**q, "category": "判断题"})
    for q in data['fill_in']:
        all_q.append({**q, "category": "填空题"})
    
    # 随机打乱
    random.shuffle(all_q)
    return jsonify(all_q)

if __name__ == '__main__':
    app.run(debug=True, port=5000)