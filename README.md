# 🚀 FOGUETE TURBO V7 - Bot Telegram MELHORADO v2.0

Bot inteligente para receber alertas do indicador **FOGUETE TURBO V7** do TradingView e enviar automaticamente para Telegram com **detecção inteligente de sinais** e **formatação profissional**.

## 🎯 Novidades v2.0

### ✅ **Detecção Inteligente de Sinais**
- 🟢🚀 **MASTER** (MACD + EMAs 12/26)
- 🚀⭐ **MASTER ESTRELA** (Stochastic + EMAs 21/50)
- 📈📉 **SuperTrend** (BUY/SELL)
- 📊 **Bollinger Bands** (Rejeições)
- 🔄 **Cruzamentos SMAs** (8x21)
- 💪 **Volume Forte**
- 💎 **Fibonacci**

### ✅ **Formatação Profissional**
- 🎨 **Emojis específicos** para cada estratégia
- 📱 **Markdown** para formatação rica
- 🕐 **Horário Manaus** (UTC-4) automático
- 📈 **Nome do ativo** detectado automaticamente
- 💪 **Força do sinal** extraída e formatada

### ✅ **Horário Correto**
- 🌎 **Fuso horário Manaus/Amazonas** (UTC-4)
- 🕐 **Conversão automática** de UTC para horário local
- ⏰ **Timestamp preciso** em cada mensagem

## 📱 Exemplos de Mensagens

### 🟢 MASTER COMPRA
```
🚀 FOGUETE TURBO V7 📈

🟢🚀 MASTER COMPRA!
📈 Ativo: BTCUSDT
⏰ Horário: 16:30:45 (Manaus)
💪 Força: 8/10 (80%)

🎯 Estratégia MASTER:
MACD + EMAs 12/26

💰 Sinal confirmado!

#Master #FogueteTurbo #TradingView
```

### 🚀⭐ MASTER ESTRELA
```
🚀 FOGUETE TURBO V7 ⭐

🚀⭐ MASTER ESTRELA COMPRA!
📈 Ativo: ETHUSDT
⏰ Horário: 16:30:45 (Manaus)
💪 Força: 9/10 (90%)

🎯 Estratégia ESTRELA:
Stochastic + EMAs 21/50

⭐ Sinal premium confirmado!

#MasterEstrela #FogueteTurbo #TradingView
```

### 📈 SuperTrend
```
🚀 FOGUETE TURBO V7 📈

📈🟢 SUPERTREND COMPRA!
📈 Ativo: ADAUSDT
⏰ Horário: 16:30:45 (Manaus)
💪 Força: 70%

🎯 SuperTrend:
Mudança de tendência confirmada

💰 Sinal de entrada!

#SuperTrend #FogueteTurbo #TradingView
```

## 🔧 Recursos Técnicos

### 🤖 **Detecção Automática**
- **Regex patterns** para identificar tipos de sinal
- **Análise de contexto** da mensagem
- **Classificação inteligente** por estratégia

### 🕐 **Fuso Horário**
- **UTC-4** (Manaus/Amazonas)
- **Conversão automática** de timestamps
- **Sem horário de verão** (Amazonas não tem)

### 📊 **Extração de Dados**
- **Nome do ativo** via regex
- **Força/porcentagem** automática
- **Tipo de sinal** por palavras-chave

## 🚀 Deploy e Configuração

### 1. **GitHub + Render**
- Deploy automático via GitHub
- Configuração via variáveis de ambiente
- 100% gratuito

### 2. **Variáveis de Ambiente**
```
BOT_TOKEN=7264851459:AAFLS0qBfjl3QhHFSpcT4sdERVIqvxRo8q8
CHAT_ID=seu_chat_id_aqui
```

### 3. **Endpoints**
- `/` - Status e informações
- `/webhook` - Receber alertas TradingView
- `/test` - Teste com formatação melhorada
- `/test-signals` - Testar detecção de sinais
- `/status` - Status completo com recursos

## 🎯 Melhorias Implementadas

### ✅ **Problemas Resolvidos**
- ❌ **Antes**: Mensagens simples sem formatação
- ✅ **Depois**: Formatação profissional com emojis

- ❌ **Antes**: Horário UTC confuso
- ✅ **Depois**: Horário Manaus correto

- ❌ **Antes**: Sem nome do ativo
- ✅ **Depois**: Ativo detectado automaticamente

- ❌ **Antes**: Sem diferenciação de sinais
- ✅ **Depois**: Cada sinal com emoji específico

### 🎨 **Formatação Inteligente**
- **MASTER**: 🟢🚀/🔴🚀 com estratégia MACD
- **MASTER ESTRELA**: 🚀⭐ com estratégia Stochastic
- **SuperTrend**: 📈🟢/📉🔴 com mudança de tendência
- **Bollinger**: 📊 com tipo de rejeição
- **SMAs**: 🔄 com direção do cruzamento
- **Volume**: 💪 com força detectada

## 🛠️ Desenvolvimento

### **Estrutura do Código**
```python
# Detecção de sinais
detect_signal_type(message)

# Formatação específica
get_signal_emoji_and_action(signal_type)

# Extração de dados
extract_asset_name(message)
extract_strength(message)

# Fuso horário
get_manaus_time()
```

### **Testes**
- `/test` - Teste geral
- `/test-signals` - Teste de detecção
- Logs detalhados para debug

---

## 🚀 FOGUETE TURBO V7 v2.0 - Sistema inteligente de alertas profissionais!

