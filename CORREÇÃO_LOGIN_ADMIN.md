# 🔧 CORREÇÃO DO LOGIN DO ADMIN

## Problema Identificado

O login do admin estava pedindo **WhatsApp + Senha**, mas deveria pedir apenas **Email + Senha**.

## O que foi corrigido

✅ **Login de Admin** (`/admin-login/`):
- Agora usa apenas **EMAIL + SENHA**
- Removidos campos de WhatsApp e Nome

✅ **Login de Compradores** (`/login/`):
- Continua usando apenas **WHATSAPP** (sem senha)
- Funciona automaticamente

## Como corrigir seu acesso atual

Você precisa adicionar um email ao seu usuário admin existente.

### Opção 1: Script Automático (Recomendado)

```bash
chmod +x fix_admin_login.sh
./fix_admin_login.sh
```

O script vai perguntar:
1. Seu email de admin
2. Se quer atualizar a senha (opcional)

### Opção 2: Manual via Django Shell

```bash
python manage.py shell
```

Depois execute:

```python
from accounts.models import User

# Buscar o admin
admin = User.objects.filter(is_staff=True).first()

# Atualizar email
admin.email = "seu@email.com"

# Opcionalmente atualizar senha
admin.set_password("sua_senha_nova")

# Salvar
admin.save()

print(f"✅ Admin atualizado: {admin.name}")
print(f"   Email: {admin.email}")
```

### Opção 3: Comando Django

```bash
# Apenas email
python manage.py update_admin_email --email="seu@email.com"

# Email + senha
python manage.py update_admin_email --email="seu@email.com" --password="suasenha123"
```

## Após a correção

### Login de Admin
Acesse: `http://localhost:8000/admin-login/`

Campos:
- 📧 **Email**: o email que você configurou
- 🔑 **Senha**: a senha do admin (padrão: `admin123` ou a que você definiu)

### Login de Compradores
Acesse: `http://localhost:8000/login/`

Campo:
- 📱 **WhatsApp**: apenas o número (ex: 5511999999999)

## Arquivos Modificados

1. **`accounts/views.py`**: Função `admin_login()` agora usa email
2. **`templates/accounts/admin_login.html`**: Removidos campos desnecessários
3. **`accounts/management/commands/update_admin_email.py`**: Novo comando criado
4. **`accounts/management/commands/create_admin.py`**: Atualizado para incluir email

## Diferenças entre os logins

| Tipo | URL | Campos | Autenticação |
|------|-----|--------|--------------|
| **Admin** | `/admin-login/` | Email + Senha | Tradicional |
| **Comprador** | `/login/` | Apenas WhatsApp | Sem senha |

## Próximos passos recomendados

1. ✅ Execute o script de correção
2. ✅ Teste o login em `/admin-login/`
3. ✅ Verifique que compradores ainda conseguem logar em `/login/`
4. ✅ Atualize suas variáveis de ambiente para incluir `ADMIN_EMAIL`

## Variáveis de ambiente sugeridas

Adicione ao seu `.env`:

```env
ADMIN_EMAIL=seu@email.com
ADMIN_PASSWORD=suasenhasegura123
ADMIN_NAME=Seu Nome
ADMIN_WHATSAPP=5511999999999  # Ainda necessário para o modelo
```
