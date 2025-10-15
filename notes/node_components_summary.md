# uflow 节点组成部分详解

## 节点核心结构

### 1. 基础属性

- **唯一标识**: `uid` - 节点的唯一UUID标识符
- **名称**: `name` - 节点显示名称
- **位置**: `x`, `y` - 节点在画布上的坐标
- **包信息**: `packageName`, `lib` - 所属包和库信息

### 2. 引脚系统 (Pins)

#### 输入引脚 (Input Pins)

- **数据引脚**: 接收数据输入
- **执行引脚**: 接收执行信号 (inExec)
- **属性**:
  - `name`: 引脚名称
  - `dataType`: 数据类型 (StringPin, IntPin, BoolPin等)
  - `direction`: 方向 (Input/Output)
  - `defaultValue`: 默认值
  - `pinIndex`: 引脚索引位置

#### 输出引脚 (Output Pins)

- **数据引脚**: 输出计算结果
- **执行引脚**: 传递执行信号 (outExec)
- **属性**: 与输入引脚类似

### 3. 节点功能

#### 计算逻辑 (Compute Method)

```python
def compute(self, *args, **kwargs):
    # 1. 从输入引脚获取数据
    # 2. 执行计算逻辑
    # 3. 设置输出引脚数据
    # 4. 调用执行引脚 (如需要)
```

#### 执行控制

- **缓存机制**: `bCacheEnabled` - 是否启用结果缓存
- **脏标记**: `dirty` - 标记是否需要重新计算
- **执行状态**: `computing`, `computed` - 执行状态信号

### 4. 节点类型

#### Callable节点 (可调用)

- 有执行端口 (inExec/outExec)
- 用于流程控制
- 示例: branch, sequence, switch

#### Pure节点 (纯函数)

- 无执行端口
- 自动执行 (数据变化时)
- 示例: 数学运算, 图像处理

### 5. 元数据系统

#### 节点元数据

- **分类**: `category` - 节点分类
- **关键词**: `keywords` - 搜索关键词
- **描述**: `description` - 节点说明
- **版本信息**: 废弃、实验性标记

#### 状态标记

- `_deprecated`: 废弃标记
- `_experimental`: 实验性标记
- `_lastError`: 最后错误信息

### 6. UI包装器 (Wrapper)

#### 视觉属性

- **颜色**: `headerColor` - 节点头部颜色
- **大小**: 节点尺寸和形状
- **位置**: 在画布上的显示位置

#### UI状态

- **折叠状态**: `collapsed` - 是否折叠显示
- **分组**: `groups` - 引脚分组管理
- **标签**: 节点显示标签

### 7. 序列化系统

#### JSON模板结构

```json
{
    "package": "包名",
    "lib": "库名", 
    "type": "节点类型",
    "name": "节点名称",
    "uuid": "唯一标识",
    "inputs": [输入引脚数据],
    "outputs": [输出引脚数据],
    "meta": {元数据},
    "wrapper": {UI包装器数据},
    "x": 0, "y": 0
}
```

### 8. 信号系统

#### 节点信号

- `killed`: 节点被删除
- `tick`: 定时信号
- `setDirty`: 标记为脏
- `computing`: 开始计算
- `computed`: 计算完成
- `errorOccurred`: 发生错误
- `errorCleared`: 错误清除

#### 引脚信号

- `onPinConnected`: 引脚连接
- `onPinDisconnected`: 引脚断开
- `dataBeenSet`: 数据设置
- `nameChanged`: 名称改变

## 节点生命周期

### 1. 创建阶段

- 初始化基础属性
- 创建引脚
- 设置默认值
- 注册到图形管理器

### 2. 配置阶段

- 设置引脚属性
- 配置计算逻辑
- 设置UI包装器
- 建立信号连接

### 3. 执行阶段

- 接收输入数据
- 执行计算逻辑
- 更新输出数据
- 触发后续节点

### 4. 销毁阶段

- 清理资源
- 断开连接
- 从图形中移除
- 释放内存

## 总结

uflow节点是一个复杂的对象，包含数据流、控制流、UI显示、序列化等多个方面的功能。通过模块化设计，实现了高度的可扩展性和灵活性，支持各种类型的节点需求。
