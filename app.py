#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 FOGUETE TURBO V7 - BOT TELEGRAM CORRIGIDO
Webhook para receber alertas do TradingView e enviar para Telegram
CORREÇÕES: Duplicação de sinais + Nome do ativo correto
"""

import os
import json
import requests
import re
from flask import Flask, request, jsonify
from datetime import datetime
import logging
import hashlib
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurações do bot (variáveis de ambiente do Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Cache para evitar duplicação de sinais (armazena hash das mensagens por 60 segundos)
message_cache = {}
CACHE_DURATION = 60  # segundos

# Verificar se as variáveis estão configuradas
if not BOT_TOKEN or not CHAT_ID:
    logger.error("❌ BOT_TOKEN ou CHAT_ID não configurados!")
    logger.error("Configure as variáveis de ambiente no Render")

def clean_cache():
    """Remove mensagens antigas do cache"""
    current_time = time.time()
    expired_keys = [key for key, timestamp in message_cache.items() 
                   if current_time - timestamp > CACHE_DURATION]
    for key in expired_keys:
        del message_cache[key]

def is_duplicate_message(message):
    """Verifica se a mensagem é duplicada usando hash"""
    clean_cache()
    
    # Criar hash da mensagem (ignorando timestamp para detectar duplicatas reais)
    message_without_time = re.sub(r'⏰ Horário: \*\d{2}:\d{2}:\d{2}\*', '', message)
    message_hash = hashlib.md5(message_without_time.encode()).hexdigest()
    
    current_time = time.time()
    
    if message_hash in message_cache:
        # Mensagem duplicada detectada
        logger.warning(f"🚫 Mensagem duplicada detectada: {message_hash}")
        return True
    
    # Adicionar ao cache
    message_cache[message_hash] = current_time
    return False

def extract_ticker_from_message(message):
    """Extrai o ticker do ativo da mensagem do TradingView"""
    try:
        # Padrões para extrair ticker
        patterns = [
            r'📈 Ativo: \*([A-Z0-9]+)\*',  # Formato: 📈 Ativo: *BTCUSDT*
            r'Ativo: \*([A-Z0-9]+)\*',     # Formato: Ativo: *BTCUSDT*
            r'📈 Ativo: ([A-Z0-9]+)',      # Formato: 📈 Ativo: BTCUSDT
            r'Ativo: ([A-Z0-9]+)',         # Formato: Ativo: BTCUSDT
            r'\| ([A-Z0-9]+)$',            # Formato: | BTCUSDT (final da linha)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                ticker = match.group(1)
                if ticker and ticker != "ATIVO" and len(ticker) >= 3:
                    return ticker
        
        # Se não encontrou, tentar extrair de contexto
        if "BTC" in message.upper():
            if "USDT" in message.upper():
                return "BTCUSDT"
            elif "USD" in message.upper():
                return "BTCUSD"
            else:
                return "BTC"
        elif "ETH" in message.upper():
            if "USDT" in message.upper():
                return "ETHUSDT"
            elif "USD" in message.upper():
                return "ETHUSD"
            else:
                return "ETH"
        
        return "CRYPTO"  # Fallback genérico
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair ticker: {str(e)}")
        return "CRYPTO"

def fix_ticker_in_message(message):
    """Corrige o ticker 'ATIVO' na mensagem"""
    try:
        # Se a mensagem contém "ATIVO", tentar extrair o ticker real
        if "ATIVO" in message:
            real_ticker = extract_ticker_from_message(message)
            
            # Substituir todas as ocorrências de "ATIVO" pelo ticker real
            message = message.replace("Ativo: ATIVO", f"Ativo: {real_ticker}")
            message = message.replace("📈 Ativo: *ATIVO*", f"📈 Ativo: *{real_ticker}*")
            message = message.replace("Ativo: *ATIVO*", f"Ativo: *{real_ticker}*")
            
            logger.info(f"✅ Ticker corrigido: ATIVO → {real_ticker}")
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir ticker: {str(e)}")
        return message

def send_telegram_message(message, parse_mode='Markdown'):
    """
    Envia mensagem para o Telegram com verificação de duplicação
    """
    try:
        # Verificar se é mensagem duplicada
        if is_duplicate_message(message):
            logger.info("🚫 Mensagem duplicada ignorada")
            return True  # Retorna True para não gerar erro, mas não envia
        
        # Corrigir ticker na mensagem
        message = fix_ticker_in_message(message)
        
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
    Formata alertas do TradingView para Telegram com melhorias visuais
    """
    try:
        # Se for string JSON, converter para dict
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except:
                # Se não for JSON válido, tratar como texto simples do TradingView
                return format_simple_alert(data)
        
        # Se for dict, extrair informações
        if isinstance(data, dict):
            # Verificar se tem campos específicos do TradingView
            ticker = data.get('ticker', extract_ticker_from_message(str(data)))
            action = data.get('action', 'SINAL')
            price = data.get('price', 'N/A')
            time = data.get('time', datetime.now().strftime("%H:%M:%S"))
            timeframe = data.get('timeframe', 'N/A')
            strength = data.get('strength', 'N/A')
            details = data.get('details', 'Sinal confirmado!')
            
            # Formatação melhorada para Telegram
            message = f"""🚀 *FOGUETE TURBO V7* 📈

💰 *{action.upper()}*
📈 Ativo: *{ticker}*
💲 Preço: *{price}*
⏰ Horário: *{time}*
📅 TF: *{timeframe}*
💪 Força: *{strength}*

🎯 *Detalhes:*
{details}

#FogueteTurbo #TradingView #Alertas"""
            
            return message
        
        # Se não conseguir processar, retornar como texto
        return format_simple_alert(str(data))
        
    except Exception as e:
        logger.error(f"❌ Erro ao formatar alerta: {str(e)}")
        return format_simple_alert(str(data))

def format_simple_alert(text):
    """
    Formata alertas simples de texto do TradingView
    """
    try:
        # Extrair ticker da mensagem
        ticker = extract_ticker_from_message(text)
        
        # Corrigir ticker na mensagem original
        text = fix_ticker_in_message(text)
        
        # Se a mensagem já está formatada (contém emojis), enviar como está
        if "🚀" in text and "*" in text:
            return text
        
        # Caso contrário, adicionar formatação básica
        current_time = datetime.now().strftime("%H:%M:%S")
        
        message = f"""🚀 *FOGUETE TURBO V7* 📈

📢 *ALERTA RECEBIDO:*

{text}

📈 *Ativo:* {ticker}
⏰ *Horário:* {current_time}
🤖 *Via:* TradingView Webhook

#FogueteTurbo #Alerta #TradingView"""
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Erro ao formatar alerta simples: {str(e)}")
        return f"🚀 FOGUETE TURBO V7\n\n{text}\n\n⏰ {datetime.now().strftime('%H:%M:%S')}"

@app.route('/', methods=['GET'])
def home():
    """
    Página inicial - verificar se o bot está funcionando
    """
    return jsonify({
        "status": "🚀 FOGUETE TURBO V7 - Bot Telegram Online! (VERSÃO CORRIGIDA)",
        "platform": "Render + GitHub",
        "bot_configured": bool(BOT_TOKEN and CHAT_ID),
        "timestamp": datetime.now().isoformat(),
        "fixes": [
            "✅ Duplicação de sinais corrigida",
            "✅ Nome do ativo corrigido",
            "✅ Cache de mensagens implementado"
        ],
        "endpoints": {
            "webhook": "/webhook",
            "test": "/test", 
            "status": "/status"
        }
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
        
        # Formatar mensagem
        if data:
            formatted_message = format_tradingview_alert(data)
            
            # Enviar para Telegram (com verificação de duplicação interna)
            success = send_telegram_message(formatted_message)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Alerta processado com sucesso!",
                    "timestamp": datetime.now().isoformat(),
                    "platform": "Render + GitHub (VERSÃO CORRIGIDA)",
                    "fixes_applied": [
                        "Verificação de duplicação",
                        "Correção do ticker do ativo"
                    ]
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
    Endpoint para testar o bot
    """
    try:
        test_message = """🚀 *FOGUETE TURBO V7* 📈

🧪 *TESTE DO BOT*
📈 Ativo: *BTCUSDT*
⏰ Horário: *""" + datetime.now().strftime("%H:%M:%S") + """*

✅ *Bot funcionando corretamente!*
🔧 *Versão:* Corrigida (sem duplicação)

#Teste #FogueteTurbo"""

        success = send_telegram_message(test_message)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Mensagem de teste enviada!",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "Erro ao enviar mensagem de teste"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """
    Status do bot e estatísticas
    """
    return jsonify({
        "bot_status": "online",
        "version": "FOGUETE TURBO V7 - CORRIGIDO",
        "bot_configured": bool(BOT_TOKEN and CHAT_ID),
        "cache_size": len(message_cache),
        "fixes": {
            "duplicate_prevention": "✅ Ativo",
            "ticker_correction": "✅ Ativo", 
            "message_cache": "✅ Ativo"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

