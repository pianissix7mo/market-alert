#!/usr/bin/env python3
import os
import smtplib
import yfinance as yf
import fear_and_greed
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# ─── CONFIGURATION ────────────────────────────────────────────────
RECIPIENT_EMAIL     = "mofeiwang@hotmail.com"
SENDER_EMAIL        = os.environ.get("ALERT_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("ALERT_APP_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT   = 587

# Thresholds
VIX_LOW  = 18
VIX_HIGH = 30
FG_LOW   = 30
FG_HIGH  = 70
QQQ_HIGH = 700
# ──────────────────────────────────────────────────────────────────


def get_vix():
    vix = yf.Ticker("^VIX")
    data = vix.history(period="1d")
    if data.empty:
        raise ValueError("Could not fetch VIX data.")
    return round(data["Close"].iloc[-1], 2)


def get_fear_and_greed():
    fg = fear_and_greed.get()
    return round(fg.value, 2), fg.description


def get_qqq_price():
    qqq = yf.Ticker("QQQ")
    data = qqq.history(period="1d")
    if data.empty:
        raise ValueError("Could not fetch QQQ data.")
    return round(data["Close"].iloc[-1], 2)


def check_conditions(vix_value, fg_value, qqq_price):
    alerts = []
    if vix_value < VIX_LOW:
        alerts.append(f"🟢 VIX is BELOW {VIX_LOW}: currently {vix_value}")
    if vix_value > VIX_HIGH:
        alerts.append(f"🔴 VIX is ABOVE {VIX_HIGH}: currently {vix_value}")
    if fg_value < FG_LOW:
        alerts.append(f"🔴 CNN Fear & Greed Index is BELOW {FG_LOW} (Extreme Fear): currently {fg_value}")
    if fg_value > FG_HIGH:
        alerts.append(f"🟢 CNN Fear & Greed Index is ABOVE {FG_HIGH} (Extreme Greed): currently {fg_value}")
    if qqq_price > QQQ_HIGH:
        alerts.append(f"🚀 QQQ is ABOVE ${QQQ_HIGH}: currently ${qqq_price}")
    return alerts


def send_email(alerts, vix_value, fg_value, fg_desc, qqq_price):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subject = f"⚠️ Market Alert Triggered — {now}"

    body = f"""
    <html>
    <body>
    <h2>⚠️ Market Alert — {now}</h2>
    <h3>Triggered Conditions:</h3>
    <ul>
        {"".join(f"<li><b>{a}</b></li>" for a in alerts)}
    </ul>
    <hr>
    <h3>Current Market Snapshot:</h3>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr><td><b>CBOE VIX</b></td><td>{vix_value}</td></tr>
        <tr><td><b>CNN Fear & Greed</b></td><td>{fg_value} ({fg_desc})</td></tr>
        <tr><td><b>QQQ Price</b></td><td>${qqq_price}</td></tr>
    </table>
    <br>
    <p><i>This is an automated alert from your Market Alert Script.</i></p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(body, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())

    print(f"✅ Alert email sent to {RECIPIENT_EMAIL}")


def main():
    print("=" * 50)
    print("  Market Alert Monitor")
    print("=" * 50)

    print("\n📡 Fetching VIX...")
    vix_value = get_vix()
    print(f"   VIX = {vix_value}")

    print("📡 Fetching CNN Fear & Greed Index...")
    fg_value, fg_desc = get_fear_and_greed()
    print(f"   Fear & Greed = {fg_value} ({fg_desc})")

    print("📡 Fetching QQQ price...")
    qqq_price = get_qqq_price()
    print(f"   QQQ = ${qqq_price}")

    alerts = check_conditions(vix_value, fg_value, qqq_price)

    if alerts:
        print(f"\n🚨 {len(alerts)} alert(s) triggered!")
        for a in alerts:
            print(f"   → {a}")
        send_email(alerts, vix_value, fg_value, fg_desc, qqq_price)
    else:
        print("\n✅ All values within normal range. No alert sent.")
        print(f"   VIX: {VIX_LOW} ≤ {vix_value} ≤ {VIX_HIGH}")
        print(f"   F&G: {FG_LOW} ≤ {fg_value} ≤ {FG_HIGH}")
        print(f"   QQQ: {qqq_price} ≤ {QQQ_HIGH}")


if __name__ == "__main__":
    main()
