# Supabase Email Templates for Connet.AI

This document contains optimized email templates for Supabase authentication emails. Please copy these templates to your Supabase dashboard under Authentication > Email Templates.

## 1. Email Confirmation Template (注册验证邮件)

### Subject Line:
```
Welcome to Connet.AI - Please verify your email address
```

### HTML Template:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to Connet.AI</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .logo {
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: white;
        }
        .content {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .verification-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #10b981, #059669);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        h1 {
            font-size: 28px;
            margin: 0 0 16px 0;
            background: linear-gradient(135deg, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
            color: #cbd5e1;
            margin: 0 0 24px 0;
        }
        .cta-button {
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(139, 92, 246, 0.3);
            margin: 20px 0;
        }
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(139, 92, 246, 0.4);
        }
        .alternative-link {
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .alternative-link p {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .alternative-link a {
            color: #8b5cf6;
            word-break: break-all;
            text-decoration: none;
            font-size: 13px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer p {
            font-size: 14px;
            color: #64748b;
            margin: 8px 0;
        }
        .security-note {
            background: rgba(251, 191, 36, 0.1);
            border: 1px solid rgba(251, 191, 36, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }
        .security-note h3 {
            color: #fbbf24;
            font-size: 16px;
            margin: 0 0 8px 0;
        }
        .security-note p {
            color: #cbd5e1;
            font-size: 14px;
            margin: 0;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px 10px;
            }
            .header, .content {
                padding: 24px 20px;
            }
            h1 {
                font-size: 24px;
            }
            .cta-button {
                width: 100%;
                padding: 18px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Connet.AI</div>
            <h1>Welcome to the Future of AI Collaboration</h1>
            <p>You're just one click away from joining our AI-powered community</p>
        </div>

        <!-- Main Content -->
        <div class="content">
            <div class="verification-icon">✓</div>
            
            <h1>Verify Your Email Address</h1>
            
            <p>Thank you for joining Connet.AI! To complete your registration and start collaborating with AI agents, please verify your email address by clicking the button below.</p>
            
            <a href="{{ .ConfirmationURL }}" class="cta-button">
                🚀 Verify Email & Start Collaborating
            </a>
            
            <p>This verification link will expire in 24 hours for security reasons.</p>
            
            <!-- Security Note -->
            <div class="security-note">
                <h3>🔒 Security Notice</h3>
                <p>If you didn't create an account with Connet.AI, please ignore this email. Your email address will not be added to our platform.</p>
            </div>
            
            <!-- Alternative Link -->
            <div class="alternative-link">
                <p>Having trouble with the button? Copy and paste this link into your browser:</p>
                <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Connet.AI</strong> - Connecting the future, one interaction at a time</p>
            <p>Questions? Contact us at <a href="mailto:support@connet.ai" style="color: #8b5cf6;">support@connet.ai</a></p>
            <p style="font-size: 12px; color: #475569;">
                This email was sent to {{ .Email }}. 
                <br>© 2024 Connet.AI. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
```

## 2. Password Reset Template (密码重置邮件)

### Subject Line:
```
Reset your Connet.AI password
```

### HTML Template:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reset Your Password - Connet.AI</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .logo {
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: white;
        }
        .content {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .reset-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        h1 {
            font-size: 28px;
            margin: 0 0 16px 0;
            background: linear-gradient(135deg, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
            color: #cbd5e1;
            margin: 0 0 24px 0;
        }
        .cta-button {
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
            margin: 20px 0;
        }
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(245, 158, 11, 0.4);
        }
        .alternative-link {
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .alternative-link p {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .alternative-link a {
            color: #f59e0b;
            word-break: break-all;
            text-decoration: none;
            font-size: 13px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer p {
            font-size: 14px;
            color: #64748b;
            margin: 8px 0;
        }
        .security-note {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }
        .security-note h3 {
            color: #ef4444;
            font-size: 16px;
            margin: 0 0 8px 0;
        }
        .security-note p {
            color: #cbd5e1;
            font-size: 14px;
            margin: 0;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px 10px;
            }
            .header, .content {
                padding: 24px 20px;
            }
            h1 {
                font-size: 24px;
            }
            .cta-button {
                width: 100%;
                padding: 18px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Connet.AI</div>
            <h1>Password Reset Request</h1>
            <p>Let's get you back into your account</p>
        </div>

        <!-- Main Content -->
        <div class="content">
            <div class="reset-icon">🔑</div>
            
            <h1>Reset Your Password</h1>
            
            <p>We received a request to reset the password for your Connet.AI account. Click the button below to choose a new password.</p>
            
            <a href="{{ .ConfirmationURL }}" class="cta-button">
                🔒 Reset Password
            </a>
            
            <p>This password reset link will expire in 1 hour for security reasons.</p>
            
            <!-- Security Note -->
            <div class="security-note">
                <h3>🚨 Important Security Information</h3>
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged. Consider enabling two-factor authentication for added security.</p>
            </div>
            
            <!-- Alternative Link -->
            <div class="alternative-link">
                <p>Having trouble with the button? Copy and paste this link into your browser:</p>
                <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Connet.AI</strong> - Connecting the future, one interaction at a time</p>
            <p>Questions? Contact us at <a href="mailto:support@connet.ai" style="color: #f59e0b;">support@connet.ai</a></p>
            <p style="font-size: 12px; color: #475569;">
                This email was sent to {{ .Email }}. 
                <br>© 2024 Connet.AI. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
```

## 3. Email Change Confirmation Template (邮箱变更确认)

### Subject Line:
```
Confirm your new email address for Connet.AI
```

### HTML Template:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirm Email Change - Connet.AI</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e293b 0%, #334155 50%, #1e293b 100%);
            color: #ffffff;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .logo {
            width: 120px;
            height: 40px;
            margin: 0 auto 20px;
            background: linear-gradient(135deg, #8b5cf6, #3b82f6);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: white;
        }
        .content {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .change-icon {
            width: 80px;
            height: 80px;
            margin: 0 auto 30px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 36px;
        }
        h1 {
            font-size: 28px;
            margin: 0 0 16px 0;
            background: linear-gradient(135deg, #ffffff, #cbd5e1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        p {
            font-size: 16px;
            line-height: 1.6;
            color: #cbd5e1;
            margin: 0 0 24px 0;
        }
        .cta-button {
            display: inline-block;
            padding: 16px 32px;
            background: linear-gradient(135deg, #3b82f6, #1d4ed8);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3);
            margin: 20px 0;
        }
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 32px rgba(59, 130, 246, 0.4);
        }
        .alternative-link {
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .alternative-link p {
            font-size: 14px;
            color: #94a3b8;
            margin-bottom: 12px;
        }
        .alternative-link a {
            color: #3b82f6;
            word-break: break-all;
            text-decoration: none;
            font-size: 13px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
        }
        .footer p {
            font-size: 14px;
            color: #64748b;
            margin: 8px 0;
        }
        .security-note {
            background: rgba(59, 130, 246, 0.1);
            border: 1px solid rgba(59, 130, 246, 0.2);
            border-radius: 12px;
            padding: 20px;
            margin: 30px 0;
        }
        .security-note h3 {
            color: #3b82f6;
            font-size: 16px;
            margin: 0 0 8px 0;
        }
        .security-note p {
            color: #cbd5e1;
            font-size: 14px;
            margin: 0;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px 10px;
            }
            .header, .content {
                padding: 24px 20px;
            }
            h1 {
                font-size: 24px;
            }
            .cta-button {
                width: 100%;
                padding: 18px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">Connet.AI</div>
            <h1>Email Address Change</h1>
            <p>Confirm your new email address</p>
        </div>

        <!-- Main Content -->
        <div class="content">
            <div class="change-icon">📧</div>
            
            <h1>Confirm Your New Email</h1>
            
            <p>You've requested to change your email address. To complete this change and ensure you continue receiving important updates, please confirm your new email address.</p>
            
            <a href="{{ .ConfirmationURL }}" class="cta-button">
                ✅ Confirm New Email
            </a>
            
            <p>This confirmation link will expire in 24 hours for security reasons.</p>
            
            <!-- Security Note -->
            <div class="security-note">
                <h3>📋 What happens next?</h3>
                <p>After confirming, this email address will become your primary contact for your Connet.AI account. All future communications will be sent here.</p>
            </div>
            
            <!-- Alternative Link -->
            <div class="alternative-link">
                <p>Having trouble with the button? Copy and paste this link into your browser:</p>
                <a href="{{ .ConfirmationURL }}">{{ .ConfirmationURL }}</a>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p><strong>Connet.AI</strong> - Connecting the future, one interaction at a time</p>
            <p>Questions? Contact us at <a href="mailto:support@connet.ai" style="color: #3b82f6;">support@connet.ai</a></p>
            <p style="font-size: 12px; color: #475569;">
                This email was sent to {{ .Email }}. 
                <br>© 2024 Connet.AI. All rights reserved.
            </p>
        </div>
    </div>
</body>
</html>
```

## 使用说明

### 在Supabase中更新邮件模板的步骤：

1. **登录Supabase Dashboard**
2. **导航到项目设置**：Settings → Authentication
3. **找到Email Templates部分**
4. **选择相应的模板类型**：
   - Confirm signup (注册确认)
   - Reset password (密码重置)  
   - Change email address (邮箱变更)
5. **复制上面对应的HTML代码**到Body字段
6. **更新Subject Line**使用上面提供的主题行
7. **保存更改**

### 模板特性：

- 🎨 **响应式设计**：支持桌面和移动设备
- 🌙 **深色主题**：与Connet.AI品牌风格一致
- 🔒 **安全提示**：包含安全注意事项
- 📱 **移动友好**：在所有设备上显示完美
- 🎭 **品牌一致性**：使用Connet.AI的视觉元素
- ⚡ **快速加载**：优化的CSS和HTML结构
- 🌐 **可访问性**：遵循邮件可访问性标准

### 可用变量：

Supabase提供以下变量用于邮件模板：
- `{{ .ConfirmationURL }}` - 确认链接
- `{{ .Email }}` - 用户邮箱
- `{{ .SiteURL }}` - 网站URL
- `{{ .RedirectTo }}` - 重定向URL（如果设置）

这些模板将为用户提供专业、现代且与品牌一致的邮件体验。