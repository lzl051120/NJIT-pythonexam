import json
import re
import os

# --- 内置答案库 (由AI预先生成) ---
TF_ANSWERS = {
    "1": "T", "2": "T", "3": "T", "4": "F", "5": "F", "6": "T", "7": "T", "8": "F", "9": "T", "10": "F",
    "11": "F", "12": "F", "13": "F", "14": "T", "15": "F", "16": "F", "17": "T", "18": "T", "19": "T", "20": "T",
    "21": "F", "22": "T", "23": "T", "24": "F", "25": "F", "26": "F", "27": "T", "28": "F", "29": "T", "30": "T",
    "31": "T", "32": "F", "33": "F", "34": "F", "35": "T", "36": "F", "37": "F", "38": "F", "39": "F", "40": "T",
    "41": "T", "42": "F", "43": "T", "44": "F", "45": "T", "46": "T", "47": "F", "48": "T", "49": "F", "50": "T",
    "51": "F", "52": "F", "53": "T", "54": "F", "55": "T", "56": "T", "57": "F", "58": "F", "59": "T", "60": "F",
    "61": "T", "62": "F", "63": "F", "64": "T", "65": "T", "66": "T", "67": "T", "68": "T", "69": "T", "70": "F",
    "71": "T", "72": "T", "73": "T"
}

FILL_ANSWERS = {
    "1": "4", "2": "NoneType", "3": "False", "4": "5", "5": "有序",
    "6": "[1, 2, 3]", "7": "None", "8": "get", "9": "9", "10": "15",
    "11": "id", "12": "'2'", "13": "512", "14": "14", "15": "[1, 2, 3]",
    "16": "[1, 2, 3]", "17": "[7, 5, 3]", "18": "4", "19": "True", "20": "[1, 13, 89, 100, 237]",
    "21": "2", "22": "aaabc", "23": "in", "24": "break", "25": "10",
    "26": "[1, 2, 3, 2]", "27": "(3, 3, 3)", "28": "{2, 3}", "29": "True", "30": "[111, 33, 2]",
    "31": "len", "32": "['abc', 'efg']", "33": "3", "34": "False", "35": "[1, 2, 1, 2]",
    "36": "False", "37": "3", "38": "True", "39": "A < B", "40": "def",
    "41": "6", "42": "[1, 2, 3]", "43": "6", "44": "True", "45": "[1, 3, 4]",
    "46": "[0, 0]", "47": "[5, 5, 5]", "48": "6", "49": "items", "50": "None"
}

def parse_mcq(content):
    questions = []
    blocks = re.split(r'第 \d+ 题', content)
    for block in blocks:
        if not block.strip(): continue
        ans_match = re.search(r'标准答案：\s*([A-D])', block)
        if not ans_match: continue
        ans = ans_match.group(1)
        q_body = block[:ans_match.start()].strip()
        opt_start = q_body.find('(A)')
        if opt_start == -1: continue
        q_text = q_body[:opt_start].strip()
        options_text = q_body[opt_start:]
        opts = []
        for tag in ['(A)', '(B)', '(C)', '(D)']:
            curr_idx = options_text.find(tag)
            if curr_idx == -1: break
            tag_letter = tag[1]
            if tag_letter == 'D': next_idx = len(options_text)
            else:
                next_char = chr(ord(tag_letter) + 1)
                next_idx = options_text.find(f"({next_char})")
                if next_idx == -1: next_idx = len(options_text)
            opts.append(options_text[curr_idx+3:next_idx].strip())
        if len(opts) == 4:
            questions.append({"question": q_text, "options": opts, "answer": ans, "type": "choice"})
    return questions

def parse_tf_fill(content):
    tf_q = []
    fill_q = []
    sections = re.split(r'### [一二三四]、', content)
    
    # 提取判断题
    tf_text = ""
    fill_text = ""
    if "判断题" in content:
        parts = content.split("### 一、判断题")
        if len(parts) > 1:
            rest = parts[1]
            if "### 二、填空题" in rest:
                tf_text, fill_text = rest.split("### 二、填空题")
            else: tf_text = rest
    
    # 解析判断
    for line in tf_text.strip().split('\n'):
        match = re.match(r'(\d+)\.\s*(.*)', line.strip())
        if match:
            qid, qtext = match.groups()
            ans = TF_ANSWERS.get(qid, "T") # 默认T，实际都已覆盖
            tf_q.append({"id": qid, "question": qtext, "answer": ans, "type": "true_false"})

    # 解析填空
    for line in fill_text.strip().split('\n'):
        match = re.match(r'(\d+)\.\s*(.*)', line.strip())
        if match:
            qid, qtext = match.groups()
            ans = FILL_ANSWERS.get(qid, "")
            fill_q.append({"id": qid, "question": qtext.replace("【1】", "____"), "answer": ans, "type": "fill_in"})
            
    return tf_q, fill_q

def main():
    final_data = {"choice": [], "fill_in": [], "true_false": []}
    
    # 1. 处理选择题
    if os.path.exists('选择.txt'):
        with open('选择.txt', 'r', encoding='utf-8') as f:
            mcqs = parse_mcq(f.read())
            # 分配试卷ID
            for i, q in enumerate(mcqs):
                q['id'] = f"M{i+1:03d}"
                q['paper_id'] = ['A', 'B', 'C', 'D'][i % 4]
                final_data['choice'].append(q)
    
    # 2. 处理填空与判断
    if os.path.exists('填空判断.txt'):
        with open('填空判断.txt', 'r', encoding='utf-8') as f:
            tfs, fills = parse_tf_fill(f.read())
            # 分配试卷ID
            for i, q in enumerate(tfs):
                q['paper_id'] = ['A', 'B', 'C', 'D'][i % 4]
                final_data['true_false'].append(q)
            for i, q in enumerate(fills):
                q['paper_id'] = ['A', 'B', 'C', 'D'][i % 4]
                final_data['fill_in'].append(q)

    with open('questions.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"✅ 生成成功: 选择题 {len(final_data['choice'])}, 判断题 {len(final_data['true_false'])}, 填空题 {len(final_data['fill_in'])}")

if __name__ == '__main__':
    main()