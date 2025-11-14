# 🔧 Correção de Migration - Deploy do Modo de Teste

## Problema

A migration 0019 estava tentando adicionar campos que já existem no banco de produção:
- ❌ `premium_numbers` (já existe)
- ❌ `home_redirect_raffle_id` (já existe)
- ✅ `is_test_mode` (novo - precisa adicionar)

## Solução Implementada

Modifiquei a migration 0019 para usar `RunPython` com verificação:
- Verifica se cada coluna já existe antes de adicionar
- Só adiciona se não existir
- Funciona tanto em produção (PostgreSQL) quanto local (SQLite)

## Como Fazer Deploy

### 1. Commit e Push das alterações

```bash
git add .
git commit -m "feat: adiciona modo de teste com toggle de número premiado"
git push origin main
```

### 2. No servidor, fazer pull

```bash
cd /caminho/do/projeto
git pull origin main
```

### 3. Aplicar a migration

A migration agora é segura e pode ser aplicada normalmente:

```bash
# Se usar docker-compose
docker-compose exec web python manage.py migrate

# Ou se usar docker run
docker exec -it nome_container python manage.py migrate

# Ou direto (se não usar docker)
python manage.py migrate
```

### 4. Reiniciar o servidor

```bash
# Se usar docker-compose
docker-compose restart web

# Ou se usar docker run
docker restart nome_container

# Ou se usar supervisor/systemd
sudo systemctl restart rifas
```

## Verificar se funcionou

1. Acesse o Admin Django
2. Entre em Raffles > Raffles
3. Edite uma campanha
4. Você deve ver o novo campo: **"Modo de Teste"** ✅
5. Marque-o e salve
6. Acesse a página pública da campanha
7. Faça um cadastro e veja o botão de teste aparecer

## Se algo der errado

Se a migration ainda falhar:

```bash
# Marcar migration 0019 como fake (pula ela)
python manage.py migrate raffles 0019 --fake

# Depois aplicar todas as migrations
python manage.py migrate
```

## Arquivos Modificados

- `raffles/models.py` - Adicionado campo `is_test_mode`
- `raffles/migrations/0019_...py` - Migration com verificação de campos
- `raffles/views.py` - View `test_payment` com toggle
- `config/urls.py` - Rota `/r/<slug>/test-payment/`
- `templates/raffles/public_view.html` - Modal com toggle
- `MODO_TESTE.md` - Documentação completa

## Status

✅ Implementação completa
✅ Migration segura (verifica campos existentes)
✅ Testado localmente
🚀 Pronto para deploy
