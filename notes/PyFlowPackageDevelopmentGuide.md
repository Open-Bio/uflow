# uflow包开发指南

## 概述

本指南以创建`uflowDataAnalysis`数据分析包为例，详细说明如何从零开始开发一个完整的uflow包，实现CSV文件的读取和保存功能。

## 第一步：包结构设计

### 1.1 创建包目录结构

在`uflow/Packages/`目录下创建新包目录：

```bash
mkdir -p uflowDataAnalysis/{FunctionLibraries,Nodes,Pins,Tools,UI,Factories}
```

### 1.2 创建必要的__init__.py文件

每个子目录都需要`__init__.py`文件：

```python
"""Packages
"""

# this line adds extension-packages not installed inside the uflow directory
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```

### 1.3 创建包主文件

`uflowDataAnalysis/__init__.py`：

```python
import os
from uflow.Core.PackageBase import PackageBase

class uflowDataAnalysis(PackageBase):
    """Data Analysis uflow package
    """    
    def __init__(self):
        super(uflowDataAnalysis, self).__init__()
        self.analyzePackage(os.path.dirname(__file__))
```

## 第二步：定义数据类型（Pin）

### 2.1 创建DataFramePin

`Pins/DataFramePin.py`：

```python
import pandas as pd
import json
from uflow.Core import PinBase
from uflow.Core.Common import *

class NoneEncoder(json.JSONEncoder):
    def default(self, obj):
        return None

class NoneDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super(NoneDecoder, self).__init__(object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, objDict):
        return None

class DataFramePin(PinBase):
    """DataFrame pin for passing pandas DataFrame objects between nodes"""

    def __init__(self, name, parent, direction, **kwargs):
        super(DataFramePin, self).__init__(name, parent, direction, **kwargs)
        self.setDefaultValue(pd.DataFrame())
        self.disableOptions(PinOptions.Storable)

    @staticmethod
    def jsonEncoderClass():
        return NoneEncoder

    @staticmethod
    def jsonDecoderClass():
        return NoneDecoder

    @staticmethod
    def IsValuePin():
        return True

    @staticmethod
    def supportedDataTypes():
        return ('DataFramePin',)

    @staticmethod
    def pinDataTypeHint():
        return 'DataFramePin', pd.DataFrame()

    @staticmethod
    def color():
        return (50, 200, 100, 255)  # Green color for data

    @staticmethod
    def internalDataStructure():
        return pd.DataFrame

    @staticmethod
    def processData(data):
        if data is None:
            return DataFramePin.pinDataTypeHint()[1]
        if isinstance(data, pd.DataFrame):
            return data
        else:
            raise Exception("Invalid DataFrame data type")
```

**关键点：**

- 直接传递Python对象，无需序列化
- 使用`NoneEncoder`和`NoneDecoder`
- 禁用`PinOptions.Storable`选项
- 设置合适的颜色标识

## 第三步：实现功能库（FunctionLibrary）

### 3.1 创建DataIOLib

`FunctionLibraries/DataIOLib.py`：

```python
import os
import pandas as pd
from uflow.Core import (
    FunctionLibraryBase,
    IMPLEMENT_NODE
)
from uflow.Core.Common import *

class DataIOLib(FunctionLibraryBase):
    '''Data IO function library for reading and writing various data formats'''

    def __init__(self, packageName):
        super(DataIOLib, self).__init__(packageName)

    ###################     READ NODES      ################################################################
    @staticmethod
    @IMPLEMENT_NODE(returns=None, meta={NodeMeta.CATEGORY: 'Data Input', NodeMeta.KEYWORDS: ['csv', 'read', 'data']})
    def ReadCSV(path=('StringPin', "", {PinSpecifiers.INPUT_WIDGET_VARIANT: "FilePathWidget"}),
                separator=('StringPin', ","),
                encoding=('StringPin', "utf-8"),
                header=('IntPin', 0),
                data=(REF, ('DataFramePin', None))):
        """Read data from CSV file."""
        try:
            df = pd.read_csv(path, sep=separator, encoding=encoding, header=header)
            data(df)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
            data(pd.DataFrame())

    ###################     WRITE NODES      ################################################################
    @staticmethod
    @IMPLEMENT_NODE(returns=None, nodeType=NodeTypes.Callable,
                    meta={NodeMeta.CATEGORY: 'Data Output', NodeMeta.KEYWORDS: ['csv', 'write', 'data']})
    def WriteCSV(path=('StringPin', "", {PinSpecifiers.INPUT_WIDGET_VARIANT: "FilePathWidget"}),
                 data=('DataFramePin', None),
                 separator=('StringPin', ","),
                 encoding=('StringPin', "utf-8"),
                 index=('BoolPin', False)):
        """Write data to CSV file."""
        try:
            data.to_csv(path, sep=separator, encoding=encoding, index=index)
        except Exception as e:
            print(f"Error writing CSV file: {e}")
```

**关键点：**

- 使用`@IMPLEMENT_NODE`装饰器
- 设置合适的`meta`信息（类别、关键词）
- 使用`REF`类型用于输出参数
- 包含错误处理机制

## 第四步：创建自定义节点

### 4.1 创建DataViewerNode

`Nodes/DataViewerNode.py`：

```python
from uflow.Core import NodeBase
from uflow.Core.NodeBase import NodePinsSuggestionsHelper
from uflow.Core.Common import *
from qtpy import QtWidgets
import pandas as pd

class DataViewerNode(NodeBase):
    def __init__(self, name):
        super(DataViewerNode, self).__init__(name)
        self.inExec = self.createInputPin(DEFAULT_IN_EXEC_NAME, 'ExecPin', None, self.compute)
        self.dataInput = self.createInputPin('data', 'DataFramePin', structure=StructureType.Multi)
        self.outExec = self.createOutputPin(DEFAULT_OUT_EXEC_NAME, 'ExecPin')

    @staticmethod
    def pinTypeHints():
        helper = NodePinsSuggestionsHelper()
        helper.addInputDataType('ExecPin')
        helper.addInputDataType('DataFramePin')
        helper.addOutputDataType('ExecPin')
        helper.addInputStruct(StructureType.Multi)
        helper.addOutputStruct(StructureType.Single)
        return helper

    @staticmethod
    def category():
        return 'Data Viewers'

    @staticmethod
    def keywords():
        return ['data', 'viewer', 'preview', 'table']

    @staticmethod
    def description():
        return "Preview DataFrame data in a table viewer."

    def compute(self, *args, **kwargs):
        if self.dataInput.dirty:
            inputData = self.dataInput.getData()
            
            # Get or create the data viewer tool
            viewer = self._wrapper.canvasRef().uflowInstance.invokeDockToolByName("uflowDataAnalysis", "DataViewerTool")
            
            if isinstance(inputData, list):
                if inputData:
                    viewer.setDataFrame(inputData[0])
            elif isinstance(inputData, pd.DataFrame):
                viewer.setDataFrame(inputData)
            else:
                viewer.setDataFrame(pd.DataFrame())

            QtWidgets.QApplication.processEvents()
        self.outExec.call()
```

## 第五步：创建工具（Tools）

### 5.1 创建数据表格组件

`UI/DataTableWidget.py`：

```python
from qtpy import QtWidgets, QtCore, QtGui
import pandas as pd

class DataTableWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(DataTableWidget, self).__init__(parent)
        self.setupUI()
        self.currentDataFrame = pd.DataFrame()

    def setupUI(self):
        layout = QtWidgets.QVBoxLayout()
        
        # Info label
        self.infoLabel = QtWidgets.QLabel("No data loaded")
        self.infoLabel.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.infoLabel)
        
        # Table widget
        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.tableWidget.setSortingEnabled(True)
        
        layout.addWidget(self.tableWidget)
        self.setLayout(layout)

    def setDataFrame(self, df):
        """Set the DataFrame to display"""
        if df is None or df.empty:
            self.currentDataFrame = pd.DataFrame()
            self.updateInfo()
            self.clearTable()
            return
            
        self.currentDataFrame = df.copy()
        self.updateInfo()
        self.updateTable()

    def updateInfo(self):
        """Update the info label with DataFrame statistics"""
        if self.currentDataFrame.empty:
            self.infoLabel.setText("No data loaded")
        else:
            rows, cols = self.currentDataFrame.shape
            self.infoLabel.setText(f"Rows: {rows}, Columns: {cols}")

    def updateTable(self):
        """Update the table with data"""
        if self.currentDataFrame.empty:
            self.clearTable()
            return
            
        # Set table dimensions
        self.tableWidget.setRowCount(len(self.currentDataFrame))
        self.tableWidget.setColumnCount(len(self.currentDataFrame.columns))
        
        # Set column headers
        self.tableWidget.setHorizontalHeaderLabels([str(col) for col in self.currentDataFrame.columns])
        
        # Populate table with data
        for i, (idx, row) in enumerate(self.currentDataFrame.iterrows()):
            for j, value in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(value) if pd.notna(value) else "")
                item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(i, j, item)

    def clearTable(self):
        """Clear the table widget"""
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setHorizontalHeaderLabels([])
```

### 5.2 创建DataViewerTool

`Tools/DataViewerTool.py`：

```python
from qtpy import QtGui
import pandas as pd

from uflow.UI.Tool.Tool import DockTool
from ..UI.DataTableWidget import DataTableWidget

class DataViewerTool(DockTool):
    """Data viewer tool for displaying DataFrame data in a table format."""
    
    def __init__(self):
        super(DataViewerTool, self).__init__()
        self.viewer = DataTableWidget(self)
        self.setWidget(self.viewer)

    @staticmethod
    def getIcon():
        return QtGui.QIcon(":brick.png")

    @staticmethod
    def toolTip():
        return "Data table viewer for DataFrame preview"

    @staticmethod
    def isSingleton():
        return True

    @staticmethod
    def name():
        return str("DataViewerTool")

    def setDataFrame(self, df):
        """Set the DataFrame to display in the viewer"""
        if self.viewer:
            self.viewer.setDataFrame(df)
```

## 第六步：创建工厂（Factories）

### 6.1 创建UINodeFactory

`Factories/UINodeFactory.py`：

```python
from uflow.UI.Canvas.UINodeBase import UINodeBase

def createUINode(raw_instance):
    # For now, return the base UI node
    # Can be extended later for custom UI nodes
    return UINodeBase(raw_instance)
```

## 第七步：依赖管理

### 7.1 创建requirements.txt

`requirements.txt`：

```
pandas
openpyxl
xlrd
```

## 第八步：测试和验证

### 8.1 测试包导入

```python
# 测试包是否能正确导入
from . import uflowDataAnalysis
print('Package loaded successfully')

# 测试DataFramePin
from ..Pins.DataFramePin import DataFramePin
print('DataFramePin color:', DataFramePin.color())

# 测试DataIOLib
from ..FunctionLibraries.DataIOLib import DataIOLib
print('Available functions:', [name for name in dir(DataIOLib) if not name.startswith('_')])
```

## 第九步：使用示例

### 9.1 在uflow中使用

1. 启动uflow
2. 在节点库中找到"Data Input"类别
3. 拖拽"ReadCSV"节点到画布
4. 拖拽"WriteCSV"节点到画布
5. 拖拽"DataViewerNode"节点到画布
6. 连接节点：ReadCSV -> DataViewerNode -> WriteCSV
7. 设置文件路径并执行

## 开发要点总结

### 1. 包结构必须完整

- 每个子目录都需要`__init__.py`
- 主包文件必须继承`PackageBase`
- 调用`self.analyzePackage()`方法

### 2. Pin类型定义

- 直接传递Python对象
- 使用`NoneEncoder`和`NoneDecoder`
- 禁用`PinOptions.Storable`
- 设置合适的颜色和默认值

### 3. 函数库实现

- 使用`@IMPLEMENT_NODE`装饰器
- 设置正确的`meta`信息
- 包含错误处理
- 使用`REF`类型用于输出参数

### 4. 节点设计

- 继承`NodeBase`
- 实现`pinTypeHints()`方法
- 设置类别和关键词
- 实现`compute()`方法

### 5. 工具开发

- 继承`DockTool`
- 实现必要的静态方法
- 创建自定义UI组件

### 6. 测试验证

- 确保所有组件能正确导入
- 测试Pin类型的数据传递
- 验证节点功能正常

## 扩展方向

基于这个基础框架，可以继续扩展：

1. **数据处理节点**：筛选、排序、分组、聚合
2. **统计分析节点**：描述性统计、相关性分析
3. **数据清洗节点**：缺失值处理、异常值检测
4. **可视化节点**：图表生成、数据探索
5. **机器学习节点**：分类、回归、聚类

## 常见问题

### Q: 包加载失败怎么办？

A: 检查包结构是否完整，确保所有`__init__.py`文件存在，类名与包名一致。

### Q: Pin类型数据传递失败？

A: 确保使用`NoneEncoder`和`NoneDecoder`，禁用`PinOptions.Storable`。

### Q: 节点在uflow中不显示？

A: 检查`@IMPLEMENT_NODE`装饰器的`meta`信息，确保类别和关键词正确。

### Q: 工具无法调用？

A: 确保工具继承`DockTool`，实现`name()`和`isSingleton()`方法。

---

通过以上步骤，你就可以成功创建一个完整的uflow包，实现自定义的数据处理功能！
