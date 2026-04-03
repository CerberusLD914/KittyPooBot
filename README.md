# 🐱💩 Kitty Poo Bot — Smart Automation

Automated bot for **KittyPoo Telegram WebApp** that optimizes income using a smart purchase strategy and real-time UI control.

---

## 🚀 Play the Game

👉 https://t.me/KittyPooBot?start=2B5FF9DA

---

## ⚙️ Features

- 🧠 Smart upgrade selection (ROI-based)
- 💩 Auto collect (moves Poo → Poo Total)
- 🛒 Market analysis only when needed (no spam scanning)
- 🔁 Dynamic countdown (real-time refresh timer)
- 🖥️ Clean console dashboard
- 🕵️ Stealth browser (undetected_chromedriver)

---

## 🚀 How It Works

### 1. Launch Game
- Reads `iframe_src` from `bot.json`
- Opens game using persistent Chrome profile
- Ensures session stays logged in

---

## 📊 Stats Used

- **Poo actual** → current box
- **Poo total** → used for purchases
- **Poo/h** → production rate
- **Coins** → account value

---

## 🧠 Smart Buying Logic

Chooses best upgrade based on:

- ROI (cost / production)
- Time to afford
- Efficiency (production / cost)

---

## ▶️ Usage

```bash
python main.py
```

---

## 💀 Disclaimer

For educational purposes only.
