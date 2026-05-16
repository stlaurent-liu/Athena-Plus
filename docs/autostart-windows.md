# Athena-Plus 开机自启设置指南

## 自动启动说明
Athena-Plus 默认就是 `mcp-server` 模式，开机启动后，云端Gabriel随时可以通过MCP调用操作你的电脑，不需要你手动启动。

## 设置开机自启步骤（计划任务方式，推荐）

### 1. 创建计划任务
1. 按 `Win + R` 输入 `taskschd.msc` 回车，打开任务计划程序
2. 右边点击"创建基本任务"
3. 名称输入 `Athena-Plus MCP Server`，描述输入 `开机自动启动Athena MCP服务供云端Gabriel调用`，下一步
4. 触发器选择"当计算机启动时"，下一步
5. 操作选择"启动程序"，下一步
6. 点击"浏览"，选择：
   ```
   C:\Users\laure\Desktop\Gabriel Domain\Athena-Plus\scripts\start-mcp-server.bat
   ```
7. 点击"下一步" → "完成"

### 2. 设置隐藏运行（推荐）
1. 在任务计划程序库中找到刚创建的 `Athena-Plus MCP Server`
2. 右键 → 属性
3. 切换到"设置"选项卡，勾选"唤醒计算机运行此任务"（可选）
4. 切换到"常规"选项卡，勾选"不管用户是否登录都要运行"
5. 勾选"使用最高权限运行"（有些操作需要管理员权限）
6. 确定，输入你的Windows密码确认

### 3. 测试
1. 点击右键 → 运行
2. 打开任务管理器，看有没有 `python` 进程在运行
3. 云端Gabriel会ping一下测试连接

## 验证连接
云端Gabriel会自动测试连接，成功后就可以随时调用工具了。

## 如何取消开机自启
打开任务计划程序，删除 `Athena-Plus MCP Server` 任务即可。

## 日志
运行日志保存在：
```
C:\Users\laure\Desktop\Gabriel Domain\Athena-Plus\data\athena-mcp.log
```
如果出问题，查看这个日志。
