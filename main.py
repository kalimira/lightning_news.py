
from flask import Flask, render_template_string, request, jsonify, session
import requests
import qrcode
import io
import base64
import os
import time
import hashlib
import os
import urllib.parse
import json


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET", "demo-lightning-network-implementation")
LNBITS_HOST = os.getenv("LNBITS_HOST", "https://demo.lnbits.com")
LNBITS_API_KEY = os.getenv("LNBITS_API_KEY", "f01f61a9421242e79f87c2337d8f7e64")
LOGIN_CHALLENGES = {}

HEADERS = {
    "X-Api-Key": LNBITS_API_KEY,
    "Content-type": "application/json"
}
#hi
ARTICLES = {
    1: {
        "title": "Bitcoin Lightning: бъдещето на интернет плащанията",
        "image": "images/ln.png",
        "preview": (
            "Lightning Network прави възможни мигновени микроплащания с почти нулеви такси. "
            "Това отваря вратата за напълно нов модел на интернет — без реклами, без абонаменти "
            "и без посредници."
        ),
        "full": (
            "Bitcoin Lightning Network е слой върху Bitcoin, създаден специално за бързи и "
            "евтини плащания. Вместо всяка транзакция да чака потвърждение в блокчейна, "
            "Lightning позволява директни плащания между потребители в реално време.\n\n"

            "Това прави възможни микроплащания от порядъка на няколко сатоши — нещо, което "
            "досега беше икономически невъзможно. Когато таксата е почти нула, можеш да "
            "плащаш за съдържание точно в момента, в който го консумираш.\n\n"

            "Вместо месечни абонаменти или натрапчиви реклами, плащаш 5 или 10 сатоши, "
            "само за конкретната статия, която четеш. Без регистрация, без карта, "
            "без да оставяш лични данни.\n\n"

            "Lightning не е просто технологично подобрение. То променя икономиката на уеба. "
            "Съдържанието отново може да се финансира директно от читателите, а не чрез "
            "вниманието им, продавано на рекламодатели."
        )
    },
    2: {
        "title": "Защо рекламният модел умира?",
        "image": "images/3.png",
        "preview": (
            "Рекламите финансират модерния интернет, но на цената на внимание, "
            "лични данни и качество. Този модел вече показва сериозни пукнатини."
        ),
        "full": (
            "Рекламният модел доминира интернет от десетилетия. Почти всичко е „безплатно“, "
            "но в действителност плащаме с внимание, лични данни и време.\n\n"

            "За да оцелеят, сайтовете са принудени да гонят кликове, сензации и максимално "
            "време на екрана. Това води до нискокачествено съдържание, clickbait заглавия "
            "и агресивно проследяване на потребителите.\n\n"

            "Резултатът е интернет, пълен с банери, попъпи, бисквитки и скрити тракери, "
            "които правят потребителското изживяване все по-лошо. Не е случайно, че "
            "ad-blocker-ите са масово използвани.\n\n"

            "Lightning предлага алтернатива. Вместо 10 реклами и 20 тракера, плащаш "
            "5 сатоши директно на автора. Без посредници. Без да бъдеш продуктът.\n\n"

            "Когато плащането е лесно, евтино и моментално, рекламният модел губи "
            "основното си предимство. И точно затова той бавно, но сигурно умира."
        )
    },
    3: {
        "title": "Биткойн: Твърди пари в свят на икономическа несигурност",
        "image": "images/bitcoin.png",
        "preview": (
            "Цял живот продаваме времето си за пари, но малцина разбират какво всъщност са те. "
            "Парите не са просто банкноти и цифри в банка — те са технология за пренасяне на стойност "
            "в пространството и времето. Работи ли днешната парична система в наша полза… или срещу нас?"
        ),
        "full": (
            "Исторически твърдите пари, като златото, предлагат устойчивост, защото са редки и "
            "трудно се добиват. Те не могат да бъдат създадени от нищото — необходима е енергия, "
            "време и труд, за да придобият стойност.\n\n"
            "Фиатните валути, които доминират днес (долар, евро, лев и други), нямат вътрешна стойност. "
            "Те са пари по нареждане — съществуват, защото правителствата заявяват, че имат стойност, "
            "а хората са принудени да им вярват. За разлика от златото, тяхното предлагане може да бъде "
            "увеличавано без ограничения от централните банки, което води до инфлация и сериозни "
            "икономически изкривявания.\n\n"
            "Оттам идва и проблемът с тях. Централните банки имат правото да създават нови пари чрез дълг."
            "Когато правителствата издават облигации, централната банка ги изкупува с новосъздадени пари, "
            "увеличавайки паричното предлагане. Това означава, че стойността на спестяванията ви намалява всеки "
            "път, когато се отпечатат нови пари.\n\n"
            "Представете си село с един пекар, който произвежда 100 хляба дневно на цена 1 лев. "
            "Ако внезапно в обращение се появят още 100 лева без повече хляб, цената логично се "
            "удвоява. Количеството пари расте, но реалното богатство не.\n\n"

            "Инфлацията е тихият крадец. Тя не отнема пари директно, а намалява покупателната им "
            "способност във времето. Хляб, мляко, транспорт, кафе, енергия — всичко поскъпва, "
            "защото валутата се обезценява.\n\n"

            "Липсата на стимул за спестяване принуждава хората да поемат риск, вместо да градят. "
            "Вместо да се фокусират върху професионалното си развитие, те са принудени да търсят "
            "начини да защитят спестяванията си.\n\n"

            "Технологичният напредък прави производството по-евтино и ефективно, но цените не падат. "
            "Причината не е липсата на напредък, а паричната система, която не допуска дефлация, "
            "за да защити дълговете.\n\n"

            "Биткойн има ограничено предлагане от 21 милиона единици — правило, заложено в кода и "
            "защитено от децентрализирана мрежа. Никой не може да го промени еднолично.\n\n"

            "Това го прави форма на твърди пари, устойчива на инфлация и цензура. С времето той се "
            "утвърждава като дигитално злато — средство за съхранение на стойност в цифровия свят.\n\n"

            "Твърдите пари насърчават дългосрочно мислене. Когато стойността не се размива, хората "
            "могат да планират, да спестяват и да градят бъдеще.\n\n"

            "Фиатните валути са в основата на много от днешните икономически проблеми. "
            "Биткойн предлага алтернатива — финансова суверенност, стабилност и справедливост "
            "в един все по-несигурен свят."
            )
        },
}


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
    background: #0f1115;
    color: #e5e7eb;
}

.header {
    background: #14171c;
    padding: 24px 40px;
    border-bottom: 1px solid #23262d;
    display: flex;
    align-items: center;
    gap: 18px;
}

.logo {
    font-size: 72px;
}

.title-text {
    font-size: 38px;
    font-weight: 700;
    color: #f7931a;
}

.subtitle {
    font-size: 22px;
    color: #9ca3af;
    margin-top: -4px;
}

.container {
    max-width: 900px;
    margin: 50px auto;
    padding: 20px;
}

.article {
    background: #14171c;
    padding: 28px;
    margin-bottom: 40px;
    border-radius: 16px;
    border: 1px solid #23262d;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

.article-image {
    width: 100%;
    height: auto;
    border-radius: 14px;
    margin-bottom: 18px;
}

h2 {
    font-size: 24px;
    margin-bottom: 12px;
    font-weight: 700;
    color: #f9fafb;
}

p {
    font-size: 16px;
    line-height: 1.6;
    color: #d1d5db;
}

button {
    padding: 14px 22px;
    background: linear-gradient(135deg, #f7931a, #ffb347);
    color: #111;
    border: none;
    font-weight: 700;
    border-radius: 10px;
    margin-top: 14px;
    cursor: pointer;
    font-size: 15px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(247,147,26,0.35);
}

.qr-box {
    margin-top: 18px;
    padding: 20px;
    background: #0f1115;
    border: 1px dashed #2a2e37;
    border-radius: 14px;
    text-align: center;
    color: #9ca3af;
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
            <img src="{{ url_for('static', filename=art.image) }}" class="article-image">
                <h2>{{ art.title }}</h2>
                <p>{{ art.preview }}</p>

                <div id="full{{id}}"></div>

                <button id="btn{{id}}" onclick="unlock({{id}})">🔓 Отключи пълния текст (5 sats)</button>
            </div>
        {% endfor %}
    </div>

    <script>
    function unlock(id) {
        const btn = document.getElementById("btn" + id);
        const full = document.getElementById("full" + id);

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
    function loginLN() {
    fetch("/login")
        .then(r => r.json())
        .then(data => {
            alert("Scan QR with your Lightning wallet");

            document.body.innerHTML += `
                <div class="qr-box">
                    <img src="data:image/png;base64,${data.qr}" width="220">
                </div>
            `;

            pollLogin();
        });
}

function pollLogin() {
    setInterval(() => {
        fetch("/me")
            .then(r => r.json())
            .then(u => {
                if (u.logged_in) {
                    location.reload();
                }
            });
    }, 1500);
}
</script>

</body>
</html>
"""

    return render_template_string(html, articles=ARTICLES)


@app.route("/create_invoice/<int:article_id>")
def create_invoice(article_id):
    payload = { "out": False, "amount": 5, "memo": f"Unlock article {article_id}", "expiry": 86400 }
    r = requests.post(f"{LNBITS_HOST}/api/v1/payments", json=payload, headers=HEADERS).json()
    qr = make_qr_image(r["payment_request"])
    
    return jsonify({
        "pr": r["payment_request"],
        "payment_hash": r["payment_hash"],
        "qr": qr
    })


@app.route("/check_payment/<payment_hash>")
def check_payment(payment_hash):
    r = requests.get(f"{LNBITS_HOST}/api/v1/payments/{payment_hash}", headers=HEADERS).json()
    return jsonify({"paid": r.get("paid", False)})


@app.route("/full_article/<int:article_id>")
def full_article(article_id):
    return jsonify({"full": ARTICLES[article_id]["full"]})


if __name__ == "__main__":
    app.run(debug=True)

