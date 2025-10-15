# uflow 组件包开发完整指南

## 概述

基于对 `DemoPackage` 模板和 `uflowOpenCv` 示例的分析，本文档整理了 uflow 组件包开发的完整逻辑和最佳实践。

## 包结构组织

### 1. DemoPackage 目录结构详解

基于 `DemoPackage` 模板，以下是各个目录的具体作用和内容：

#### 核心功能目录

**`Nodes/` - 节点定义目录**

- **作用**: 存放所有自定义节点的实现
- **内容**:
  - `DemoNode.py` - 示例节点实现
  - `__init__.py` - 节点模块初始化
- **说明**: 每个 `.py` 文件定义一个或多个节点类，继承自 `NodeBase`

**`Pins/` - 引脚类型定义目录**

- **作用**: 定义自定义引脚类型和数据结构
- **内容**:
  - `DemoPin.py` - 示例自定义引脚类型
  - `__init__.py` - 引脚模块初始化
- **说明**: 实现自定义数据类型和对应的引脚处理逻辑

**`FunctionLibraries/` - 函数库目录**

- **作用**: 提供可调用的函数节点集合
- **内容**:
  - `DemoLib.py` - 示例函数库实现
  - `__init__.py` - 函数库模块初始化
- **说明**: 使用 `@IMPLEMENT_NODE` 装饰器将普通函数转换为节点

#### UI 相关目录

**`UI/` - 用户界面组件目录**

- **作用**: 定义节点和引脚的可视化界面
- **内容**:
  - `UIDemoNode.py` - 节点UI实现
  - `UIDemoPin.py` - 引脚UI实现
- **说明**: 继承自 `UINodeBase` 和 `UIPinBase`，自定义节点的外观和交互

**`Factories/` - 工厂类目录**

- **作用**: 负责创建UI组件和注册组件类型
- **内容**:
  - `UINodeFactory.py` - UI节点工厂
  - `UIPinFactory.py` - UI引脚工厂
  - `PinInputWidgetFactory.py` - 引脚输入控件工厂
- **说明**: 实现工厂模式，根据节点/引脚类型创建对应的UI组件

#### 工具和扩展目录

**`Tools/` - 工具类目录**

- **作用**: 提供工具栏和停靠窗口工具
- **内容**:
  - `DemoShelfTool.py` - 工具栏工具实现
  - `DemoDockTool.py` - 停靠窗口工具实现
- **说明**: 继承自 `ShelfTool` 或 `DockTool`，提供自定义功能工具

**`Exporters/` - 导入导出器目录**

- **作用**: 实现数据的导入导出功能
- **内容**:
  - `DemoExporter.py` - 示例导出器实现
- **说明**: 实现 `IDataExporter` 接口，支持自定义数据格式的导入导出

**`PrefsWidgets/` - 首选项窗口目录**

- **作用**: 提供包相关的配置界面
- **内容**:
  - `DemoPrefs.py` - 示例首选项页面
- **说明**: 继承自 `CategoryWidgetBase`，在首选项窗口中添加配置选项

#### 目录关系图

```
DemoPackage/
├── __init__.py                 # 包入口，继承PackageBase
├── Nodes/                      # 核心逻辑层
│   ├── DemoNode.py            # 节点业务逻辑
│   └── __init__.py
├── Pins/                       # 数据层
│   ├── DemoPin.py             # 自定义数据类型
│   └── __init__.py
├── FunctionLibraries/          # 函数层
│   ├── DemoLib.py             # 可调用函数集合
│   └── __init__.py
├── UI/                         # 表现层
│   ├── UIDemoNode.py          # 节点UI实现
│   └── UIDemoPin.py           # 引脚UI实现
├── Factories/                  # 创建层
│   ├── UINodeFactory.py       # 节点UI工厂
│   ├── UIPinFactory.py        # 引脚UI工厂
│   └── PinInputWidgetFactory.py # 输入控件工厂
├── Tools/                      # 工具层
│   ├── DemoShelfTool.py       # 工具栏工具
│   └── DemoDockTool.py        # 停靠窗口工具
├── Exporters/                  # 扩展层
│   └── DemoExporter.py        # 数据导入导出
└── PrefsWidgets/               # 配置层
    └── DemoPrefs.py           # 首选项配置
```

#### 各目录间的协作关系

1. **核心流程**: `Nodes/` → `Pins/` → `UI/` → `Factories/`
2. **数据流**: `FunctionLibraries/` → `Nodes/` → `Pins/`
3. **UI流**: `UI/` → `Factories/` → 用户界面
4. **工具流**: `Tools/` → 用户操作 → `Nodes/`
5. **配置流**: `PrefsWidgets/` → 全局设置 → 所有组件

### 2. 基本目录结构

每个 uflow 包都应该遵循以下标准目录结构：

```
PackageName/
├── __init__.py              # 包入口文件
├── Nodes/                   # 节点定义
│   ├── __init__.py
│   └── *.py                 # 各种节点实现
├── Pins/                    # 引脚类型定义
│   ├── __init__.py
│   └── *.py                 # 各种引脚类型实现
├── Factories/               # 工厂类
│   ├── __init__.py
│   ├── UINodeFactory.py     # UI节点工厂
│   ├── UIPinFactory.py      # UI引脚工厂
│   └── PinInputWidgetFactory.py  # 引脚输入控件工厂
├── FunctionLibraries/       # 函数库
│   ├── __init__.py
│   └── *.py                 # 各种函数库实现
├── UI/                      # UI组件
│   ├── UINode*.py           # 节点UI实现
│   └── UIPin*.py            # 引脚UI实现
├── Tools/                   # 工具类
│   ├── __init__.py
│   ├── *ShelfTool.py        # 工具栏工具
│   └── *DockTool.py         # 停靠窗口工具
├── Exporters/               # 导入导出器
│   ├── __init__.py
│   └── *.py                 # 各种导入导出器
├── PrefsWidgets/            # 首选项窗口
│   └── *.py                 # 首选项页面
├── Compounds/               # 复合节点（可选）
├── CV_classes/              # 自定义类（可选）
├── res/                     # 资源文件（可选）
└── requirements.txt         # 依赖文件（可选）
```

## 核心组件开发

### 1. 包入口文件 (**init**.py)

```python
import os
from uflow.Core.PackageBase import PackageBase

class YourPackage(PackageBase):
    def __init__(self):
        super(YourPackage, self).__init__()
        self.analyzePackage(os.path.dirname(__file__))
```

**关键点：**

- 继承 `PackageBase`
- 调用 `analyzePackage()` 自动扫描包结构
- 包名与类名保持一致

### 2. 节点开发 (Nodes/)

#### 基本节点结构

```python
from uflow.Core import NodeBase
from uflow.Core.NodeBase import NodePinsSuggestionsHelper
from uflow.Core.Common import *

class YourNode(NodeBase):
    def __init__(self, name):
        super(YourNode, self).__init__(name)
        # 创建输入引脚
        self.input_pin = self.createInputPin('input', 'DataTypePin', defaultValue)
        # 创建输出引脚
        self.output_pin = self.createOutputPin('output', 'DataTypePin')
        # 创建执行引脚（可选）
        self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

    @staticmethod
    def pinTypeHints():
        """定义引脚类型提示"""
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('DataTypePin')
        helper.addOutputDataType('DataTypePin')
        helper.addInputStruct(StructureType.Single)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        """节点分类"""
        return 'YourCategory'

    @staticmethod
    def keywords():
        """搜索关键词"""
        return ['keyword1', 'keyword2']

    @staticmethod
    def description():
        """节点描述（RST格式）"""
        return "Description in rst format."

    def compute(self, *args, **kwargs):
        """节点计算逻辑"""
        input_data = self.input_pin.getData()
        # 处理数据
        result = process_data(input_data)
        self.output_pin.setData(result)
        # 如果有执行引脚
        if hasattr(self, 'outExec'):
            self.outExec.call()
```

#### 节点开发最佳实践

1. **引脚管理**
   - 使用 `createInputPin()` 和 `createOutputPin()` 创建引脚
   - 设置合适的默认值
   - 使用 `pinTypeHints()` 提供类型建议

2. **执行流程**
   - 对于需要执行顺序的节点，使用 `ExecPin`
   - 在 `compute()` 方法中实现核心逻辑
   - 使用 `call()` 触发下游节点

3. **数据结构支持**
   - `StructureType.Single`: 单个值
   - `StructureType.Array`: 数组
   - `StructureType.Multi`: 多值

### 3. 引脚类型开发 (Pins/)

#### 自定义引脚类型

```python
from uflow.Core import PinBase
from uflow.Core.Common import *

class YourCustomType(object):
    """自定义数据类型"""
    def __init__(self, value=None):
        self.value = value

class YourPin(PinBase):
    def __init__(self, name, parent, direction, **kwargs):
        super(YourPin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(YourCustomType())

    @staticmethod
    def IsValuePin():
        """是否为值引脚"""
        return True

    @staticmethod
    def supportedDataTypes():
        """支持的数据类型"""
        return ('YourPin',)

    @staticmethod
    def pinDataTypeHint():
        """引脚数据类型提示"""
        return 'YourPin', False

    @staticmethod
    def color():
        """引脚颜色 (R, G, B, A)"""
        return (200, 200, 50, 255)

    @staticmethod
    def internalDataStructure():
        """内部数据结构"""
        return YourCustomType

    @staticmethod
    def processData(data):
        """数据处理"""
        return YourPin.internalDataStructure()(data)
```

### 4. 函数库开发 (FunctionLibraries/)

#### 函数库实现

```python
from uflow.Core.Common import *
from uflow.Core import FunctionLibraryBase
from uflow.Core import IMPLEMENT_NODE

class YourLib(FunctionLibraryBase):
    def __init__(self, packageName):
        super(YourLib, self).__init__(packageName)

    @staticmethod
    @IMPLEMENT_NODE(
        returns=None, 
        nodeType=NodeTypes.Callable, 
        meta={NodeMeta.CATEGORY: 'YourLib', NodeMeta.KEYWORDS: []}
    )
    def your_function(param1=('StringPin', "default_value")):
        """函数文档（RST格式）"""
        # 函数实现
        return result
```

**关键点：**

- 使用 `@IMPLEMENT_NODE` 装饰器
- 参数使用元组格式：`(pin_type, default_value)`
- 支持多种引脚类型：`StringPin`, `IntPin`, `FloatPin`, `BoolPin` 等

### 5. UI组件开发 (UI/)

#### 节点UI实现

```python
from uflow.UI.Canvas.UINodeBase import UINodeBase

class UIYourNode(UINodeBase):
    def __init__(self, raw_node):
        super(UIYourNode, self).__init__(raw_node)
        # 自定义UI逻辑
```

#### 引脚UI实现

```python
from uflow.UI.Canvas.UIPinBase import UIPinBase

class UIYourPin(UIPinBase):
    def __init__(self, owningNode, raw_pin):
        super(UIYourPin, self).__init__(owningNode, raw_pin)
        # 自定义引脚UI逻辑
```

### 6. 工厂类开发 (Factories/)

#### UI节点工厂

```python
from uflow.UI.Canvas.UINodeBase import UINodeBase
from uflow.Packages.YourPackage.UI.UIYourNode import UIYourNode

def createUINode(raw_instance):
    if raw_instance.__class__.__name__ == "YourNode":
        return UIYourNode(raw_instance)
    return UINodeBase(raw_instance)
```

#### UI引脚工厂

```python
from uflow.UI.Canvas.UIPinBase import UIPinBase
from uflow.Packages.YourPackage.UI.UIYourPin import UIYourPin

def createUIPin(owningNode, raw_instance):
    if raw_instance.__class__.__name__ == "YourPin":
        return UIYourPin(owningNode, raw_instance)
    else:
        return UIPinBase(owningNode, raw_instance)
```

### 7. 工具开发 (Tools/)

#### 工具栏工具

```python
from uflow.UI.Tool.Tool import ShelfTool
from qtpy import QtGui

class YourShelfTool(ShelfTool):
    def __init__(self):
        super(YourShelfTool, self).__init__()

    @staticmethod
    def toolTip():
        return "工具提示"

    @staticmethod
    def getIcon():
        return QtGui.QIcon(":icon_path.png")

    @staticmethod
    def name():
        return "YourShelfTool"

    def do(self):
        # 工具执行逻辑
        pass
```

#### 停靠窗口工具

```python
from uflow.UI.Tool.Tool import DockTool
from qtpy import QtWidgets

class YourDockTool(DockTool):
    def __init__(self):
        super(YourDockTool, self).__init__()

    @staticmethod
    def name():
        return "YourDockTool"

    def onShow(self):
        # 显示时的逻辑
        pass

    def onHide(self):
        # 隐藏时的逻辑
        pass
```

### 8. 导入导出器开发 (Exporters/)

```python
from datetime import datetime
from uflow.UI.UIInterfaces import IDataExporter
from uflow.Core.version import Version

class YourExporter(IDataExporter):
    def __init__(self):
        super(YourExporter, self).__init__()

    @staticmethod
    def createImporterMenu():
        return True

    @staticmethod
    def creationDateString():
        return datetime.now().strftime("%I:%M%p on %B %d, %Y")

    @staticmethod
    def version():
        return Version(1, 0, 0)

    @staticmethod
    def toolTip():
        return "导出器描述"

    @staticmethod
    def displayName():
        return "Your exporter"

    @staticmethod
    def doImport(uflowInstance):
        # 导入逻辑
        pass

    @staticmethod
    def doExport(uflowInstance):
        # 导出逻辑
        pass
```

### 9. 首选项窗口开发 (PrefsWidgets/)

```python
from qtpy.QtWidgets import *
from uflow.UI.Widgets.PropertiesFramework import CollapsibleFormWidget
from uflow.UI.Widgets.PreferencesWindow import CategoryWidgetBase

class YourPrefs(CategoryWidgetBase):
    def __init__(self, parent=None):
        super(YourPrefs, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(2)

        # 创建配置项
        section = CollapsibleFormWidget(headName="配置节")
        self.property = QLineEdit("默认值")
        section.addWidget("配置项", self.property)
        self.layout.addWidget(section)

    def initDefaults(self, settings):
        settings.setValue("Property", "默认值")

    def serialize(self, settings):
        settings.setValue("Property", self.property.text())

    def onShow(self, settings):
        self.property.setText(settings.value("Property"))
```

## 开发流程和最佳实践

### 1. 开发流程

1. **规划阶段**
   - 确定包的功能范围
   - 设计节点和引脚类型
   - 规划UI交互方式

2. **实现阶段**
   - 创建包基础结构
   - 实现核心节点和引脚
   - 开发UI组件
   - 添加工具和导出器

3. **测试阶段**
   - 单元测试各个组件
   - 集成测试整个包
   - 性能优化

4. **发布阶段**
   - 编写文档
   - 创建示例
   - 版本管理

### 2. 最佳实践

#### 代码组织

- 保持单一职责原则
- 使用清晰的命名约定
- 添加充分的文档字符串
- 遵循uflow的编码规范

#### 性能优化

- 避免在 `compute()` 中进行重复计算
- 使用 `dirty` 标志优化更新
- 合理使用缓存机制

#### 错误处理

- 添加输入验证
- 提供有意义的错误信息
- 优雅处理异常情况

#### 用户体验

- 提供直观的节点分类
- 使用清晰的引脚标签
- 添加工具提示和帮助文档

### 3. 调试技巧

1. **使用打印语句**

   ```python
   def compute(self, *args, **kwargs):
       print(f"Node {self.name} computing...")
       # 计算逻辑
   ```

2. **检查引脚状态**

   ```python
   def compute(self, *args, **kwargs):
       if self.input_pin.dirty:
           print(f"Input pin is dirty: {self.input_pin.getData()}")
   ```

3. **使用调试工具**
   - 利用uflow的内置调试功能
   - 使用外部调试器
   - 检查节点执行顺序

## 总结

uflow组件包开发是一个系统性的过程，需要理解其架构设计理念。通过遵循标准的结构组织和开发模式，可以创建出功能强大、易于维护的扩展包。关键是要理解节点-引脚-UI的分离设计，以及工厂模式在组件注册中的作用。

参考 `DemoPackage` 模板和 `uflowOpenCv` 示例，开发者可以快速上手并创建自己的专业级uflow扩展包。
