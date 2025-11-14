# 🔧 Corrigindo Problema de Migração Django

## ❌ O Problema

```
django.db.utils.ProgrammingError: column "premium_numbers" of relation "raffles_raffle" already exists
```

O Django tentou criar uma migração 0019 que adiciona o campo `premium_numbers`, mas esse campo **já existe no banco de dados** desde as migrações anteriores (0012/0013).

---

## ✅ A Solução

Criei uma migração 0019 vazia que pula esse passo. Agora você precisa fazer:

### No Container:

```bash
# 1. Deletar a migração 0019 problemática (se ainda existir)
rm /app/raffles/migrations/0019_raffle_premium_numbers_and_more.py

# 2. Agora puxar a nova migração do seu PC
# (O arquivo raffles/migrations/0019_skip_duplicate_premium_numbers.py foi criado)

# 3. Recriar as migrações limpas
python manage.py makemigrations --merge --noinput

# 4. Aplicar a migração
python manage.py migrate

# 5. Verificar se funcionou
python manage.py migrate --check
```

---

## 📁 Arquivos Criados

### `raffles/migrations/0019_skip_duplicate_premium_numbers.py`
- Migração vazia que pula o passo problemático
- Respeita o histórico de migrações
- Permite que o Django continue normalmente

### `notifications/migrations/0003_*`
- Já foi aplicada automaticamente
- Apenas altera um campo de template

---

## 🧪 Teste Pós-Corrigir

```bash
# Ver se todas as migrações foram aplicadas
python manage.py migrate --check

# Deve retornar vazio (tudo OK) ou zero (nada a fazer)
```

---

## 📋 Se Ainda Não Funcionar

Se continuar com erro, tente:

```bash
# Resetar TUDO (⚠️ cuidado, deleta dados!)
# python manage.py migrate raffles zero  # NÃO FAÇA ISSO EM PRODUÇÃO!

# Opção segura: deletar apenas a migração 0019
rm /app/raffles/migrations/0019_*.py

# Recriar
python manage.py makemigrations raffles
python manage.py migrate
```

---

## 🎯 Raiz Causa

Alguém (provavelmente uma mudança recente) modificou o modelo da Raffle, mas:
- O campo `premium_numbers` já estava no banco (desde 0012/0013)
- Django tentou adicioná-lo novamente na 0019
- Banco rejeitou (duplicate column)

Isso é um conflito de estado entre o código e o banco.

---

## ✨ Próximos Passos

Depois de corrigir as migrações:

1. ✅ Deletar `/app/raffles/migrations/0019_raffle_premium_numbers_and_more.py` (se existir)
2. ✅ Executar `python manage.py migrate`
3. ✅ Verificar com `python manage.py migrate --check`

Pronto! 🚀
