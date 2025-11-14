# 🔍 Diferenças de Código - Antes e Depois

## 1. notifications/evolution.py

### ANTES ❌
```python
def send_text_message(self, phone, message):
    """Send text message via Evolution API"""
    url = f"{self.base_url}/message/sendText/{self.instance_name}"

    # Evolution API expects just the phone number, NO @s.whatsapp.net suffix
    # Remove @s.whatsapp.net if present
    if '@' in phone:
        phone = phone.split('@')[0]

    payload = {
        'number': phone,
        'text': message
    }
    # ... resto do código
```

**Problema**: Destroi qualquer ID com `@`, incluindo `120363xxx@g.us` de grupos.

### DEPOIS ✅
```python
def _is_group(self, phone):
    """Check if phone/jid is a group"""
    return '@g.us' in str(phone).lower()

def _normalize_phone(self, phone):
    """Normalize phone number, preserving group format"""
    phone = str(phone).strip()
    
    # If it's a group, keep the full JID format
    if self._is_group(phone):
        return phone
    
    # For regular numbers, remove @ and everything after
    if '@' in phone:
        phone = phone.split('@')[0]
    
    # Remove common formatting characters
    for char in [' ', '-', '(', ')', '+']:
        phone = phone.replace(char, '')
    
    # Keep only digits
    phone = ''.join(filter(str.isdigit, phone))
    
    # Add Brazil country code if not present
    if phone and not phone.startswith('55'):
        phone = '55' + phone
    
    return phone

def send_text_message(self, phone, message):
    """Send text message via Evolution API"""
    url = f"{self.base_url}/message/sendText/{self.instance_name}"

    # Normalize phone/JID
    phone = self._normalize_phone(phone)
    is_group = self._is_group(phone)

    payload = {
        'number': phone,
        'text': message
    }
    # ... resto do código
```

**Solução**: 
- Detecta grupos antes de processar
- Preserva formato de grupo
- Normaliza números corretamente

---

## 2. notifications/views.py

### ANTES ❌
```python
@staff_member_required
def send_test_message(request):
    """Send test WhatsApp message"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        message = request.POST.get('message', 'Mensagem de teste do sistema de rifas!')

        if not phone:
            return JsonResponse({
                'success': False,
                'error': 'Número de telefone é obrigatório'
            })

        # Remove caracteres não numéricos
        phone = ''.join(filter(str.isdigit, phone))

        # Adiciona código do Brasil se não tiver
        if not phone.startswith('55'):
            phone = '55' + phone

        try:
            result = evolution_api.send_text_message(phone, message)
            if result:
                return JsonResponse({
                    'success': True,
                    'message': 'Mensagem enviada com sucesso!',
                    'result': result
                })
```

**Problema**: Remove TODOS os caracteres não numéricos, incluindo `@` e `-` de grupos.

### DEPOIS ✅
```python
@staff_member_required
def send_test_message(request):
    """Send test WhatsApp message"""
    if request.method == 'POST':
        phone = request.POST.get('phone')
        message = request.POST.get('message', 'Mensagem de teste do sistema de rifas!')

        if not phone:
            return JsonResponse({
                'success': False,
                'error': 'Número de telefone ou ID do grupo é obrigatório'
            })

        phone = phone.strip()
        
        # Check if it's a group (contains @g.us)
        is_group = '@g.us' in phone.lower()
        
        if not is_group:
            # For regular numbers, remove non-numeric characters and format
            phone_digits = ''.join(filter(str.isdigit, phone))
            
            if not phone_digits:
                return JsonResponse({
                    'success': False,
                    'error': 'Número de telefone inválido'
                })
            
            # Add Brazil country code if not present
            if not phone_digits.startswith('55'):
                phone_digits = '55' + phone_digits
            
            phone = phone_digits

        try:
            result = evolution_api.send_text_message(phone, message)
            if result:
                dest_info = "grupo" if is_group else "número"
                return JsonResponse({
                    'success': True,
                    'message': f'Mensagem enviada com sucesso para o {dest_info}!',
                    'result': result
                })
```

**Solução**:
- Detecta tipo (grupo ou número) antes de processar
- Processa apenas números como números
- Preserva grupos como estão
- Retorna mensagens apropriadas para cada tipo

---

## 3. templates/admin/whatsapp_manager.html

### ANTES ❌
```html
<div class="test-message-form">
    <h2>Enviar Mensagem de Teste</h2>
    <form id="test-form" onsubmit="sendTestMessage(event)">
        {% csrf_token %}
        <div class="form-group">
            <label for="phone">Número do WhatsApp (com código do país)</label>
            <input type="text" id="phone" name="phone" placeholder="5511999999999" required>
        </div>
        <div class="form-group">
            <label for="message">Mensagem</label>
            <textarea id="message" name="message" placeholder="Digite sua mensagem...">Olá! Esta é uma mensagem de teste do sistema de rifas. 🎉</textarea>
        </div>
        <button type="submit" class="btn btn-primary">📤 Enviar Mensagem</button>
    </form>
</div>
```

**Problema**: 
- Apenas menciona "Número do WhatsApp"
- Sem instrução sobre grupos
- Sem dicas de formatação

### DEPOIS ✅
```html
<div class="test-message-form">
    <h2>Enviar Mensagem de Teste</h2>
    <p style="color: #666; margin-bottom: 15px; font-size: 14px;">
        💡 <strong>Dica:</strong> Você pode enviar para números individuais ou para grupos. 
        Para grupos, copie o ID do grupo do WhatsApp (formato: <code>120363xxx@g.us</code>)
    </p>
    <form id="test-form" onsubmit="sendTestMessage(event)">
        {% csrf_token %}
        <div class="form-group">
            <label for="phone">Número do WhatsApp ou ID do Grupo</label>
            <input type="text" id="phone" name="phone" 
                placeholder="5511999999999 ou 120363xxx@g.us" 
                required
                style="font-family: monospace;">
            <small style="color: #999; display: block; margin-top: 5px;">
                📱 <strong>Para número:</strong> Use com ou sem + e código do país<br>
                👥 <strong>Para grupo:</strong> Cole o ID do grupo (termine com @g.us)
            </small>
        </div>
        <div class="form-group">
            <label for="message">Mensagem</label>
            <textarea id="message" name="message" placeholder="Digite sua mensagem...">Olá! Esta é uma mensagem de teste do sistema de rifas. 🎉</textarea>
        </div>
        <button type="submit" class="btn btn-primary">📤 Enviar Mensagem</button>
    </form>
</div>
```

**Solução**:
- Título agora menciona "Número ou ID do Grupo"
- Placeholder mostra ambas as opções
- Dica clara e visível no topo
- Instruções específicas para cada tipo
- Monospace font para melhor legibilidade

---

## 📊 Resumo das Mudanças

| Aspecto | Antes | Depois |
|--------|-------|--------|
| **Detecção de tipo** | Não | Sim - `_is_group()` |
| **Normalização inteligente** | Não | Sim - `_normalize_phone()` |
| **Suporte a grupos** | ❌ | ✅ |
| **Interface** | Genérica | Específica para cada tipo |
| **Mensagens de erro** | Genéricas | Específicas |
| **Documentação** | Não | Sim - 5 guias |
| **Testes** | Não | Sim - 9 testes |

---

## 🔄 Fluxo de Processamento

### ANTES ❌
```
Entrada (qualquer formato)
    ↓
Remove tudo que não é número
    ↓
Adiciona código 55 se necessário
    ↓
Envia para API
    ↓
❌ Grupos não funcionam
```

### DEPOIS ✅
```
Entrada (número ou grupo)
    ↓
Detecta tipo (@g.us?)
    ├─ É grupo?
    │  └─ SIM: Preserva ID completo
    │
    └─ É número?
       └─ SIM: Normaliza e adiciona código 55
    ↓
Envia para API com tipo correto
    ↓
✅ Ambos funcionam perfeitamente
```

---

## 🧪 Verificação

Para verificar que tudo funciona:

```bash
cd /Users/user/Desktop/Programação/rifas

# Executar testes
python3 test_group_messages.py

# Verificar sintaxe
python3 -m py_compile notifications/evolution.py
python3 -m py_compile notifications/views.py
```

---

**Data da Mudança**: 14 de novembro de 2025  
**Status**: ✅ Implementado e Testado
