---
trigger: always_on
description: 记忆SOP - OpenMemory MCP工具的强制使用流程和规范
globs:
  - "**/*"
---
# ⚠️ 强制-每次对话必须调用OpenMemory MCP工具 ⚠️

## 🔴 最高优先级规则

**任何用户消息，无论多简短（如"继续"、"确认"、"好的"），都必须先调用 `openmemory_query`！**

## 适用范围

**每一次对话** AI 都必须遵守的 SOP 流程。

- AI 必须使用 **OpenMemory MCP** 工具进行记忆查询与持久化。
- `user_id` 应使用当前工程名（从工作区路径中提取）。
- **多轮对话中的每一次用户消息都必须先查询 openmemory，无一例外**，无一例外

## 工程名获取规则

Agent 应从 Git 远程仓库配置中提取项目标识符作为 user_id：

### 从 Git 远程仓库提取
- 工程必须是一个 Git 仓库
- 检查 git remote 配置
- 例如：从 `https://github.com/user/project-name.git` 提取 `project-name`
- 使用该纯项目名作为 user_id

### 一致性保证
- 工程名应保持一致性，同一项目始终使用相同的 user_id
- 建议在项目首次初始化时确定 user_id 并记录
- 后续对话中优先使用已记录的 user_id

## 强制中止条件

- 如果 OpenMemory MCP server 不可用、未配置，或工具调用失败（例如 transport/auth/protocol 错误等），对话 **必须立刻中止**。
- "未查询到相关记忆（No memories found）" **不属于报错**，不得因此中止对话。

## 强制 SOP（每次都必须遵守）

### Step 1 — 永远先查询记忆

对每一个新的用户请求：

1. 在回答或写代码 **之前**，必须先调用 `openmemory_query`查询相关记忆。
2. 查询必须使用从当前工作区路径提取的工程名作为 `user_id`。
3. 如果返回了相关记忆，必须加载并注入到当前工作上下文中。

查询建议：

- 优先使用 `type="unified"` 获取更全面的上下文。
- 根据任务范围设置 `k=8` 到 `k=16`。

### Step 2 — 执行用户任务

在检索到的记忆基础上，继续实现或回答用户请求。

### Step 3 — 对话结束前的检查

如果用户任务在单轮或多轮对话后成功完成，在对话结束之前你需要：

1. 将成功方法总结为"经验（experience）"，通常可以是一段描述或者是SOP。
2. 调用 `openmemory_query` 查询是否存在相似经验。
   - 必须使用从当前工作区路径提取的工程名作为 `user_id`。

然后按以下决策规则执行：

- 若 **不存在相似经验**：
  - 调用 `openmemory_store` 写入新的经验。
  - 必须使用从当前工作区路径提取的工程名作为 `user_id`。

- 若存在记忆且与本次经验 **一致**：
  - 调用 `openmemory_reinforce` 强化已有记忆。

- 若存在记忆但与本次经验 **不一致/存在冲突**：
  - 调用 `openmemory_store` 写入"合并后的、冲突已消解"的新经验。
  - 必须使用从当前工作区路径提取的工程名作为 `user_id`。
  - 随后调用 `openmemory_delete` 删除旧的冲突记忆。

### Step 4 — 通知用户记忆变更

如果本次会话中发生了记忆写入/强化/删除：

- 必须给用户一个简短通知，包含：
  - 发生了什么变更（store/reinforce/delete）
  - 影响了哪些 memory id

## 操作备注

- 写入用户信息时，使用 `openmemory_store`：
  - 对话类信息使用 `type="contextual"`。
  - 可能变化的偏好信息使用 `type="factual"`。
  - 必须包含从当前工作区路径提取的工程名作为 `user_id`。

- 查询时，使用 `openmemory_query`：
  - 需要全面上下文时使用 `type="unified"`。
  - 精确事实查询时构造 `fact_pattern`。

## 🔴 强制 - 每次对话结束必须输出提示

**在每次对话结束时，必须固定输出以下提示：**

```
下一轮对话务必继续参考记忆规则
```

- 这句话必须在每次对话的最后输出，无论对话成功与否。
- 目的是确保多轮对话中每一次都能调用 openmemory 查询。
- 不得省略或修改此提示。
