import math
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ===== CONFIGURAÇÃO =====
TOKEN = "8559248167:AAEfvbs-HYtP5d2XMDNQLgwbUqNN5Zolvdk"

# Rating base fixo por força atual (V22 Simple Pro)
RATING = {
    "ATL":0.98, "BOS":1.08, "BKN":0.95, "CHA":0.92, "CHI":0.96, "CLE":1.07,
    "DAL":1.02, "DEN":1.09, "DET":0.93, "GSW":0.99, "HOU":0.97, "IND":1.03,
    "LAC":1.04, "LAL":1.05, "MEM":0.94, "MIA":1.01, "MIL":1.08, "MIN":1.06,
    "NOP":1.00, "NYK":1.04, "OKC":1.10, "ORL":1.02, "PHI":1.06, "PHX":1.03,
    "POR":0.91, "SAC":1.02, "SAS":0.90, "TOR":0.95, "UTA":0.96, "WAS":0.89
}

def calcular(t1, t2, odd1, odd2, linha):
    r1 = RATING.get(t1, 1.0)
    r2 = RATING.get(t2, 1.0)

    # Cálculo de projeção de pontos
    score1 = 114 * r1 * (2 - r2)
    score2 = 114 * r2 * (2 - r1)
    total_proj = score1 + score2

    # Probabilidades (Modelo vs Mercado)
    p_model = score1 / (score1 + score2)
    p_market = (1 / odd1) / ((1 / odd1) + (1 / odd2))
    
    # 70% de peso para o mercado, 30% para o modelo matemático
    p_final = (p_market * 0.7) + (p_model * 0.3)

    # Cálculo de Over/Under usando distribuição normal
    z = (total_proj - linha) / 13
    over = round(0.5 * (1 + math.erf(z / math.sqrt(2))) * 100)
    under = 100 - over

    return p_final, total_proj, over, under, round(score1), round(score2)

async def mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Transforma tudo em maiúsculo para bater com o dicionário RATING
    entrada = update.message.text.upper().split("\n")

    try:
        # Linha 1: TIME1 VS TIME2
        jogo = entrada[0].split("VS")
        t1 = jogo[0].strip()
        t2 = jogo[1].strip()

        # Linha 2: ODD 1.50 2.60
        odds_str = entrada[1].replace("ODD", "").strip().split()
        odd1 = float(odds_str[0])
        odd2 = float(odds_str[1])

        # Linha 3: LINHA 228.5
        linha = float(entrada[2].replace("LINHA", "").strip())

        p, total_proj, ov, un, s1, s2 = calcular(t1, t2, odd1, odd2, linha)

        resp = (
            f"📊 NBA SHARP SIMPLE PRO\n"
            f"🏀 {t1} vs {t2}\n\n"
            f"🏆 Prob vitória:\n"
            f"{round(p*100)}% | {round((1-p)*100)}%\n\n"
            f"🎯 Total mercado: {linha}\n"
            f"📈 Total projetado: {total_proj:.1f}\n\n"
            f"🔥 Over {ov}% | Under {un}%\n\n"
            f"📉 Placar proj:\n"
            f"{s1} x {s2}"
        )

        await update.message.reply_text(resp)

    except Exception:
        await update.message.reply_text(
            "❌ Formato errado!\n\n"
            "Mande assim:\n"
            "LAL VS BOS\n"
            "ODD 1.90 1.90\n"
            "LINHA 225.5"
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), mensagem))
    print("🔥 BOT SIMPLE PRO ONLINE")
    app.run_polling()
