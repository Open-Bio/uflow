# uFlow 命令行执行快速参考

## 基本命令

```bash
uv run .\uflow\pyflow_run.py .\untitled.pygraph
```

## 必需条件

1. **graphInputs 节点** - 手动在图形编辑器中添加
2. **执行引脚** - 在 graphInputs 节点中添加 ExecPin 输出并连接到目标节点

## 常见错误

- `The file doesn't contain graphInputs nodes` → 添加 graphInputs 节点
- 没有执行控件 → 添加 ExecPin 并连接

## 成功标志

- 控制台显示包加载信息
- 弹出参数配置对话框
- 生成输出文件
