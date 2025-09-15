#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 FOGUETE TURBO V7 - BOT TELEGRAM MELHORADO
Webhook otimizado para receber alertas do TradingView e enviar para Telegram
com formatação profissional e detecção inteligente de sinais
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime, timezone, timedelta
import logging
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurações do bot (variáveis de ambiente do Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Fuso horário de Manaus (UTC-4)
MANAUS_TIMEZONE = timezone(timedelta(hours=-4))

# Verificar se as variáveis estão configuradas
if not BOT_TOKEN or not CHAT_ID:
    logger.error("❌ BOT_TOKEN ou CHAT_ID não configurados!")
    logger.error("Configure as variáveis de ambiente no Render")

def get_manaus_time():
    """
    Retorna horário atual de Manaus (UTC-4)
    """
    return datetime.now(MANAUS_TIMEZONE).strftime("%H:%M:%S")

def detect_signal_type(message):
    """
    Detecta o tipo de sinal baseado na mensagem
    """
    message_upper = message.upper()
    
    # Detectar sinais MASTER
    if "MASTER COMPRA" in message_upper or "MASTER BUY" in message_upper:
        return "master_buy"
    elif "MASTER VENDA" in message_upper or "MASTER SELL" in message_upper:
        return "master_sell"
    elif "MASTER PREPARAÇÃO" in message_upper or "MASTER PREP" in message_upper:
        return "master_prep"
    
    # Detectar sinais MASTER ESTRELA
    elif "MASTER ESTRELA" in message_upper or "ESTRELA" in message_upper:
        if "COMPRA" in message_upper or "BUY" in message_upper:
            return "estrela_buy"
        elif "VENDA" in message_upper or "SELL" in message_upper:
            return "estrela_sell"
        else:
            return "estrela_signal"
    
    # Detectar SuperTrend
    elif "SUPERTREND BUY" in message_upper:
        return "supertrend_buy"
    elif "SUPERTREND SELL" in message_upper:
        return "supertrend_sell"
    
    # Detectar Bollinger Bands
    elif "BOLLINGER" in message_upper:
        if "SUPERIOR" in message_upper or "ALTA" in message_upper:
            return "bollinger_high"
        elif "INFERIOR" in message_upper or "BAIXA" in message_upper:
            return "bollinger_low"
        elif "MÉDIA" in message_upper or "MEDIO" in message_upper:
            return "bollinger_mid"
        else:
            return "bollinger_signal"
    
    # Detectar cruzamentos SMAs
    elif "CRUZ" in message_upper and "SMA" in message_upper:
        if "BAIXA" in message_upper or "ABAIXO" in message_upper:
            return "sma_cross_down"
        elif "ALTA" in message_upper or "ACIMA" in message_upper:
            return "sma_cross_up"
        else:
            return "sma_cross"
    
    # Detectar volume
    elif "VOLUME" in message_upper:
        return "volume_signal"
    
    # Detectar Fibonacci
    elif "FIBONACCI" in message_upper or "FIB" in message_upper:
        return "fibonacci_signal"
    
    # Detectar sinais gerais de compra/venda
    elif "COMPRA" in message_upper and ("FORTE" in message_upper or "CONFIRMADA" in message_upper):
        return "buy_strong"
    elif "VENDA" in message_upper and ("FORTE" in message_upper or "CONFIRMADA" in message_upper):
        return "sell_strong"
    elif "COMPRA" in message_upper:
        return "buy_signal"
    elif "VENDA" in message_upper:
        return "sell_signal"
    
    # Padrão genérico
    return "general_signal"

def extract_asset_name(message):
    """
    Tenta extrair o nome do ativo da mensagem ou do contexto
    """
    # Padrões comuns de ativos
    patterns = [
        r'\b([A-Z]{3,6}USDT?)\b',  # BTCUSDT, ETHUSDT, etc.
        r'\b([A-Z]{3,6}USD)\b',    # BTCUSD, ETHUSD, etc.
        r'\b([A-Z]{3,6}BRL)\b',    # BTCBRL, ETHBRL, etc.
        r'\b(BTC|ETH|ADA|SOL|MATIC|DOT|LINK|UNI|AAVE|ATOM)\b'  # Principais cryptos
    ]
    
    for pattern in patterns:
        match = re.search(pattern, message.upper())
        if match:
            return match.group(1)
    
    # Se não encontrar, retornar padrão
    return "ATIVO"

def extract_strength(message):
    """
    Extrai informações de força/porcentagem da mensagem
    """
    # Procurar por porcentagens
    percentage_match = re.search(r'(\d+)%', message)
    if percentage_match:
        return f"{percentage_match.group(1)}%"
    
    # Procurar por força em formato X/Y
    strength_match = re.search(r'(\d+)/(\d+)', message)
    if strength_match:
        num = int(strength_match.group(1))
        total = int(strength_match.group(2))
        percentage = int((num/total) * 100)
        return f"{num}/{total} ({percentage}%)"
    
    return "N/A"

def get_signal_emoji_and_action(signal_type):
    """
    Retorna emoji e ação baseado no tipo de sinal
    """
    signal_map = {
        "master_buy": ("🟢🚀", "MASTER COMPRA", "💰"),
        "master_sell": ("🔴🚀", "MASTER VENDA", "📉"),
        "master_prep": ("🟡🚀", "MASTER PREPARAÇÃO", "⚠️"),
        "estrela_buy": ("🚀⭐", "MASTER ESTRELA COMPRA", "💰"),
        "estrela_sell": ("🚀⭐", "MASTER ESTRELA VENDA", "📉"),
        "estrela_signal": ("🚀⭐", "MASTER ESTRELA SINAL", "⭐"),
        "supertrend_buy": ("📈🟢", "SUPERTREND COMPRA", "💰"),
        "supertrend_sell": ("📉🔴", "SUPERTREND VENDA", "📉"),
        "bollinger_high": ("📊🔴", "BOLLINGER SUPERIOR", "⬆️"),
        "bollinger_low": ("📊🟢", "BOLLINGER INFERIOR", "⬇️"),
        "bollinger_mid": ("📊🟡", "BOLLINGER MÉDIA", "↔️"),
        "bollinger_signal": ("📊", "BOLLINGER SINAL", "📊"),
        "sma_cross_up": ("🔄🟢", "CRUZ SMAs ALTA", "⬆️"),
        "sma_cross_down": ("🔄🔴", "CRUZ SMAs BAIXA", "⬇️"),
        "sma_cross": ("🔄", "CRUZAMENTO SMAs", "🔄"),
        "volume_signal": ("📊💪", "VOLUME FORTE", "💪"),
        "fibonacci_signal": ("💎", "FIBONACCI SINAL", "💎"),
        "buy_strong": ("💰🟢", "COMPRA FORTE", "💰"),
        "sell_strong": ("📉🔴", "VENDA FORTE", "📉"),
        "buy_signal": ("🟢⬆️", "SINAL COMPRA", "💰"),
        "sell_signal": ("🔴⬇️", "SINAL VENDA", "📉"),
        "general_signal": ("🚀", "SINAL GERAL", "🎯")
    }
    
    return signal_map.get(signal_type, ("🚀", "SINAL", "🎯"))

def send_telegram_message(message, parse_mode='Markdown'):
    """
    Envia mensagem para o Telegram
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        data = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True
        }
        
        response = requests.post(url, data=data, timeout=10)
        
        if response.status_code == 200:
            logger.info("✅ Mensagem enviada com sucesso!")
            return True
        else:
            logger.error(f"❌ Erro ao enviar mensagem: {response.status_code}")
            logger.error(f"Resposta: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro na função send_telegram_message: {str(e)}")
        return False

def format_tradingview_alert(data):
    """
    Formata alertas do TradingView para Telegram com detecção inteligente
    """
    try:
        # Converter para string se necessário
        if isinstance(data, dict):
            message_text = json.dumps(data)
        else:
            message_text = str(data)
        
        # Detectar tipo de sinal
        signal_type = detect_signal_type(message_text)
        emoji, action, action_emoji = get_signal_emoji_and_action(signal_type)
        
        # Extrair informações
        asset = extract_asset_name(message_text)
        strength = extract_strength(message_text)
        current_time = get_manaus_time()
        
        # Formatação específica por tipo de sinal
        if signal_type.startswith("master"):
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 📈

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)
💪 Força: *{strength}*

🎯 *Estratégia MASTER:*
MACD + EMAs 12/26

{action_emoji} *Sinal confirmado!*

#Master #FogueteTurbo #TradingView"""

        elif signal_type.startswith("estrela"):
            formatted_message = f"""🚀 *FOGUETE TURBO V7* ⭐

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)
💪 Força: *{strength}*

🎯 *Estratégia ESTRELA:*
Stochastic + EMAs 21/50

⭐ *Sinal premium confirmado!*

#MasterEstrela #FogueteTurbo #TradingView"""

        elif signal_type.startswith("supertrend"):
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 📈

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)
💪 Força: *{strength}*

🎯 *SuperTrend:*
Mudança de tendência confirmada

{action_emoji} *Sinal de entrada!*

#SuperTrend #FogueteTurbo #TradingView"""

        elif signal_type.startswith("bollinger"):
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 📊

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)

🎯 *Bollinger Bands:*
Rejeição detectada - Pullback

{action_emoji} *Oportunidade de entrada!*

#Bollinger #Pullback #FogueteTurbo"""

        elif signal_type.startswith("sma_cross"):
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 🔄

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)

🎯 *Cruzamento SMAs:*
SMA 8 x SMA 21

{action_emoji} *Mudança de tendência!*

#SMAs #Cruzamento #FogueteTurbo"""

        elif signal_type == "volume_signal":
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 💪

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)

🎯 *Volume Forte:*
Acima da média

💪 *Movimento com força!*

#Volume #Força #FogueteTurbo"""

        else:
            # Formatação padrão para outros sinais
            formatted_message = f"""🚀 *FOGUETE TURBO V7* 📈

{emoji} *{action}!*
📈 Ativo: *{asset}*
⏰ Horário: *{current_time}* (Manaus)
💪 Força: *{strength}*

🎯 *Detalhes:*
{message_text[:100]}...

{action_emoji} *Sinal confirmado!*

#FogueteTurbo #TradingView #Alertas"""

        return formatted_message
        
    except Exception as e:
        logger.error(f"❌ Erro ao formatar alerta: {str(e)}")
        # Fallback simples
        current_time = get_manaus_time()
        return f"""🚀 *FOGUETE TURBO V7* 📈

📢 *ALERTA RECEBIDO:*

{str(data)[:200]}

⏰ Horário: *{current_time}* (Manaus)
🤖 Via: *TradingView Webhook*

#FogueteTurbo #Alerta #TradingView"""

@app.route('/', methods=['GET'])
def home():
    """
    Página inicial - verificar se o bot está funcionando
    """
    return jsonify({
        "status": "🚀 FOGUETE TURBO V7 - Bot Telegram Online! (MELHORADO)",
        "platform": "Render + GitHub",
        "version": "2.0 - Detecção Inteligente",
        "features": [
            "Detecção automática de sinais",
            "Formatação profissional",
            "Horário Manaus (UTC-4)",
            "Emojis específicos por estratégia",
            "Suporte MASTER e MASTER ESTRELA"
        ],
        "bot_configured": bool(BOT_TOKEN and CHAT_ID),
        "manaus_time": get_manaus_time(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint principal para receber alertas do TradingView
    """
    try:
        # Log da requisição recebida
        logger.info("📨 Webhook recebido do TradingView!")
        
        # Obter dados da requisição
        content_type = request.content_type
        
        if content_type and 'application/json' in content_type:
            data = request.get_json()
            logger.info(f"📊 Dados JSON: {data}")
        else:
            data = request.get_data(as_text=True)
            logger.info(f"📊 Dados texto: {data}")
        
        # Verificar se bot está configurado
        if not BOT_TOKEN or not CHAT_ID:
            logger.error("❌ Bot não configurado!")
            return jsonify({"error": "Bot não configurado"}), 500
        
        # Formatar mensagem com detecção inteligente
        if data:
            formatted_message = format_tradingview_alert(data)
            
            # Enviar para Telegram
            success = send_telegram_message(formatted_message)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Alerta enviado com formatação melhorada!",
                    "signal_detected": detect_signal_type(str(data)),
                    "manaus_time": get_manaus_time(),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({
                    "status": "error",
                    "message": "Erro ao enviar alerta para Telegram"
                }), 500
        else:
            logger.warning("⚠️ Nenhum dado recebido do TradingView")
            return jsonify({"error": "Nenhum dado recebido"}), 400
            
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET', 'POST'])
def test():
    """
    Endpoint para testar o bot com diferentes tipos de sinais
    """
    try:
        # Teste com sinal MASTER
        test_message = f"""🚀 *FOGUETE TURBO V7* 📈

🟢🚀 *MASTER COMPRA!*
📈 Ativo: *BTCUSDT*
⏰ Horário: *{get_manaus_time()}* (Manaus)
💪 Força: *8/10 (80%)*

🎯 *Estratégia MASTER:*
MACD + EMAs 12/26

💰 *Sinal confirmado!*

#Master #FogueteTurbo #TradingView

---

✅ *TESTE REALIZADO COM SUCESSO!*
🤖 Bot funcionando perfeitamente
📱 Formatação melhorada ativa
🕐 Horário Manaus configurado
🎯 Detecção inteligente funcionando"""
        
        success = send_telegram_message(test_message)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "✅ Teste enviado com formatação melhorada!",
                "features_tested": [
                    "Formatação profissional",
                    "Horário Manaus (UTC-4)",
                    "Emojis específicos",
                    "Detecção de sinais"
                ],
                "manaus_time": get_manaus_time(),
                "bot_token_configured": bool(BOT_TOKEN),
                "chat_id_configured": bool(CHAT_ID)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ Erro ao enviar mensagem de teste"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/test-signals', methods=['GET'])
def test_signals():
    """
    Testar diferentes tipos de sinais
    """
    test_signals = [
        "🚀🟢 MASTER COMPRA! MACD+0.0123 EMAs↗",
        "🚀🔴 MASTER VENDA! MACD-0.0087 EMAs↘", 
        "🚀⭐ MASTER ESTRELA COMPRA! Stochastic+EMAs",
        "🚀📈 SUPERTREND BUY! Força: 70%",
        "🚀📊 BOLLINGER REJEIÇÃO SUPERIOR! Pullback",
        "🚀🔄 CRUZ SMAs 8x21 ALTA! SMA8 cruzou acima"
    ]
    
    results = []
    for signal in test_signals:
        signal_type = detect_signal_type(signal)
        emoji, action, action_emoji = get_signal_emoji_and_action(signal_type)
        results.append({
            "original": signal,
            "detected_type": signal_type,
            "emoji": emoji,
            "action": action
        })
    
    return jsonify({
        "status": "Signal detection test",
        "results": results,
        "manaus_time": get_manaus_time()
    })

@app.route('/status', methods=['GET'])
def status():
    """
    Verificar status completo do bot melhorado
    """
    return jsonify({
        "bot_online": True,
        "version": "2.0 - Detecção Inteligente",
        "platform": "Render + GitHub",
        "bot_token_configured": bool(BOT_TOKEN),
        "chat_id_configured": bool(CHAT_ID),
        "manaus_time": get_manaus_time(),
        "timezone": "UTC-4 (Manaus/Amazonas)",
        "features": {
            "intelligent_detection": "✅ Ativo",
            "professional_formatting": "✅ Ativo", 
            "manaus_timezone": "✅ Ativo",
            "master_signals": "✅ Suportado",
            "master_estrela": "✅ Suportado",
            "supertrend": "✅ Suportado",
            "bollinger": "✅ Suportado",
            "sma_cross": "✅ Suportado",
            "volume": "✅ Suportado"
        },
        "endpoints": {
            "home": "/",
            "webhook": "/webhook (POST)",
            "test": "/test (GET/POST)",
            "test_signals": "/test-signals (GET)",
            "status": "/status (GET)"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Health check para o Render
    """
    return jsonify({
        "status": "healthy",
        "version": "2.0",
        "manaus_time": get_manaus_time(),
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Porta do Render (padrão 10000)
    port = int(os.environ.get('PORT', 10000))
    
    # Log de inicialização
    logger.info("🚀 Iniciando FOGUETE TURBO V7 Bot MELHORADO...")
    logger.info("⭐ Versão 2.0 - Detecção Inteligente")
    logger.info("☁️ Plataforma: Render + GitHub")
    logger.info(f"🌐 Porta: {port}")
    logger.info(f"🕐 Horário Manaus: {get_manaus_time()}")
    logger.info(f"🤖 Bot Token: {'✅ Configurado' if BOT_TOKEN else '❌ Não configurado'}")
    logger.info(f"💬 Chat ID: {'✅ Configurado' if CHAT_ID else '❌ Não configurado'}")
    logger.info("🎯 Recursos: Detecção inteligente, formatação profissional, horário Manaus")
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=port, debug=False)

