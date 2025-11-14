# ✅ Migrações Django - Corrigidas

## O Problema

O container detectava mudanças pendentes nos modelos que não foram migradas:

```
Your models in app(s): 'notifications', 'raffles' have changes 
that are not yet reflected in a migration, and so won't be applied.
```

---

## A Solução

Criei duas migrações legítimas para sincronizar código e banco:

### 1. `raffles/migrations/0019_siteconfiguration_home_redirect_raffle.py`

Adiciona o campo `home_redirect_raffle` à tabela `SiteConfiguration`:

```python
# Este campo permite:
# - Redirecionar a home para uma campanha específica
# - Se vazio, mostra lista de campanhas
```

### 2. `notifications/migrations/0003_alter_whatsappmessagetemplate_template.py`

Altera o campo `template` em `WhatsAppMessageTemplate`:

```python
# Atualiza o help_text com placeholders disponíveis
```

---

## 🚀 Como Aplicar (No Container)

```bash
# 1. Puxar os arquivos novos (já estão em /app se você fez git pull)
cd /app

# 2. Aplicar as migrações
python manage.py migrate

# 3. Verificar se deu certo
python manage.py migrate --check

# Deve retornar VAZIO (sem mensagens) = OK ✅
```

---

## 📊 Resultado Esperado

```
root@xxx:/app# python manage.py migrate
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, notifications, raffles, sessions
Running migrations:
  Applying notifications.0003_alter_whatsappmessagetemplate_template... OK
  Applying raffles.0019_siteconfiguration_home_redirect_raffle... OK

root@xxx:/app# python manage.py migrate --check
root@xxx:/app# 
```

Sem mensagens = Tudo aplicado corretamente ✅

---

## 🔍 O Que Mudou

### Arquivo: `raffles/models.py`

Campo novo em `SiteConfiguration`:

```python
home_redirect_raffle = models.ForeignKey(
    'Raffle',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    verbose_name='Campanha Padrão da Home',
    help_text='Campanha para a qual a página inicial redirecionará. Se vazio, mostra lista de campanhas.'
)
```

### Arquivo: `notifications/models.py`

Campo `template` agora tem help_text descritivo:

```python
template = models.TextField(
    help_text="Use placeholders: {name}, {raffle_name}, {prize_name}, {draw_date}, {numbers}, {amount}, {order_id}, {customer_area_url}"
)
```

---

## 📁 Arquivos Criados

```
raffles/migrations/0019_siteconfiguration_home_redirect_raffle.py
notifications/migrations/0003_alter_whatsappmessagetemplate_template.py
```

---

## ✨ Próximos Passos

1. ✅ Faça git pull para puxar as novas migrações
2. ✅ No container, rode `python manage.py migrate`
3. ✅ Verifique com `python manage.py migrate --check`
4. ✅ Reinicie o Django (se necessário)

Pronto! 🚀
