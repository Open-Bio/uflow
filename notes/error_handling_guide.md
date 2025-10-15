# uflow 节点错误处理指南

## 概述

本文档说明如何在uflow节点中正确实现错误处理，确保执行错误的节点能够显示红色边框提示。

## 错误显示机制

### 视觉提示

- **红色虚线边框**: 错误节点会显示红色虚线边框
- **错误tooltip**: 悬停在错误节点上显示错误信息
- **Logger输出**: 错误信息会记录到系统日志中

### 实现原理

1. 节点错误状态由 `NodeBase._lastError` 控制
2. `NodeBase.isValid()` 返回 `self._lastError is None`
3. `Painters.py` 在 `not node.isValid()` 时绘制红色虚线边框
4. UI通过 `errorOccurred` 信号更新显示

## 错误处理方式

### 1. 类继承节点 (NodeBase子类)

在类继承的节点中，直接调用 `setError()` 方法：

```python
class MyNode(NodeBase):
    def compute(self, *args, **kwargs):
        try:
            # 执行逻辑
            result = self.perform_calculation()
            self.output_pin.setData(result)
        except Exception as e:
            self.setError(f"计算错误: {str(e)}")
```

### 2. 函数库节点 (@IMPLEMENT_NODE装饰)

在函数库节点中，**抛出异常**会自动触发错误状态：

```python
@staticmethod
@IMPLEMENT_NODE(returns=None, nodeType=NodeTypes.Pure)
def MyFunction(data=('DataFramePin', None), result=(REF, ('DataFramePin', None))):
    """我的节点函数"""
    if data is None or data.empty:
        raise ValueError("数据为空")
    
    if 'required_column' not in data.columns:
        raise ValueError("缺少必需列 'required_column'")
    
    # 执行逻辑
    processed_data = data.dropna()
    result(processed_data)
```

## 常见错误处理模式

### 输入验证

```python
# 检查必需输入
if not input_data:
    raise ValueError("输入数据不能为空")

# 检查数据类型
if not isinstance(input_data, pd.DataFrame):
    raise TypeError("输入必须是DataFrame类型")

# 检查列是否存在
if column_name not in data.columns:
    raise ValueError(f"列 '{column_name}' 不存在")
```

### 文件操作

```python
# 检查文件路径
if not path or not path.strip():
    raise ValueError("文件路径为空")

# 检查文件是否存在
if not os.path.exists(path):
    raise FileNotFoundError(f"文件不存在: {path}")
```

### 数据验证

```python
# 检查DataFrame是否为空
if data.empty:
    raise ValueError("DataFrame为空")

# 检查数值范围
if value < 0 or value > 100:
    raise ValueError("数值必须在0-100之间")

# 检查列表是否为空
if not value_list:
    raise ValueError("值列表不能为空")
```

## 错误类型选择

### ValueError

用于参数值不正确的情况：

```python
raise ValueError("列名不能为空")
raise ValueError("数值超出有效范围")
```

### TypeError

用于类型不匹配的情况：

```python
raise TypeError("输入必须是字符串类型")
```

### FileNotFoundError

用于文件不存在的情况：

```python
raise FileNotFoundError("文件不存在")
```

### KeyError

用于键不存在的情况：

```python
raise KeyError("配置项不存在")
```

## 最佳实践

### 1. 错误信息要清晰

```python
# 好的错误信息
raise ValueError(f"列 '{column_name}' 在DataFrame中不存在")

# 避免模糊的错误信息
raise ValueError("错误")
```

### 2. 在合适的时机检查

```python
def process_data(data, column_name):
    # 在函数开始就验证输入
    if data is None:
        raise ValueError("数据不能为None")
    
    if column_name not in data.columns:
        raise ValueError(f"列 '{column_name}' 不存在")
    
    # 然后执行处理逻辑
    return data[column_name]
```

### 3. 避免捕获所有异常

```python
# 好的做法 - 捕获特定异常
try:
    result = risky_operation()
except ValueError as e:
    raise ValueError(f"数值错误: {e}")
except FileNotFoundError as e:
    raise FileNotFoundError(f"文件错误: {e}")

# 避免的做法 - 捕获所有异常
try:
    result = risky_operation()
except Exception as e:
    print(f"错误: {e}")  # 这样不会显示红色边框
```

### 4. 使用具体的异常类型

```python
# 好的做法
if not path:
    raise ValueError("路径不能为空")

# 避免的做法
if not path:
    raise Exception("路径不能为空")
```

## 调试技巧

### 1. 检查节点状态

在节点执行后，可以通过以下方式检查错误状态：

```python
# 在节点中
print(f"节点是否有效: {self.isValid()}")
print(f"错误信息: {self.getLastErrorMessage()}")
```

### 2. 查看错误日志

错误信息会输出到uflow的日志系统中，可以在控制台或日志文件中查看。

### 3. 测试错误场景

创建测试用例验证错误处理：

```python
# 测试空数据
node.setData(None)
node.execute()
assert not node.isValid()

# 测试无效列名
node.setColumnName("nonexistent_column")
node.execute()
assert not node.isValid()
```

## 常见问题

### Q: 为什么我的节点出错但没有显示红色边框？

A: 检查是否正确抛出了异常，而不是只打印错误信息。

### Q: 如何清除节点的错误状态？

A: 调用 `clearError()` 方法或确保下次执行成功。

### Q: 错误信息在哪里显示？

A: 错误信息会显示在节点的tooltip中，也会记录到系统日志。

### Q: 可以自定义错误显示样式吗？

A: 可以修改 `Painters.py` 中的绘制逻辑来自定义错误显示样式。

## 示例代码

### 完整的数据处理节点示例

```python
@staticmethod
@IMPLEMENT_NODE(returns=None, nodeType=NodeTypes.Pure,
                meta={NodeMeta.CATEGORY: 'Data Processing'})
def ProcessData(data=('DataFramePin', None),
                column_name=('StringPin', ""),
                operation=('StringPin', "sum"),
                result=(REF, ('DataFramePin', None))):
    """数据处理节点示例"""
    
    # 输入验证
    if data is None or data.empty:
        raise ValueError("输入数据为空")
    
    if not column_name or not column_name.strip():
        raise ValueError("列名不能为空")
    
    if column_name not in data.columns:
        raise ValueError(f"列 '{column_name}' 不存在于数据中")
    
    if operation not in ["sum", "mean", "count"]:
        raise ValueError(f"不支持的操作: {operation}")
    
    try:
        # 执行操作
        if operation == "sum":
            processed_data = data.groupby(column_name).sum()
        elif operation == "mean":
            processed_data = data.groupby(column_name).mean()
        elif operation == "count":
            processed_data = data.groupby(column_name).size().to_frame('count')
        
        result(processed_data)
        
    except Exception as e:
        raise RuntimeError(f"数据处理失败: {str(e)}")
```

这个示例展示了完整的错误处理模式，包括输入验证、操作验证和异常处理。

## 总结

正确的错误处理是uflow节点开发的重要组成部分：

1. **函数库节点**: 抛出异常自动触发错误状态
2. **类继承节点**: 调用 `setError()` 方法
3. **错误信息**: 要清晰具体，便于调试
4. **错误类型**: 选择合适的异常类型
5. **测试验证**: 确保错误处理正常工作

遵循这些指导原则，可以创建健壮、用户友好的uflow节点。
