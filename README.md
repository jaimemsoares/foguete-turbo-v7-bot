# 🚀 FOGUETE TURBO V7 - Bot Telegram

Bot para receber alertas do indicador **FOGUETE TURBO V7** do TradingView e enviar automaticamente para Telegram com formatação profissional.

## 🎯 Funcionalidades

- ✅ **Recebe alertas** do TradingView via webhook
- ✅ **Envia para Telegram** com formatação melhorada
- ✅ **Formatação profissional** com emojis e Markdown
- ✅ **Deploy gratuito** no Render
- ✅ **Funcionamento 24/7** automático
- ✅ **Logs detalhados** para debug

## 📋 Arquivos

- `app.py` - Código principal do bot Python/Flask
- `requirements.txt` - Dependências Python
- `render.yaml` - Configuração específica do Render
- `runtime.txt` - Versão Python
- `.gitignore` - Arquivos ignorados pelo Git

## 🚀 Deploy no Render

### 1. Fork este repositório
### 2. Conectar ao Render
### 3. Configurar variáveis de ambiente:
- `BOT_TOKEN`: Token do bot Telegram
- `CHAT_ID`: ID do canal/grupo Telegram

### 4. Deploy automático!

## 🔗 Endpoints

- `/` - Status do bot e informações
- `/webhook` - Receber alertas do TradingView (POST)
- `/test` - Testar envio de mensagem
- `/status` - Verificar configuração completa
- `/health` - Health check

## 🎯 Como Usar

1. **Configure o webhook** no TradingView:
   ```
   https://seu-app.onrender.com/webhook
   ```

2. **Teste o funcionamento**:
   ```
   https://seu-app.onrender.com/test
   ```

3. **Verifique o status**:
   ```
   https://seu-app.onrender.com/status
   ```

## 📱 Exemplo de Mensagem

```
🚀 FOGUETE TURBO V7 📈

💰 COMPRA CONFIRMADA!
📈 Ativo: BTCUSDT
💲 Preço: 45,230.50
⏰ Horário: 15:30:45
📅 TF: 1h
💪 Força: 8/10 (80%)

🎯 Detalhes:
SuperTrend BUY + MACD positivo + Volume forte

#FogueteTurbo #TradingView #Alertas
```

## 🔧 Configuração

### Variáveis de Ambiente (Render)
```
BOT_TOKEN=seu_token_do_bot_telegram
CHAT_ID=id_do_seu_canal_telegram
```

### Token do Bot
1. Fale com @BotFather no Telegram
2. Crie um novo bot: `/newbot`
3. Copie o token gerado

### Chat ID
1. Adicione @userinfobot ao seu canal
2. Ele mostrará o Chat ID automaticamente
3. Remova o bot depois

## 🛠️ Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export BOT_TOKEN="seu_token"
export CHAT_ID="seu_chat_id"

# Executar
python app.py
```

## 📞 Suporte

- Verifique os logs no Render
- Teste endpoints individualmente
- Confirme configuração das variáveis
- Verifique permissões do bot no Telegram

---

## 🚀 FOGUETE TURBO V7 - Sistema completo de alertas automáticos!

