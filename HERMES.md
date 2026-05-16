# Athena-Plus 全栈开发规范

## META
- agent: gabriel-hermes
- scenario: standard
- stack: python
- generated: 2026-05-14
- scale_version: 10.0-windows
- doc: HERMES.md

## COMMANDS
dev: python main.py
test: pytest
lint: flake8
typecheck: mypy .

## TECH_STACK
- Python 3.10+
- FastAPI
- PyWebView
- MCP (Model Context Protocol)
- Ollama
- SQLite
- Pydantic

## AGENT_CAPABILITY
- support_level: experimental
- memory_files: HERMES.md
- config_files: scale-hermes-config.json
- hooks: supported
- mcp: native-supported

## CODE_RULES
[ENFORCED] 禁止空 catch 块
[ENFORCED] 禁止硬编码密钥、token、password、private key
[ENFORCED] Python 代码类型提示必须完整，通过 mypy 检查
[ENFORCED] 遵循 PEP8 编码规范
[ENFORCED] Windows 路径处理必须使用 pathlib，避免硬编码分隔符

## KARPATHY_PRINCIPLES
[K1-THINK] 编码前必须明确列出假设，不确定时停下来提问而非猜测
[K1-THINK] 存在多种解释时必须呈现所有选项，不得默默选择一种
[K1-THINK] 存在更简单方案时必须提出异议
[K2-SIMPLE] 禁止添加未要求的功能、抽象、灵活性或可配置性
[K2-SIMPLE] 如果 200 行可写 50 行，必须重写——资深工程师检验标准
[K2-SIMPLE] 禁止为不可能场景添加错误处理
[K3-SURGICAL] 每一行修改都必须可追溯到用户请求——无关改动零容忍
[K3-SURGICAL] 禁止"顺手"重构、改格式、加类型标注、改注释
[K3-SURGICAL] 匹配现有代码风格，即使你更倾向不同写法
[K4-GOAL] 必须将命令式任务转化为可验证目标：测试先行→实现→验证
[K4-GOAL] 多步任务必须声明计划：1. [步骤] → 验证: [检查]
[K4-GOAL] 成功标准必须明确——弱标准（"让它工作"）需要不断澄清

## WORKFLOW
- mode: standard
- step_1: 探索 → 读知识文档 + 扫代码 + 找验证命令
- step_2: 规划 → 影响分析 + 契约定义 + 回滚思考
- step_3: 执行 → RED/GREEN/REFACTOR
- step_4: 验证 → 运行真实命令，不用脑补结果
- step_5: 交付 → 列出完成内容、验证结果、未验证项

## GATES (Windows Edition)
- G1: 探索完成 → 已读文件、命令或测试证据可追溯
- G2: 规划完成 → 计划包含边界、风险、验证方式
- G3: TDD 合规 → 测试先行或说明不适用原因
- G4: Lint 通过 → flake8 exit code = 0
- G5: 测试通过 → pytest exit code = 0
- G6: 类型通过 → mypy exit code = 0
- G7: 安全检查 → 无密钥、危险删除、未授权数据变更

## SKILLS
- graphify: Graphify — Use when 项目结构复杂时.
- systematic-debugging: Systematic Debugging (Superpowers) — Use when 修复bug连续2次失败.
- freeze-guard: Freeze Guard (gstack) — Use when 执行阶段开始前.
- tdd: TDD (Superpowers) — Use when 写任何新代码时.
- verification: Verification (Superpowers) — Use when 声称完成前必须验证.
- review: Review (gstack) — Use when 提交PR前.

## MACHINE_CHECKS (Windows PowerShell)
- must_run: powershell scripts/validate-config.ps1
- must_run: pytest tests/
- must_run: .\scripts\gates\all.ps1 -DryRun
- never_claim_passed_without_exit_code_0: true

## HONEST_DELIVERY
- 未运行测试时禁止说"测试通过"
- 门控失败时禁止说"已完成"
- 工具缺失或命令跳过时必须列为"未验证项"
- 最终回复必须包含：完成内容、验证结果、未验证项

## VERIFICATION_CRITERIA
- VC1: diff 中只有请求的改动——无关改动零容忍
- VC2: 代码第一次就简洁——无需因过度复杂而重写
- VC3: 澄清问题在实现之前提出——不是犯错之后
- VC4: 每步修改附带验证——不靠脑补结果

## RED_LINES
- R1: 不确定事实必须标注 [UNCERTAIN]
- R2: 禁止编造文件、命令输出、测试结果
- R3: 禁止写入 .env*、密钥、证书、token 文件
- R4: 声称环境问题前必须给出证据

<!-- SCALE OS v10.0-Windows · HERMES.md · project-specific -->
