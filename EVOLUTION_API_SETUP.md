# Configuração da Evolution API

Este guia explica como configurar e usar a Evolution API no sistema de rifas.

## 📋 Pré-requisitos

1. Instância da Evolution API configurada e funcionando
2. API Key da sua instância
3. Nome da instância

## 🔧 Configuração

### 1. Variáveis de Ambiente

Adicione as seguintes variáveis no seu arquivo `.env`:

```bash
# Evolution API
EVOLUTION_API_URL=https://sua-evolution-api.com
EVOLUTION_API_KEY=sua-api-key-aqui
EVOLUTION_INSTANCE_NAME=nome-da-sua-instancia
```

**Exemplo:**
```bash
EVOLUTION_API_URL=https://evo.exemplo.com.br
EVOLUTION_API_KEY=B6D9F8E2A1C4D5E6F7G8H9I0J1K2L3M4
EVOLUTION_INSTANCE_NAME=rifas-whatsapp
```

### 2. Estrutura da URL da API

A Evolution API geralmente usa o seguinte formato:

- **Base URL**: `https://seu-dominio.com` ou `http://seu-ip:8080`
- **Endpoints**:
  - Enviar mensagem: `POST /message/sendText/{instance}`
  - Status: `GET /instance/connectionState/{instance}`

### 3. Verificar Configuração

Execute o script de teste para verificar se tudo está funcionando:

```bash
python test_evolution.py
```

## 🚀 Como Funciona

### Sistema de Fallback Automático

O sistema implementa fallback automático entre APIs:

1. **Primeira tentativa**: Evolution API
2. **Fallback**: Avolution API (se Evolution falhar)

```python
# O código já trata automaticamente:
from notifications.whatsapp import send_whatsapp_message

# Tenta Evolution primeiro, depois Avolution se necessário
send_whatsapp_message('5511999999999', 'Olá!')
```

### Funções Disponíveis

#### 1. Enviar Mensagem Simples

```python
from notifications.evolution import send_whatsapp_message

send_whatsapp_message(
    phone='5511999999999',
    message='Sua mensagem aqui'
)
```

#### 2. Enviar Confirmação de Pagamento

```python
from notifications.evolution import send_payment_confirmation

# order é uma instância de RaffleOrder
send_payment_confirmation(order)
```

#### 3. Enviar Notificação de Ganhador

```python
from notifications.evolution import send_winner_notification

# raffle: instância de Raffle
# winner_number: instância de AllocatedNumber (número vencedor)
send_winner_notification(raffle, winner_number)
```

#### 4. Verificar Status da Instância

```python
from notifications.evolution import evolution_api

status = evolution_api.check_instance_status()
print(status)
```

## 📱 Formato de Números

A Evolution API aceita números nos seguintes formatos:

- `5511999999999` - número com código do país
- `5511999999999@s.whatsapp.net` - formato completo (automático)

O sistema converte automaticamente para o formato correto.

## 🔍 Logs e Debugging

Os logs são salvos automaticamente usando o logger do Django:

```python
import logging
logger = logging.getLogger(__name__)
```

Para ver os logs durante desenvolvimento:

```python
# Em settings.py, configure:
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

## ⚙️ Endpoints da Evolution API

### Enviar Mensagem de Texto
```
POST /message/sendText/{instance}
Headers:
  - apikey: YOUR_API_KEY
  - Content-Type: application/json
Body:
{
  "number": "5511999999999@s.whatsapp.net",
  "text": "Sua mensagem"
}
```

### Enviar Mídia
```
POST /message/sendMedia/{instance}
Headers:
  - apikey: YOUR_API_KEY
  - Content-Type: application/json
Body:
{
  "number": "5511999999999@s.whatsapp.net",
  "mediatype": "image",
  "media": "https://url-da-imagem.com/imagem.jpg",
  "caption": "Legenda opcional"
}
```

### Verificar Status
```
GET /instance/connectionState/{instance}
Headers:
  - apikey: YOUR_API_KEY
```

## 🧪 Testando a Integração

### Teste Manual via Script

```bash
# Execute o script de teste
python test_evolution.py

# Opções do menu:
# 1. Testar conexão
# 2. Enviar mensagem de teste
# 3. Testar conexão + enviar mensagem
# 4. Sair
```

### Teste no Shell do Django

```bash
python manage.py shell
```

```python
from notifications.evolution import evolution_api, send_whatsapp_message

# Testar conexão
status = evolution_api.check_instance_status()
print(status)

# Enviar mensagem de teste
send_whatsapp_message('5511999999999', 'Teste!')
```

## 🛠️ Resolução de Problemas

### Erro: "No WhatsApp API configured!"

**Causa**: Nenhuma API está configurada (nem Evolution nem Avolution)

**Solução**: Configure pelo menos uma das APIs no arquivo `.env`

### Erro: Timeout

**Causa**: A API não está respondendo

**Soluções**:
1. Verifique se a URL está correta
2. Verifique se a instância está online
3. Verifique firewall/segurança

### Erro: 401 Unauthorized

**Causa**: API Key incorreta

**Solução**: Verifique a API Key no `.env`

### Erro: 404 Not Found

**Causa**: Nome da instância incorreto ou instância não existe

**Solução**: Verifique o `EVOLUTION_INSTANCE_NAME`

### Mensagens não chegam

**Checklist**:
1. ✅ Instância está conectada ao WhatsApp?
2. ✅ Número está no formato correto (com código do país)?
3. ✅ API Key está correta?
4. ✅ Verifique os logs do sistema

## 📊 Monitoramento

Para monitorar o uso da API em produção:

```python
# Adicione em um management command ou view admin
from notifications.evolution import evolution_api

def check_whatsapp_status():
    status = evolution_api.check_instance_status()
    if status:
        return {
            'provider': 'Evolution API',
            'status': 'connected',
            'details': status
        }
    return {
        'provider': 'Evolution API',
        'status': 'disconnected'
    }
```

## 🔄 Migração da Avolution para Evolution

Não é necessário migrar! O sistema funciona com ambas:

- **Evolution API**: Prioritária (tentada primeiro)
- **Avolution API**: Fallback automático

Você pode manter ambas configuradas para redundância.

## 📝 Notas Importantes

1. **Rate Limiting**: Respeite os limites da Evolution API
2. **Timeout**: Requests têm timeout de 30 segundos
3. **Retry**: Não há retry automático (usa fallback)
4. **Formato**: Mensagens suportam formatação WhatsApp (*negrito*, _itálico_)

## 🆘 Suporte

Para problemas com a Evolution API:
- Documentação: https://doc.evolution-api.com
- GitHub: https://github.com/EvolutionAPI/evolution-api

Para problemas com a integração neste projeto:
- Verifique os logs do Django
- Execute `test_evolution.py` para diagnóstico
- Verifique as configurações no `.env`
