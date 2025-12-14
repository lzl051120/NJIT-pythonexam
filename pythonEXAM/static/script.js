document.addEventListener("DOMContentLoaded", function() {
    // 只有在考试页面才启动计时器
    if (document.getElementById('exam-form')) {
        startTimer(60 * 60); // 60分钟倒计时
    }
});

function startTimer(duration) {
    let timer = duration, minutes, seconds;
    const display = document.getElementById('time-display');
    
    const interval = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        display.textContent = minutes + ":" + seconds;

        if (--timer < 0) {
            clearInterval(interval);
            alert("考试时间到！系统将自动交卷。");
            submitExam();
        }
    }, 1000);
}

function submitExam() {
    const paperId = document.getElementById('paper-id-hidden').value;
    const form = document.getElementById('exam-form');
    const formData = new FormData(form);
    const answers = {};

    // 收集所有答案
    for (let [key, value] of formData.entries()) {
        answers[key] = value;
    }

    // 发送给后端
    fetch('/api/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            paper_id: paperId,
            answers: answers
        })
    })
    .then(response => response.json())
    .then(data => {
        showResults(data);
    })
    .catch(error => console.error('Error:', error));
}

function showResults(data) {
    const container = document.querySelector('.container');
    
    let html = `<h1>考试结果</h1>
                <h2>得分: ${data.total_score} / ${data.max_score}</h2>
                <hr>`;
    
    data.details.forEach(item => {
        const statusClass = item.is_correct ? 'correct' : 'wrong';
        const statusIcon = item.is_correct ? '✅' : '❌';
        
        html += `
        <div class="result-card ${statusClass}">
            <p><strong>题目:</strong> ${item.question}</p>
            <p>${statusIcon} <strong>你的答案:</strong> ${item.user_answer || '(未填)'}</p>
            ${!item.is_correct ? `<p><strong>正确答案:</strong> ${item.correct_answer}</p>` : ''}
        </div>`;
    });

    html += `<a href="/" class="paper-btn" style="display:block; text-align:center; margin-top:20px;">返回首页</a>`;
    
    container.innerHTML = html;
    window.scrollTo(0, 0);
}