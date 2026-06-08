# MCP Server 配置指南

## 添加 MCP Server

### HTTP Streamable MCP Server

```bash
# 交互式添加
hermes mcp add NAME --url https://example.com/mcp

# 自动确认添加
echo "Y" | hermes mcp add NAME --url https://example.com/mcp
```

### 命令型 MCP Server

```bash
# 使用本地命令
hermes mcp add NAME --command "path/to/mcp/server"

# 带参数
hermes mcp add NAME --command "python /path/to/server.py --config /path/to/config.json"
```

### 文件型 MCP Server

```bash
# 使用 MCP 配置文件
hermes mcp add NAME --file "/path/to/mcp.json"
```

## 启用/禁用 MCP 工具

```bash
# 查看已配置的 MCP Server
hermes mcp list

# 启用所有工具
hermes mcp configure NAME

# 禁用所有工具
hermes mcp configure NAME --disable-all

# 选择特定工具
hermes mcp configure NAME --select TOOL1 TOOL2

# 查看工具状态
hermes mcp test NAME
```

## 配置示例

### 中文文档 MCP Server

```yaml
# config.yaml
mcp_servers:
  hermes-cn:
    url: https://mcp.hermesagent.org.cn/v1
    tools:
      - search_docs
      - get_doc
      - list_recent_releases
```

### 本地开发工具

```bash
# 添加本地代码检查工具
hermes mcp add code-checker --command "/path/to/eslint"
hermes mcp configure code-checker --select check lint format
```

## 配置验证

```bash
# 检查 MCP Server 连接
hermes mcp test NAME

# 查看工具列表
hermes mcp list

# 查看配置文件
cat ~/.hermes/config.yaml | grep -A 20 mcp
```

## 故障排除

### 连接失败

```bash
# 检查 URL
curl -I https://example.com/mcp

# 检查认证需求
# 如果提示需要 API key，取消确认
echo "n" | hermes mcp add NAME --url URL
```

### 工具未启用

```bash
# 启用所有工具
hermes mcp configure NAME

# 或选择特定工具
hermes mcp configure NAME --select TOOL1 TOOL2
```

### 会话后不生效

```bash
# 需要重启会话
hermes mcp reload

# 或重新运行
hermes /reset
```

## 最佳实践

1. **先测试后启用**：使用 `hermes mcp test` 验证连接
2. **逐步启用工具**：不要一次性启用所有工具
3. **记录配置**：在 `references/` 目录保存配置模板
4. **定期清理**：移除不再使用的 MCP Server

## 参考资料

- [Hermes Agent MCP 文档](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
- [MCP 配置参考](https://hermes-agent.nousresearch.com/docs/reference/mcp)