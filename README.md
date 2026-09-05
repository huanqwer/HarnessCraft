# HarnessCraft

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一套完整的 Harness 工程化落地实践——不只是文章，更包含可直接使用并经过实际验证的 Skills、Rules、Workflows、Memories 和工程结构。

通过这个项目你可以了解到：

- 从零开始构建一个 AI Harness Coding 商业化项目的全流程和要素
- Harness Coding 成本控制方法
- 必要的 AI Harness Coding 基础知识
- 可能未来 AI Coding 的标准范式
- 很多可直接使用并且经过实际验证的 Skills、Rules、Workflows

适合人群

* 想学习 Harness Coding 的同学
* 想 Harness 出商业化应用而非小 Demo 的初创公司或者 OPC
* 想要了解 AI 时代下传统软件应用架构转型的架构师



## 项目结构

```
HarnessCraft/
├── posts/              # 系列文章（平铺，不按章节分组）
├── .devin/             # 工程化落地实践
│   ├── skills/         # 可复用 Skills（配图、任务执行、反思等）
│   ├── rules/          # 全局规则（Rollback、记忆、反思等）
│   └── ...
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

> `.devin/` 目录是本项目的工程化核心，包含实际开发中使用的 Skills、Rules、Workflows 和 Memories。这些不是示例代码，而是真实生产环境中验证过的 Harness 组件。



## 背景

自2025年5月中旬开始

我就开始了我的Harness Coding科研之旅（当时这套方法论还被称为Vibe Coding）

那时候还没有现在炒的很火的Harness工程

但是回过头来发现我不断优化和Agent交互的过程其实和Harness如出一辙

期间Harness Coding了不少项目

做了不少创新性的尝试

得益于模型参数规模的增长

以及不断完善的Harness Coding工具集和方法论

AI在Harness Coding的表现中越来越稳定

其中一个项目在历经了约8个月的Harness Coding后代码量达到了接近50万行

![image-20260518111145648](https://res.cloudinary.com/isieghiq/image/upload/v1787445811/harnesscraft/403bbdd9d0e86a5defd7575ebbc8200b4874af3b.png)

并且上线后已稳定运行了约半年的时间

所以想要将现有的方法论总结一下

一个是方便自己启动新项目的时候能快速boot

另一个则是造福他人



## 设计思想：ISIER 五层 Harness 落地架构

在长期与 Agent 协作的过程中，作者沉淀出一套可复用的 Harness 落地架构，简称 **ISIER**（Implement of Harness，取自五层首字母）：

- **I** — Intent 意图层
- **S** — Spec 契约层
- **I** — Impl 执行层
- **E** — Eval 验收层
- **R** — Refl 反思层

ISIER 描述了一个任务从"用户意图"到"反思归档"的完整主线流程，每一层是前一层的下游。**Rollback 不作为独立一层，而是贯穿五层的横切原则**——任意一层失败时都需要有可执行的安全网。

![ISIER 五层 Harness 落地架构](https://res.cloudinary.com/isieghiq/image/upload/v1787445815/harnesscraft/6b3d61a533f27f6eb273466f258171f17152cfdd.png)

### Intent 意图层

识别用户意图，通过标准化模板和模糊部分的反复确认，最后为用户的意图生成标准的 Spec 和 Plan。

### Spec 契约层（基于 SDD 和 TDD 思想）

根据上述已明确的用户意图，生成 Spec 标准化的文档，以及 Agent 执行完毕后的验收清单、测试用例等。

### Impl 执行层

根据 Plan、Spec 等上述生成的文档，结合开发态时的上下文注入（Rules、Skills、MCPs、Memories 等），开始执行任务，生成 Todos、SubAgents、基于 ReAct 不断修正任务，执行完成后进行冒烟测试。

> ⚠️ **硬约束：任何任务执行之前必须要有 Rollback 方案。**
> 无 Rollback 方案，或存在多个互相冲突的 Rollback 方案时，必须 STOP 并向用户确认，不得擅自推进。这是 `fallback-first` 规则的核心要求。

### Eval 验收层

根据上述的验收清单、测试用例等，开始自我测试，同时通知用户验收，如果不满意则根据用户的最新反馈，反哺并 loop 前四步。

### Refl 反思层

用户验收后，开始自动执行反思，反思具体工作为：更新 Agent 上下文，保证 Agent 时时刻刻在最新的 Runtime 中，为上述任务生成带版本号的归档文档，并针对期间发现的问题完善我们的整个 Harness 环境，存储各种类型的记忆（长短期记忆、用户偏好、场景记忆、事实记忆等）。

### Rollback 横切原则（贯穿 ISIER 全层）

Rollback 不是流程节点，而是保障 ISIER 安全执行的横切机制，在每一层都有对应职责：

| 层级 | Rollback 职责 |
|------|---------------|
| Intent | 识别风险任务，初步评估回滚必要性 |
| Spec | 定义验收标准时同步定义回滚标准（什么算失败、回滚到哪个状态） |
| Impl | 执行前必须确认 Rollback 方案存在（fallback-first 硬约束） |
| Eval | 验收失败时触发 Rollback |
| Refl | 反思 Rollback 是否有效，沉淀回滚经验 |

![Harness 任务执行流程](https://res.cloudinary.com/isieghiq/image/upload/v1787445818/harnesscraft/eb6d5a31b07882bc303534ababc6c197434a2912.png)

## 实践案例：5 人团队 0 手写代码

本 Harness 方法论已应用于博主所在 5 人开发团队：

- **强制要求全员使用提示词工程在 Harness 架构下开发**
- **0 手写代码**，所有代码由 Agent 在 Harness 约束下生成
- 截至 **2026-08-23**：
  - 已完成 **2 个项目**的开发
  - 另有 **3 个商用项目**立项

![用户与 Agent 协作旅程](https://res.cloudinary.com/isieghiq/image/upload/v1787445822/harnesscraft/eed2c7887a86a1f486a649b12a0a71a038178d67.png)

实践证明，在完善的 Harness 约束下，团队无需手写代码即可稳定交付商业级项目，开发者角色从"代码编写者"转变为"Harness 设计者与提示词工程师"。



## 系列文章

所有文章平铺在 `posts/` 目录下，推荐按以下顺序阅读：

| 序号 | 文章 | 主题 |
|------|------|------|
| 1 | [如何选择自己称手的VibeCoding「兵器」](posts/如何选择自己称手的VibeCoding「兵器」.md) | 工具选择 |
| 2 | [我自研的Harness五层架构原理](posts/我自研的Harness五层架构原理.md) | 核心思想 |
| 3 | [如何让AI设计出优秀的产品](posts/如何让AI设计出优秀的产品.md) | 产品设计 |
| 4 | [前端总跑偏？针对前端工程师的Harness](posts/前端总跑偏？针对前端工程师的Harness.md) | 前端 |
| 5 | [架构思维于Harness的重要性](posts/架构思维于Harness的重要性.md) | 后端架构 |
| 6 | [AI自验证并纠错通宵跑完任务，我只负责验收](posts/AI自验证并纠错通宵跑完任务，我只负责验收.md) | 后端实践 |
| 7 | [测试工程师借助AI不完全摸鱼指南](posts/测试工程师借助AI不完全摸鱼指南.md) | 测试 |
| 8 | [通用上线skill，让AI帮你部署和运维](posts/通用上线skill，让AI帮你部署和运维.md) | 运维 |
| 9 | [优秀的AI应用工程师需要学会白嫖Token的技巧](posts/优秀的AI应用工程师需要学会白嫖Token的技巧.md) | 成本控制 |
| 10 | [别人的AI为什么越来越好用](posts/别人的AI为什么越来越好用.md) | 自我进化 |
| 11 | [看看真实企业内部的Harness+FDE改造如何落地的](posts/看看真实企业内部的Harness+FDE改造如何落地的.md) | 最佳实践 |

> 文章正文均由作者手写，配图由 Agent 在配图阶段统一生成技术图表并插入。如果你对文章中提到的 Skills、Rules、Workflows 感兴趣，可以直接查看 `.devin/` 目录下的工程化实现。



## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详情。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目主页：https://github.com/huanqwer/HarnessCraft
- 我的邮箱：huanqwer0314@gmail.com
