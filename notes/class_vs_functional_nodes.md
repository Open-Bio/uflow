# uflow 类节点 vs 函数式节点 详细对比

## 概述

在uflow中，有两种主要的节点实现方式：

1. **类节点 (Class-based Nodes)** - 在 `Nodes/` 目录下
2. **函数式节点 (Functional Nodes)** - 在 `FunctionLibraries/` 目录下

## 1. 类节点 (Class-based Nodes)

### 特点

- 继承自 `NodeBase` 类
- 位于 `Packages/*/Nodes/` 目录下
- 具有完整的生命周期管理
- 支持复杂的状态管理和UI交互

### 代码结构

```python
from uflow.Core import NodeBase
from uflow.Core.NodeBase import NodePinsSuggestionsHelper
from uflow.Core.Common import *

class YourNode(NodeBase):
    def __init__(self, name):
        super(YourNode, self).__init__(name)
        # 创建引脚
        self.input_pin = self.createInputPin('input', 'DataTypePin')
        self.output_pin = self.createOutputPin('output', 'DataTypePin')
        
    @staticmethod
    def pinTypeHints():
        # 引脚类型提示
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('DataTypePin')
        helper.addOutputDataType('DataTypePin')
        return helper
        
    @staticmethod
    def category():
        return 'YourCategory'
        
    def compute(self, *args, **kwargs):
        # 核心计算逻辑
        input_data = self.input_pin.getData()
        result = process_data(input_data)
        self.output_pin.setData(result)
```

### 优势

- **状态管理**: 可以维护内部状态
- **复杂逻辑**: 支持复杂的计算流程
- **UI定制**: 可以自定义UI组件
- **生命周期**: 完整的创建、更新、销毁流程
- **引脚管理**: 动态创建和管理引脚

### 适用场景

- 需要维护状态的节点（如累加器、缓存器）
- 复杂的图像处理节点（如ViewerNode）
- 需要自定义UI的节点
- 需要执行流程控制的节点

### 实际例子

```python
# ViewerNode.py - 图像查看器节点
class ViewerNode(NodeBase):
    def __init__(self, name):
        super(ViewerNode, self).__init__(name)
        self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        self.inp = self.createInputPin('img', 'ImagePin', structure=StructureType.Multi)
        self.arrayData = self.createInputPin('graph', 'GraphElementPin', structure=StructureType.Array)
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

    def compute(self, *args, **kwargs):
        if self.inp.dirty or self.arrayData.dirty:
            # 复杂的图像处理逻辑
            inputData = self.inp.getData()
            viewer = self._wrapper.canvasRef().uflowInstance.invokeDockToolByName("OpenCVPackage","ImageViewerTool")
            # ... 处理逻辑
        self.outExec.call()
```

## 2. 函数式节点 (Functional Nodes)

### 特点

- 使用 `@IMPLEMENT_NODE` 装饰器
- 位于 `FunctionLibraries/` 目录下
- 纯函数式实现
- 无状态，输入输出明确

### 代码结构

```python
from uflow.Core.Common import *
from uflow.Core import FunctionLibraryBase
from uflow.Core import IMPLEMENT_NODE

class YourLib(FunctionLibraryBase):
    def __init__(self, packageName):
        super(YourLib, self).__init__(packageName)

    @staticmethod
    @IMPLEMENT_NODE(
        returns=('OutputPinType', default_value),
        nodeType=NodeTypes.Callable,
        meta={NodeMeta.CATEGORY: 'Category', NodeMeta.KEYWORDS: []}
    )
    def your_function(
        param1=('InputPinType1', default_value1),
        param2=('InputPinType2', default_value2)
    ):
        """函数文档"""
        # 纯函数逻辑
        result = process(param1, param2)
        return result
```

### 优势

- **简洁**: 代码更简洁，易于理解
- **无状态**: 纯函数，无副作用
- **快速开发**: 快速创建简单功能
- **测试友好**: 易于单元测试
- **性能**: 通常性能更好

### 适用场景

- 简单的数学运算
- 数据转换
- 文件I/O操作
- 纯函数计算

### 实际例子

```python
# OpenCvLib.py - 图像读取函数
@staticmethod
@IMPLEMENT_NODE(returns=None, meta={NodeMeta.CATEGORY: 'Inputs', NodeMeta.KEYWORDS: []})
def cv_ReadImage(
    path=('StringPin', "", {PinSpecifiers.INPUT_WIDGET_VARIANT: "FilePathWidget"}),
    gray_scale=('BoolPin', False), 
    img=(REF, ('ImagePin', None))
):
    """Return a frame of the loaded image."""
    if gray_scale:
        img(cv2.imread(path, cv2.IMREAD_GRAYSCALE))
    else:
        img(cv2.imread(path, cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH | cv2.IMREAD_UNCHANGED))

# 图像写入函数
@staticmethod
@IMPLEMENT_NODE(returns=None, nodeType=NodeTypes.Callable,
                meta={NodeMeta.CATEGORY: 'Inputs', NodeMeta.KEYWORDS: []})
def cv_WriteImage(
    path=('StringPin', "", {PinSpecifiers.INPUT_WIDGET_VARIANT: "FilePathWidget"}),
    img=('ImagePin', None)
):
    """Write image to file."""
    cv2.imwrite(path, img)
```

## 3. 详细对比

| 特性 | 类节点 | 函数式节点 |
|------|--------|------------|
| **实现方式** | 继承NodeBase | @IMPLEMENT_NODE装饰器 |
| **位置** | Nodes/目录 | FunctionLibraries/目录 |
| **状态管理** | ✅ 支持 | ❌ 无状态 |
| **UI定制** | ✅ 完全支持 | ❌ 有限支持 |
| **引脚管理** | ✅ 动态创建 | ❌ 静态定义 |
| **执行控制** | ✅ 支持ExecPin | ✅ 支持ExecPin |
| **代码复杂度** | 较高 | 较低 |
| **开发速度** | 较慢 | 较快 |
| **性能** | 一般 | 较好 |
| **测试难度** | 较难 | 较易 |
| **维护成本** | 较高 | 较低 |

## 4. 选择指南

### 使用类节点的情况

- 需要维护内部状态
- 需要复杂的UI交互
- 需要动态创建引脚
- 需要执行流程控制
- 需要与外部工具集成

### 使用函数式节点的情况

- 简单的数据转换
- 纯函数计算
- 快速原型开发
- 数学运算
- 文件I/O操作

## 5. 混合使用策略

在实际开发中，通常采用混合策略：

1. **核心功能用类节点**: 复杂的状态管理和UI交互
2. **工具函数用函数式节点**: 简单的数据处理和转换
3. **I/O操作用函数式节点**: 文件读写、网络请求等
4. **算法实现用函数式节点**: 数学计算、图像处理算法

## 6. 实际项目中的分布

### uflowOpenCv包分析

- **类节点** (Nodes/目录):
  - `ViewerNode.py` - 图像查看器（需要UI交互）
  - `PaintNode.py` - 绘画节点（需要状态管理）

- **函数式节点** (FunctionLibraries/OpenCvLib.py):
  - `cv_ReadImage` - 读取图像（纯I/O操作）
  - `cv_WriteImage` - 写入图像（纯I/O操作）
  - `cv_Histogram` - 直方图计算（纯函数计算）
  - 各种OpenCV算法函数（纯函数计算）

## 总结

**类节点**适合复杂的功能实现，提供完整的生命周期管理和UI定制能力；**函数式节点**适合简单的功能实现，提供快速开发和良好的性能。

在实际项目中，应该根据具体需求选择合适的实现方式，通常采用混合策略来平衡开发效率和功能复杂度。
