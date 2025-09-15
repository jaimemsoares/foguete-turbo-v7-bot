#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 FOGUETE TURBO V7 - BOT TELEGRAM (RENDER + GITHUB)
Webhook para receber alertas do TradingView e enviar para Telegram
Deploy: GitHub → Render (100% Gratuito)
"""

import os
import json
import requests
from flask import Flask, request, jsonify
from datetime import datetime
import logging
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Define o fuso horário de Manaus
manaus_tz = pytz.timezone('America/Manaus')

# Obtém a hora atual no fuso horário de Manaus
hora_manaus = datetime.now(manaus_tz)

# Configurações do bot (variáveis de ambiente do Render)
BOT_TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Verificar se as variáveis estão configuradas
if not BOT_TOKEN or not CHAT_ID:
    logger.error("❌ BOT_TOKEN ou CHAT_ID não configurados!")
    logger.error("Configure as variáveis de ambiente no Render")

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
            ticker = data.get('ticker', 'N/A')
            action = data.get('action', 'SINAL')
            price = data.get('price', 'N/A')
            time = data.get('time', hora_manaus.strftime("%H:%M:%S"))
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
        if isinstance(data, dict):
            # Verificar se tem campos específicos do TradingView
            ticker = data.get('ticker', 'N/A')
            action = data.get('action', 'SINAL')
            price = data.get('price', 'N/A')
            time = data.get('time', hora_manaus.strftime("%H:%M:%S"))
            timeframe = data.get('timeframe', 'N/A')
            strength = data.get('strength', 'N/A')
            details = data.get('details', 'Sinal confirmado!')
        # Adicionar formatação básica para alertas de texto
        current_time = hora_manaus.strftime("%H:%M:%S")
        
        message = f"""🚀 *FOGUETE TURBO V7* 📈

📢 *ALERTA RECEBIDO:*

{text}

📈 Ativo: *{ticker}*
💲 Sinal: *{action}*
⏰ Horário: *{current_time}*
🤖 Via: *TradingView Webhook*

#FogueteTurbo #Alerta #TradingView"""
        
        return message
        
    except Exception as e:
        logger.error(f"❌ Erro ao formatar alerta simples: {str(e)}")
        return f"🚀 FOGUETE TURBO V7\n\n{text}\n\n⏰ {hora_manaus.strftime('%H:%M:%S')}"

@app.route('/', methods=['GET'])
def home():
    """
    Página inicial - verificar se o bot está funcionando
    """
    return jsonify({
        "status": "🚀 FOGUETE TURBO V7 - Bot Telegram Online!",
        "platform": "Render + GitHub",
        "bot_configured": bool(BOT_TOKEN and CHAT_ID),
        "timestamp": hora_manaus.isoformat(),
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
            
            # Enviar para Telegram
            success = send_telegram_message(formatted_message)
            
            if success:
                return jsonify({
                    "status": "success",
                    "message": "Alerta enviado com sucesso para Telegram!",
                    "timestamp": hora_manaus.isoformat(),
                    "platform": "Render + GitHub"
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
        test_message = f"""🚀 *TESTE - FOGUETE TURBO V7* ✅

🎯 *Bot funcionando perfeitamente!*
📱 Telegram: *Conectado*
🌐 Webhook: *Ativo*
☁️ Plataforma: *Render + GitHub*
⏰ Horário: *{hora_manaus.strftime("%H:%M:%S")}*
📅 Data: *{hora_manaus.strftime("%d/%m/%Y")}*

💡 *Pronto para receber alertas do TradingView!*

#Teste #BotOnline #FogueteTurbo"""
        
        success = send_telegram_message(test_message)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "✅ Mensagem de teste enviada para Telegram!",
                "bot_token_configured": bool(BOT_TOKEN),
                "chat_id_configured": bool(CHAT_ID),
                "platform": "Render + GitHub",
                "timestamp": hora_manaus.isoformat()
            })
        else:
            return jsonify({
                "status": "error",
                "message": "❌ Erro ao enviar mensagem de teste"
            }), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """
    Verificar status completo do bot
    """
    return jsonify({
        "bot_online": True,
        "platform": "Render + GitHub",
        "bot_token_configured": bool(BOT_TOKEN),
        "chat_id_configured": bool(CHAT_ID),
        "timestamp": hora_manaus.isoformat(),
        "endpoints": {
            "home": "/",
            "webhook": "/webhook (POST)",
            "test": "/test (GET/POST)",
            "status": "/status (GET)"
        },
        "configuration": {
            "bot_token": "✅ Configurado" if BOT_TOKEN else "❌ Não configurado",
            "chat_id": "✅ Configurado" if CHAT_ID else "❌ Não configurado"
        },
        "instructions": {
            "webhook_url": "Use esta URL nos alertas do TradingView: https://SEU-APP.onrender.com/webhook",
            "test_url": "Teste o bot em: https://SEU-APP.onrender.com/test"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Health check para o Render
    """
    return jsonify({
        "status": "healthy",
        "timestamp": hora_manaus.isoformat()
    })

if __name__ == '__main__':
    # Porta do Render (padrão 10000)
    port = int(os.environ.get('PORT', 10000))
    
    # Log de inicialização
    logger.info("🚀 Iniciando FOGUETE TURBO V7 Bot...")
    logger.info("☁️ Plataforma: Render + GitHub")
    logger.info(f"🌐 Porta: {port}")
    logger.info(f"🤖 Bot Token: {'✅ Configurado' if BOT_TOKEN else '❌ Não configurado'}")
    logger.info(f"💬 Chat ID: {'✅ Configurado' if CHAT_ID else '❌ Não configurado'}")
    
    # Iniciar servidor
    app.run(host='0.0.0.0', port=port, debug=False)

