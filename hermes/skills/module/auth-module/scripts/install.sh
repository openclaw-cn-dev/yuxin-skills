#!/bin/bash
# Auth Module Installer - Run in your project directory
# Usage: bash <(curl -sL https://raw.githubusercontent.com/...) auth-module-install.sh

set -e

echo "🔐 Auth Module Installer"
echo "========================"

# Detect project type
if [ -f "package.json" ] && [ -f "requirements.txt" ]; then
    PROJECT_TYPE="fullstack"
elif [ -f "requirements.txt" ] || [ -f "pyproject.toml" ]; then
    PROJECT_TYPE="python"
elif [ -f "package.json" ]; then
    PROJECT_TYPE="nodejs"
else
    PROJECT_TYPE="unknown"
fi

echo "Detected project type: $PROJECT_TYPE"

# Install Python dependencies
install_python() {
    echo "📦 Installing Python dependencies..."
    pip install python-jose[cryptography] passlib[bcrypt] python-multipart pydantic email-validator
    echo "✅ Python dependencies installed"
}

# Install Node dependencies
install_nodejs() {
    echo "📦 Installing Node dependencies..."
    npm install element-plus @element-plus/icons-vue pinia
    echo "✅ Node dependencies installed"
}

# Copy backend files
copy_backend() {
    echo "📁 Copying backend files..."
    mkdir -p auth
    cp -r ~/.hermes/skills/module/auth-module/backend/* auth/
    echo "✅ Backend files copied to ./auth/"
}

# Copy frontend files
copy_frontend() {
    echo "📁 Copying frontend files..."
    mkdir -p src/api src/stores src/components/auth
    cp ~/.hermes/skills/module/auth-module/frontend/api/auth.js src/api/
    cp ~/.hermes/skills/module/auth-module/frontend/stores/auth.js src/stores/
    cp ~/.hermes/skills/module/auth-module/frontend/components/*.vue src/components/auth/
    echo "✅ Frontend files copied"
}

# Main
case $PROJECT_TYPE in
    fullstack)
        install_python
        install_nodejs
        copy_backend
        copy_frontend
        ;;
    python)
        install_python
        copy_backend
        ;;
    nodejs)
        install_nodejs
        copy_frontend
        ;;
    *)
        echo "⚠️ Unknown project type. Please copy files manually."
        ;;
esac

echo ""
echo ""
echo "⚠️  重要：登录响应字段名修复"
echo "  auth-module 的 service.py 登录方法默认返回 {\"token\": ...}"
echo "  但 Pydantic LoginResponse 模型期望 {\"access_token\": ...}"
echo "  请检查并修改 service.py 第 46 行:"
echo "    \"token\": access_token  →  \"access_token\": access_token"
echo "  同时检查 models.py 的 LoginResponse 确保包含 access_token 和 refresh_token 字段。"
echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Add auth router to your main.py:"
echo "   from auth.router import router as auth_router"
echo "   app.include_router(auth_router, prefix='/api/auth', tags=['认证'])"
echo ""
echo "2. Add to your frontend App.vue:"
echo "   import LoginDialog from './components/auth/LoginDialog.vue'"
echo "   import RegisterDialog from './components/auth/RegisterDialog.vue'"
echo ""
