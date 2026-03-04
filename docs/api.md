# API 文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`

## 接口列表

### 1. 健康检查

```
GET /api/health
```

**响应**:
```json
{
  "status": "ok",
  "message": "Server is running"
}
```

### 2. 获取支持的 AI 服务商

```
GET /api/providers
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "zhipu": {
      "name": "智谱AI",
      "base_url": "https://open.bigmodel.cn/api/paas/v4/",
      "models": ["glm-4", "glm-4-flash", "glm-4-plus"],
      "default_model": "glm-4-flash"
    },
    ...
  }
}
```

### 3. 上传文件

```
POST /api/upload
Content-Type: multipart/form-data
```

**请求参数**:
- `file`: Word 文档 (.docx)

**响应**:
```json
{
  "code": 0,
  "message": "File uploaded successfully",
  "data": {
    "file_id": "uuid",
    "filename": "论文.docx",
    "file_size": 12345,
    "file_size_formatted": "12.1 KB",
    "upload_time": "2024-01-01T12:00:00Z"
  }
}
```

### 4. 保存 API 配置

```
POST /api/config
```

**请求体**:
```json
{
  "provider": "zhipu",
  "api_key": "sk-xxxx",
  "model": "glm-4-flash",
  "enabled_checks": ["format", "language", "content", "citation"]
}
```

**响应**:
```json
{
  "code": 0,
  "message": "Configuration saved successfully",
  "data": {
    "session_id": "uuid",
    "provider": "zhipu",
    "model": "glm-4-flash",
    "enabled_checks": [...]
  }
}
```

### 5. 开始检查

```
POST /api/check
```

**请求体**:
```json
{
  "file_id": "uuid",
  "session_id": "uuid",
  "check_types": ["format", "ai"]
}
```

**响应**:
```json
{
  "code": 0,
  "message": "Check completed successfully",
  "data": {
    "check_id": "uuid",
    "status": "completed",
    "total_issues": 23
  }
}
```

### 6. 获取检查状态

```
GET /api/check/{check_id}/status
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "check_id": "uuid",
    "status": "completed",
    "format_check_status": "completed",
    "ai_check_status": "completed"
  }
}
```

### 7. 获取检查报告

```
GET /api/check/{check_id}/report
```

**响应**:
```json
{
  "code": 0,
  "data": {
    "check_id": "uuid",
    "file_id": "uuid",
    "file_name": "论文.docx",
    "status": "completed",
    "check_time": "2024-01-01T12:01:00Z",
    "format_check": {
      "status": "completed",
      "issues": [...],
      "issue_count": 15
    },
    "ai_check": {
      "status": "completed",
      "issues": [...],
      "issue_count": 8,
      "summary": {
        "total_issues": 8,
        "error_count": 2,
        "warning_count": 3,
        "suggestion_count": 3,
        "overall_evaluation": "论文整体质量较好..."
      }
    },
    "total_issues": 23
  }
}
```

### 8. 删除文件

```
DELETE /api/upload/{file_id}
```

**响应**:
```json
{
  "code": 0,
  "message": "File deleted successfully"
}
```

## 错误码

| 错误码 | 说明 |
|--------|------|
| 0 | 成功 |
| 1 | 通用错误 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |
