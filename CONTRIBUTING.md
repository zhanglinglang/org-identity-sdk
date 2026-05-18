# 贡献指南

感谢你对 org-identity-sdk 的关注！

## 参与方式

- 🐛 **Bug 报告**: 通过 [GitHub Issues](https://github.com/lingzhu-ai/org-identity-sdk/issues) 提交
- 💡 **功能建议**: 在 Issues 发起讨论
- 🔧 **代码贡献**: Fork → Branch → PR
- 📖 **文档改进**: README、Wiki、中文翻译

## 开发环境

```bash
git clone https://github.com/lingzhu-ai/org-identity-sdk.git
cd org-identity-sdk
pip install -e ".[dev]"
```

## 代码规范

- Python 3.9+
- 使用 [ruff](https://github.com/astral-sh/ruff) 格式化
- 新增功能需附带测试
- 测试通过后再提交 PR

## 提交信息格式

```
<type>: <description>

类型:
  feat     新功能
  fix      修复
  docs     文档
  test     测试
  refactor 重构
  chore    杂项
```

## 协议规范贡献

对 ATH 协议 Schema 的修改请走 RFC 流程:
1. 在 Issues 发起 RFC 提案
2. 社区讨论 ≥ 1 周
3. 核心团队 Review
4. 合并并发布新协议版本

## 行为准则

- 尊重每一位贡献者
- 建设性的技术讨论
- 以开放姿态接受不同意见
