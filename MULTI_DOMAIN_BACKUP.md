# 🔄 Configuração de Domínios Múltiplos (Backup)

## Situação

Seu domínio principal `vip.institutoacender.com.br` saiu do ar.  
Agora você tem um domínio de backup no EasyPanel: `acender-sorteios-acender-sorteios.ivhjcm.easypanel.host`

## ✅ Solução Implementada

Foi adicionado um **middleware de detecção dinâmica de domínio** que:

1. **Detecta qual domínio o usuário está usando**
2. **Automaticamente gera links com esse domínio**
3. **Funciona perfeitamente mesmo se o principal cair**

## 🔧 Configuração do .env

Atualize as seguintes variáveis no seu `.env` em produção:

```bash
# Adicione AMBOS os domínios
ALLOWED_HOSTS=vip.institutoacender.com.br,acender-sorteios-acender-sorteios.ivhjcm.easypanel.host

# Adicione AMBOS os domínios
CSRF_TRUSTED_ORIGINS=https://vip.institutoacender.com.br,https://acender-sorteios-acender-sorteios.ivhjcm.easypanel.host

# Mantenha o principal como fallback
SITE_URL=https://vip.institutoacender.com.br
```

## 🚀 Como Funciona

**Cenário 1: Principal Online**
- Usuário acessa: `vip.institutoacender.com.br`
- Sistema usa: Links com `vip.institutoacender.com.br`
- ✅ Funciona normalmente

**Cenário 2: Principal Fora do Ar**
- Usuário acessa: `acender-sorteios-acender-sorteios.ivhjcm.easypanel.host`
- Sistema usa: Links com `acender-sorteios-acender-sorteios.ivhjcm.easypanel.host`
- ✅ Funciona perfeitamente - sem quebra de links!

**Cenário 3: Ambos Online**
- Usuário pode usar qualquer um
- Links gerados são sempre válidos para o domínio acessado
- ✅ Total flexibilidade

## 📝 Checklist de Deploy

- [ ] Atualize o `.env` em produção com os novos `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`
- [ ] Execute `docker-compose up` ou redeploy sua aplicação
- [ ] Teste acessando o domínio principal
- [ ] Teste acessando o domínio do EasyPanel
- [ ] Verifique se os links gerados estão corretos em ambos

## 🔗 Domínios Configurados

| Domínio | Tipo | Status |
|---------|------|--------|
| `vip.institutoacender.com.br` | Principal | ⚠️ Offline |
| `acender-sorteios-acender-sorteios.ivhjcm.easypanel.host` | Backup (EasyPanel) | ✅ Ativo |

## 💡 Próximos Passos

1. **Redirecionar o DNS do principal** para o EasyPanel (se quiser migrar definitivamente)
2. **Manter ambos ativos** para redundância total
3. **Configurar CDN** na frente para distribuição de carga

Qualquer dúvida, é só chamar! 🚀
