-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- CRIAR DATABASE EVOLUTION NO POSTGRESQL
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Execute este script no terminal do PostgreSQL no EasyPanel
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- 1. Criar database evolution
CREATE DATABASE evolution;

-- 2. Verificar databases existentes
\l

-- 3. Conectar ao novo database
\c evolution

-- 4. Verificar conexão
SELECT current_database();

-- 5. Database está pronto!
-- A Evolution API criará as tabelas automaticamente na primeira execução

-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- INFORMAÇÕES
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
-- Database criado: evolution
-- Owner: postgres
-- Encoding: UTF8
-- Locale: pt_BR.UTF-8 ou en_US.UTF-8
-- ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

-- Para verificar tamanho do database futuramente:
-- SELECT pg_size_pretty(pg_database_size('evolution'));

-- Para listar tabelas criadas pela Evolution:
-- \dt

-- Para ver conexões ativas:
-- SELECT * FROM pg_stat_activity WHERE datname = 'evolution';
