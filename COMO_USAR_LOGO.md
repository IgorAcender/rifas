# Como Personalizar a Logo do Site

## Visão Geral

O sistema agora suporta upload de logo personalizada que será exibida em **todas as páginas do site**, incluindo:

- ✅ Painel administrativo (sidebar)
- ✅ Página de login do admin
- ✅ Página de login do cliente
- ✅ Página de login genérica
- ✅ Todas as outras páginas que herdam dos templates base

## Como Fazer Upload da Logo

### 1. Acesse o Painel

1. Faça login no sistema: `http://seu-dominio.com/admin-login`
2. No menu lateral, clique em "**Logo do Site**"

### 2. Faça Upload da Imagem

1. Na página de configurações, você verá uma caixa de upload com a opção:
   - **Clique** na caixa para selecionar uma imagem
   - Ou **arraste e solte** sua logo diretamente na caixa

2. A imagem será automaticamente:
   - Convertida para Base64
   - Exibida como preview
   - Salva no sistema

3. (Opcional) Altere o "Nome do Site" se desejar

4. Clique em "**Salvar Configurações**"

### 3. Pronto!

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

### A logo não aparece após fazer upload

1. Verifique se a imagem foi carregada corretamente (deve aparecer um preview)

2. Clique em "Salvar Configurações" após fazer o upload

3. Limpe o cache do navegador (Ctrl+Shift+R ou Cmd+Shift+R)

4. Verifique se você está logado como administrador

### A logo aparece distorcida

- Certifique-se de usar uma imagem quadrada (120x120px recomendado)
- Use PNG com fundo transparente para melhor resultado
- Tente fazer upload de uma nova imagem otimizada

### Erro ao fazer upload

- Verifique o tamanho da imagem (recomendado: menos de 2MB)
- Confirme que está usando um formato suportado (PNG, JPG, SVG)
- Otimize a imagem antes do upload usando TinyPNG ou Squoosh

## Suporte

Em caso de dúvidas ou problemas, entre em contato com o suporte técnico.
