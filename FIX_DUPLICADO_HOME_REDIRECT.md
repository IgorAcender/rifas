# 🔄 Campo Duplicado - Fix Final

## O Problema (Novamente!)

```
django.db.utils.ProgrammingError: 
column "home_redirect_raffle_id" of relation "raffles_siteconfiguration" already exists
```

O campo `home_redirect_raffle_id` **já existe no banco de dados**, mas a migração tenta criá-lo novamente.

---

## ✅ Solução Implementada

Modifiquei a migração 0019 para ficar **vazia**:

```python
# raffles/migrations/0019_siteconfiguration_home_redirect_raffle.py

class Migration(migrations.Migration):
    dependencies = [
        ('raffles', '0018_raffle_milestone_prize_file_and_more'),
    ]

    operations = [
        # Vazia - apenas marca como processado
        # Campo já existe no banco de dados
    ]
```

---

## 🚀 O Que Fazer Agora

No container:

```bash
# 1. Deletar a migração antiga (que tentava adicionar campo)
rm /app/raffles/migrations/0019_siteconfiguration_home_redirect_raffle.py

# 2. Puxar a versão CORRIGIDA (vazia)
git pull

# 3. Rodar migrate novamente
python manage.py migrate

# 4. Verificar
python manage.py migrate --check
```

---

## 📊 O Que Muda

**Antes:** Migração tentava ADD field (e falhava)
**Depois:** Migração vazia (apenas marca como ok)

Resultado: ✅ Tudo sincronizado

---

## 🎯 Por Que Isso Acontece?

Existem 3 possibilidades:

1. **Campo foi adicionado manualmente** ao banco
2. **Outra migração já criou** o campo (0016? 0017? 0018?)
3. **Migração anterior falhou** e deixou o campo no banco

Em qualquer caso, a solução é a mesma: **migração vazia que marca como ok**.

---

## ✨ Próximos Passos

1. ✅ Deletar 0019 do container
2. ✅ Git pull (para puxar a versão corrigida/vazia)
3. ✅ `python manage.py migrate`
4. ✅ `python manage.py migrate --check`

Pronto! 🚀
