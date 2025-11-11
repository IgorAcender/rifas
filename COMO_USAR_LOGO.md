# Como Personalizar a Logo do Site

## Visão Geral

O sistema agora suporta upload de logo personalizada que será exibida em **todas as páginas do site**, incluindo:

- ✅ Painel administrativo (sidebar)
- ✅ Página de login do admin
- ✅ Página de login do cliente
- ✅ Página de login genérica
- ✅ Todas as outras páginas que herdam dos templates base

## Como Fazer Upload da Logo

### 1. Acesse o Painel Admin

1. Acesse: `http://seu-dominio.com/admin`
2. Faça login com suas credenciais de administrador

### 2. Navegue até Configurações do Site

1. No menu lateral, procure por "**Raffles**"
2. Clique em "**Site Configurations**" ou "**Configurações do Site**"
3. Você verá a configuração existente (ou poderá criar uma nova)

### 3. Converta sua Logo para Base64

1. Acesse um conversor online gratuito:
   - **https://base64-image.de** (recomendado)
   - **https://www.base64-image.de**
   - Ou pesquise "image to base64 converter"

2. Faça upload da sua logo no conversor
3. Copie o código gerado (começará com `data:image/...`)

### 4. Cole o Código Base64

1. Volte para a edição da configuração no admin
2. Na seção "**Logo e Identidade Visual**":
   - Cole o código Base64 completo no campo "Logo do Site (Base64)"
   - (Opcional) Altere o "Nome do Site" se desejar
3. Clique em "**Salvar**"

### 5. Pronto!

A logo será automaticamente exibida em todas as páginas do site! ✨

## Especificações Recomendadas para a Logo

- **Formato**: PNG (preferencialmente com fundo transparente)
- **Tamanho**: 120x120 pixels
- **Formatos suportados**: PNG, JPG, JPEG, SVG
- **Peso**: Máximo 2MB (recomendado: menos de 500KB)

### Tamanhos de Exibição

A logo será redimensionada automaticamente para:
- **Sidebar do admin**: 60x60px
- **Páginas de login**: 80x80px
- **Outras páginas**: Variável conforme o template

## Logo Padrão

Se nenhuma logo for carregada, o sistema usará a logo padrão (ícone "W" azul com detalhes dourados).

## Detalhes Técnicos

### Como Funciona

1. **Base64**: A logo é armazenada como texto Base64 direto no banco de dados (mesmo padrão usado nas imagens das campanhas)

2. **Context Processor**: Um context processor injeta automaticamente a logo em todos os templates via variáveis:
   - `{{ site_logo }}`: URL da logo em formato base64
   - `{{ site_name }}`: Nome do site configurado
   - `{{ site_config }}`: Objeto completo de configuração

3. **Templates Atualizados**: Todos os templates que exibiam a logo hardcoded agora usam `{{ site_logo }}`

### Arquivos Modificados

- `raffles/models.py`: Adicionado modelo `SiteConfiguration`
- `raffles/admin.py`: Registrado admin para `SiteConfiguration`
- `raffles/context_processors.py`: Criado context processor
- `config/settings.py`: Adicionado context processor nas configurações
- `templates/base.html`: Logo dinâmica
- `templates/accounts/admin_login.html`: Logo dinâmica
- `templates/accounts/customer_login.html`: Logo dinâmica
- `templates/accounts/login.html`: Logo dinâmica

### Singleton Pattern

O modelo `SiteConfiguration` usa o padrão Singleton, garantindo que:
- Apenas **uma** configuração pode existir
- Não é possível deletar a configuração pelo admin
- Sempre há uma configuração disponível (criada automaticamente se necessário)

## Solução de Problemas

### A logo não aparece após colar o Base64

1. Verifique se você colou o código completo (deve começar com `data:image/...`)

2. Limpe o cache do navegador (Ctrl+Shift+R ou Cmd+Shift+R)

3. Verifique se o context processor está configurado em `settings.py`:
   ```python
   'raffles.context_processors.site_config'
   ```

### A logo aparece distorcida

- Certifique-se de usar uma imagem quadrada (120x120px recomendado)
- Use PNG com fundo transparente para melhor resultado
- Converta novamente a imagem usando um conversor diferente

### Código Base64 muito grande

- Otimize sua imagem antes de converter (reduza o tamanho/dimensões)
- Use ferramentas como TinyPNG ou Squoosh para comprimir
- Recomendado: imagens menores que 100KB

## Suporte

Em caso de dúvidas ou problemas, entre em contato com o suporte técnico.
