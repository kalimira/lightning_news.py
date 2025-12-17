
from flask import Flask, render_template_string, request, jsonify
import requests
import qrcode
import io
import base64
import os
import time

app = Flask(__name__)

# -----------------------------
# CONFIG — сложи твоите данни
# -----------------------------
LNBITS_HOST = os.getenv("LNBITS_HOST", "https://demo.lnbits.com")
LNBITS_API_KEY = os.getenv("LNBITS_API_KEY", "f01f61a9421242e79f87c2337d8f7e64")

HEADERS = {
    "X-Api-Key": LNBITS_API_KEY,
    "Content-type": "application/json"
}

ARTICLES = {
    1: {
        "title": "Bitcoin Lightning: бъдещето на интернет плащанията",
        "preview": "Lightning Network позволява микроплащания в реално време...",
        "full": "Lightning Network позволява микроплащания в реално време, "
                "почти без такси, с висока скорост и директно между потребителите. "
                "Това напълно променя модела на монетизация в интернет — "
                "вместо реклами, тракване и абонаменти, можеш да плащаш само когато четеш."
    },
    2: {
        "title": "Защо рекламният модел умира",
        "preview": "Интернет рекламите финансират всичко, но на висока цена...",
        "full": "Интернет рекламите финансират почти целия съвременен уеб, "
                "но цената е огромна: непрекъснато проследяване, нискокачествено съдържание "
                "и изкривяване на вниманието. Lightning позволява директна монетизация — "
                "5 сатоши вместо 10 банера и 20 тракера."
    }
}

# Генериране на QR от invoice
def make_qr_image(data):
    qr = qrcode.QRCode(version=1, box_size=8, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@app.route("/")
def index():
    html = """
    <html>
<head>
    <title>Lightning News Demo</title>

    <!-- Google Font -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;500;700&display=swap" rel="stylesheet">

    <style>
        body {
            font-family: "Inter", sans-serif;
            margin: 0;
            padding: 0;
            background: #f7f7f7;
            color: #222;
        }

        .header {
            background: white;
            padding: 20px 40px;
            border-bottom: 2px solid #eee;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo {
            font-size: 40px;
        }

        .title-text {
            font-size: 26px;
            font-weight: 700;
        }

        .subtitle {
            font-size: 16px;
            color: #666;
            margin-top: -4px;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }

        .article {
            background: white;
            padding: 25px;
            margin-bottom: 35px;
            border-radius: 12px;
            border: 1px solid #e5e5e5;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        h2 {
            font-size: 23px;
            margin-bottom: 10px;
            font-weight: 700;
        }

        p {
            font-size: 16px;
            line-height: 1.55;
            color: #444;
        }

        button {
            padding: 12px 18px;
            background: #f2a900;
            color: black;
            border: none;
            font-weight: 600;
            border-radius: 8px;
            margin-top: 10px;
            cursor: pointer;
            font-size: 15px;
        }

        button:hover {
            background: #ffbe32;
        }

        .qr-box {
            margin-top: 10px;
            padding: 15px;
            background: #fafafa;
            border: 1px dashed #ccc;
            border-radius: 10px;
            text-align: center;
        }
    </style>
</head>

<body>

    <div class="header">
        <div class="logo">⚡</div>
        <div>
            <div class="title-text">BitReads</div>
            <div class="subtitle">Чети без акаунт — пълният текст се отключва с LN ⚡</div>
        </div>
    </div>

    <div class="container">
        {% for id, art in articles.items() %}
            <div class="article">
                <h2>{{ art.title }}</h2>
                <p>{{ art.preview }}</p>

                <div id="full{{id}}"></div>

                <button id="btn{{id}}" onclick="unlock({{id}})">🔓 Отключи пълния текст (10 sats)</button>
            </div>
        {% endfor %}
    </div>

    <script>
    function unlock(id) {
        const btn = document.getElementById("btn" + id);
        const full = document.getElementById("full" + id);

        // Скриваме бутона
        btn.style.display = "none";

        fetch("/create_invoice/" + id)
            .then(r => r.json())
            .then(data => {
                full.innerHTML = `
                    <div class="qr-box">
                        <p><b>Сканирай QR за плащане:</b></p>
                        <img src="data:image/png;base64,${data.qr}" width="200"><br>
                        <p><i>Изчаква се плащане...</i></p>
                        <button onclick="cancelPayment(${id})" 
                                style="background:#ddd;margin-top:10px;">
                            ❌ Откажи плащането
                        </button>
                    </div>
                `;

                // POLLING
                let interval = setInterval(() => {
                    fetch("/check_payment/" + data.payment_hash)
                        .then(r => r.json())
                        .then(st => {
                            if (st.paid) {
                                clearInterval(interval);

                                fetch("/full_article/" + id)
                                    .then(r=>r.json())
                                    .then(info => {
                                        full.innerHTML = "<p>"+info.full+"</p>";
                                    });
                            }
                        });
                }, 1500);

                // Запазваме interval, за да го спрем при Cancel
                full.dataset.interval = interval;
            });
    }

    function cancelPayment(id) {
        const full = document.getElementById("full" + id);
        const btn = document.getElementById("btn" + id);

        // Спираме polling-a
        const interval = full.dataset.interval;
        if (interval) clearInterval(interval);

        // Почистваме QR кутията
        full.innerHTML = "";

        // Връщаме бутона
        btn.style.display = "inline-block";
    }
</script>

</body>
</html>
"""

    return render_template_string(html, articles=ARTICLES)


# API: Създаване на invoice
@app.route("/create_invoice/<int:article_id>")
def create_invoice(article_id):
    payload = { "out": False, "amount": 10, "memo": f"Unlock article {article_id}", "expiry": 86400 }
    r = requests.post(f"{LNBITS_HOST}/api/v1/payments", json=payload, headers=HEADERS).json()
    qr = make_qr_image(r["payment_request"])
    
    return jsonify({
        "pr": r["payment_request"],
        "payment_hash": r["payment_hash"],
        "qr": qr
    })


# API: Проверка на плащане
@app.route("/check_payment/<payment_hash>")
def check_payment(payment_hash):
    r = requests.get(f"{LNBITS_HOST}/api/v1/payments/{payment_hash}", headers=HEADERS).json()
    return jsonify({"paid": r.get("paid", False)})


# API: Връщане на пълния текст
@app.route("/full_article/<int:article_id>")
def full_article(article_id):
    return jsonify({"full": ARTICLES[article_id]["full"]})



if __name__ == "__main__":
    app.run(debug=True)

