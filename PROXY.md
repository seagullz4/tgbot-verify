# SOCKS5 代理配置说明

## 概述

本项目支持使用 SOCKS5 代理进行 SheerID 验证请求。当配置代理后，系统会自动从代理池中随机选择一个代理进行请求。

## 配置方法

### 1. 创建代理文件

创建一个文本文件（如 `proxies.txt`），每行一个代理，支持以下格式。你可以参考项目中的 `proxies.txt.example` 文件。

```
# 带认证的代理
socks5://username:password@host:port

# 不需要认证的代理
socks5://host:port
```

**示例：**

```
# 代理示例文件
socks5://user1:pass123@proxy1.example.com:1080
socks5://user2:pass456@proxy2.example.com:1080
socks5://192.168.1.100:1080
socks5://10.0.0.1:1080
```

**注意事项：**
- 以 `#` 开头的行会被忽略（注释行）
- 空行会被忽略
- 每个代理必须是有效的 SOCKS5 代理地址
- 代理地址格式必须以 `socks5://` 开头
- 如果代理 URL 格式不正确，将在日志中显示警告并跳过该代理
- **重要**：用户名和密码中不应包含 `@` 字符。如需使用特殊字符，请使用 URL 编码（如 `%40` 代替 `@`）

### 2. 配置环境变量

在 `.env` 文件中添加代理文件路径：

```env
PROXY_FILE_PATH=/path/to/proxies.txt
```

或使用相对路径（相对于项目根目录）：

```env
PROXY_FILE_PATH=./proxies.txt
```

### 3. 重启机器人

修改配置后，需要重启机器人使配置生效：

```bash
# 如果是直接运行
python bot.py

# 如果是 Docker 部署
docker-compose restart
```

## 工作原理

1. **初始化**：机器人启动时会读取代理文件，将所有有效代理加载到内存中
2. **随机选择**：每次执行验证时，系统会从代理池中随机选择一个代理
3. **自动应用**：选中的代理会自动应用到 HTTP 请求中
4. **日志记录**：使用的代理会在日志中显示（出于安全考虑，密码会被隐藏）

## 代理要求

- **类型**：必须是 SOCKS5 代理
- **稳定性**：建议使用稳定可靠的代理，避免验证失败
- **速度**：代理速度会影响验证时间，建议使用低延迟代理
- **地区**：建议使用美国或其他英语国家的代理

## 不使用代理

如果不配置 `PROXY_FILE_PATH` 或代理文件为空，系统会使用直连方式进行请求。

## 故障排除

### 代理加载失败

**问题**：日志显示 "代理文件不存在" 或 "加载代理文件失败"

**解决方案**：
1. 检查文件路径是否正确
2. 确认文件存在且有读取权限
3. 检查文件编码是否为 UTF-8

### 验证失败

**问题**：使用代理后验证经常失败

**解决方案**：
1. 测试代理是否可用
2. 检查代理速度和稳定性
3. 尝试更换其他代理
4. 查看日志中的详细错误信息

### 代理格式错误

**问题**：代理无法正常工作

**解决方案**：
1. 确认代理格式符合规范：`socks5://[user:pass@]host:port`
2. 检查是否有多余的空格或特殊字符
3. 确认端口号是否正确

## 安全建议

1. **不要将代理文件提交到 Git**：在 `.gitignore` 中添加代理文件
2. **保护代理凭据**：代理文件可能包含敏感的用户名和密码
3. **定期更新**：定期检查和更新代理列表
4. **避免公开代理**：免费公开代理可能不稳定且存在安全风险

## 示例配置

完整的配置示例：

**proxies.txt：**
```
# 主代理服务器
socks5://user1:password1@proxy1.example.com:1080

# 备用代理服务器
socks5://user2:password2@proxy2.example.com:1080

# 本地代理
socks5://127.0.0.1:1080
```

**.env：**
```env
# Telegram Bot 配置
BOT_TOKEN=YOUR_BOT_TOKEN_HERE
ADMIN_USER_ID=123456789

# MySQL 配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=tgbot_user
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=tgbot_verify

# 代理配置
PROXY_FILE_PATH=./proxies.txt
```

**.gitignore：**
```
.env
proxies.txt
*.log
```

## 技术细节

- 使用 `httpx` 库的代理支持
- 线程安全的代理管理器
- 支持动态重载代理列表（需要重启）
- 每个验证请求独立使用一个随机代理
