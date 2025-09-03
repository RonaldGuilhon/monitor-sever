# 🔒 PRÁTICAS DE SEGURANÇA - Monitor Server

## ⚠️ IMPORTANTE: Prevenção de Vazamento de Credenciais

Este documento estabelece as práticas obrigatórias para manter a segurança do projeto e prevenir vazamentos de credenciais.

## 📋 Checklist de Segurança

### ✅ Configuração Inicial
- [ ] Instalar pre-commit hooks: `pip install pre-commit && pre-commit install`
- [ ] Configurar GitGuardian: `ggshield auth login`
- [ ] Verificar `.gitignore` inclui arquivos sensíveis
- [ ] Criar arquivo `.env` local (nunca commitado)

### ✅ Desenvolvimento Diário
- [ ] Usar variáveis de ambiente para todas as credenciais
- [ ] Nunca hardcodar senhas, tokens ou chaves no código
- [ ] Executar `ggshield secret scan .` antes de commits importantes
- [ ] Revisar diffs antes de fazer push

## 🚫 O QUE NUNCA FAZER

```bash
# ❌ NUNCA faça isso:
SMTP_PASSWORD = "minha_senha_real_123"
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "postgresql://user:senha@host/db"

# ✅ SEMPRE faça isso:
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

## 📁 Arquivos que NUNCA devem ser commitados

```
.env
.env.local
.env.production
config/secrets.json
config/local/*
*.key
*.pem
*.p12
*.pfx
credentials.json
secrets.yaml
```

## 🔧 Configuração de Variáveis de Ambiente

### Desenvolvimento Local
1. Copie `.env.template` para `.env`
2. Preencha com suas credenciais reais
3. **NUNCA** commite o arquivo `.env`

### Produção
1. Configure variáveis no servidor/container
2. Use serviços de gerenciamento de segredos (AWS Secrets Manager, Azure Key Vault, etc.)
3. Configure CI/CD com GitHub Secrets

### GitHub Actions
```yaml
env:
  SMTP_HOST: ${{ secrets.SMTP_HOST }}
  SMTP_PORT: ${{ secrets.SMTP_PORT }}
  SMTP_USER: ${{ secrets.SMTP_USER }}
  SMTP_PASS: ${{ secrets.SMTP_PASS }}
  SMTP_FROM: ${{ secrets.SMTP_FROM }}
```

## 🛡️ Ferramentas de Segurança

### GitGuardian (ggshield)
```bash
# Instalar
pip install ggshield

# Configurar
ggshield auth login

# Escanear repositório
ggshield secret scan .

# Escanear antes do commit
ggshield secret scan pre-commit
```

### Pre-commit Hooks
```bash
# Instalar
pip install pre-commit
pre-commit install

# Executar manualmente
pre-commit run --all-files
```

### Verificação Manual
```bash
# Buscar padrões suspeitos
git grep -nE '(PASSWORD|API[_-]?KEY|SECRET|TOKEN).*=.*["\'][^"\']'

# Verificar histórico
git log --grep="password\|secret\|key" --oneline
```

## 🚨 PROCEDIMENTO DE EMERGÊNCIA

### Se credenciais foram expostas:

1. **IMEDIATO** - Revogar/rotacionar credenciais
   - Desative as credenciais no provedor
   - Gere novas credenciais
   - Atualize todos os ambientes

2. **Limpar histórico do Git**
   ```bash
   # Usando git filter-repo (recomendado)
   pip install git-filter-repo
   git filter-repo --replace-text <(echo 'literal:SENHA_EXPOSTA==>***REMOVED***')
   git push --force --all
   ```

3. **Notificar equipe**
   - Avisar sobre force push
   - Solicitar re-clone dos repositórios
   - Documentar o incidente

## 📚 Recursos Adicionais

- [GitGuardian Documentation](https://docs.gitguardian.com/)
- [OWASP Secrets Management](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

## 📞 Contato de Segurança

Em caso de incidentes de segurança, contate imediatamente:
- Responsável pelo projeto
- Administrador do sistema
- Equipe de DevOps/SRE

---

**Lembre-se: A segurança é responsabilidade de todos!** 🔐