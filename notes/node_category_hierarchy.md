# uflow 节点二级分类实现详解

## 概述

uflow支持节点的多级分类系统，通过管道符 `|` 分隔不同层级的分类。这种设计让节点可以在节点浏览器中形成清晰的层级结构，便于用户查找和使用。

## 分类系统架构

### 1. 分类层级结构

```
包名
├── 一级分类
│   ├── 二级分类
│   │   └── 节点
│   └── 二级分类
│       └── 节点
└── 一级分类
    └── 节点
```

### 2. 分类路径格式

- **单级分类**: `"CategoryName"`
- **二级分类**: `"CategoryName|SubCategoryName"`
- **多级分类**: `"Category1|Category2|Category3"`

## 实现方式

### 1. 类节点 (Class-based Nodes)

#### 基本实现

```python
class YourNode(NodeBase):
    @staticmethod
    def category():
        return "YourCategory|YourSubCategory"
```

#### 实际例子

```python
# 单级分类
class DemoNode(NodeBase):
    @staticmethod
    def category():
        return "Generated from wizard"

# 二级分类
class ViewerNode(NodeBase):
    @staticmethod
    def category():
        return "Viewers"  # 单级分类
```

### 2. 函数式节点 (Functional Nodes)

#### 基本实现

```python
@staticmethod
@IMPLEMENT_NODE(
    returns=("OutputPinType", default_value),
    meta={NodeMeta.CATEGORY: "Category|SubCategory", NodeMeta.KEYWORDS: []}
)
def your_function():
    pass
```

#### 实际例子

```python
# 数学基础运算 - 二级分类
@staticmethod
@IMPLEMENT_NODE(
    returns=("BoolPin", False), 
    meta={NodeMeta.CATEGORY: 'Math|Basic', NodeMeta.KEYWORDS: ["=", "operator"]}
)
def isEqual(a=("AnyPin", None), b=("AnyPin", None)):
    """Is a equal b."""
    return a == b

# 数学位运算 - 二级分类
@staticmethod
@IMPLEMENT_NODE(
    returns=("IntPin", 0), 
    meta={NodeMeta.CATEGORY: "Math|Bits manipulation", NodeMeta.KEYWORDS: []}
)
def bitwiseAnd(a=("IntPin", 0), b=("IntPin", 0)):
    """Bitwise AND operation."""
    return a & b

# 数学浮点运算 - 二级分类
@staticmethod
@IMPLEMENT_NODE(
    returns=("FloatPin", 0.0), 
    meta={NodeMeta.CATEGORY: "Math|Float", NodeMeta.KEYWORDS: ["lerp"]}
)
def lerp(a=("FloatPin", 0.0), b=("FloatPin", 0.0), t=("FloatPin", 0.0)):
    """Linear interpolation between a and b."""
    return a + (b - a) * t

# 数学随机数 - 二级分类
@staticmethod
@IMPLEMENT_NODE(
    returns=("FloatPin", 0.0), 
    meta={NodeMeta.CATEGORY: "Math|random", NodeMeta.KEYWORDS: []}
)
def randomFloat(min_val=("FloatPin", 0.0), max_val=("FloatPin", 1.0)):
    """Generate random float between min and max."""
    import random
    return random.uniform(min_val, max_val)
```

## 分类系统实现机制

### 1. 节点注册过程

```python
# 在 PackageBase.analyzePackage() 中
def loadPackageElements(packagePath, element, elementDict, classType):
    # 对于类节点
    nodeCategoryPath = "{0}|{1}".format(package_name, node_class.category())
    
    # 对于函数式节点
    nodeCategoryPath = "{0}|{1}".format(package_name, meta[NodeMeta.CATEGORY])
```

### 2. UI树形结构构建

```python
# 在 NodeBoxTreeWidget.insertNode() 中
def insertNode(self, nodeCategoryPath, name, doc=None, libName=None, bPyNode=False, bCompoundNode=False):
    nodePath = nodeCategoryPath.split("|")  # 按管道符分割
    categoryPath = ""
    
    # 逐级创建分类文件夹
    for folderId in range(0, len(nodePath)):
        folderName = nodePath[folderId]
        if folderId == 0:
            # 创建根分类
            categoryPath = folderName
            if categoryPath not in self.categoryPaths:
                rootFolderItem = QTreeWidgetItem(self)
                rootFolderItem.bCategory = True
                rootFolderItem.setText(0, folderName)
                self.categoryPaths[categoryPath] = rootFolderItem
        else:
            # 创建子分类
            parentCategoryPath = categoryPath
            categoryPath += "|{}".format(folderName)
            if categoryPath not in self.categoryPaths:
                childCategoryItem = QTreeWidgetItem(self.categoryPaths[parentCategoryPath])
                childCategoryItem.bCategory = True
                childCategoryItem.setText(0, folderName)
                self.categoryPaths[categoryPath] = childCategoryItem
    
    # 在最终分类下创建节点
    nodeItem = QTreeWidgetItem(self.categoryPaths[categoryPath])
    nodeItem.bCategory = False
    nodeItem.setText(0, name)
    return nodeItem
```

## 分类设计最佳实践

### 1. 分类命名规范

#### 推荐的一级分类

- **Math**: 数学运算
- **Logic**: 逻辑运算
- **Data**: 数据处理
- **Flow**: 流程控制
- **I/O**: 输入输出
- **Viewers**: 查看器
- **Debug**: 调试工具
- **Utils**: 工具函数

#### 推荐的二级分类

- **Math|Basic**: 基础数学运算
- **Math|Float**: 浮点运算
- **Math|Int**: 整数运算
- **Math|Bool**: 布尔运算
- **Math|Bits manipulation**: 位运算
- **Math|random**: 随机数
- **Logic|Comparison**: 比较运算
- **Logic|Boolean**: 布尔逻辑
- **Data|Array**: 数组操作
- **Data|String**: 字符串操作
- **Flow|Loops**: 循环控制
- **Flow|Conditionals**: 条件控制

### 2. 分类层级设计原则

#### 层级深度

- **建议**: 2-3级分类
- **避免**: 超过4级分类（过于复杂）

#### 分类粒度

- **一级分类**: 按功能领域划分
- **二级分类**: 按具体用途划分
- **三级分类**: 按数据类型或特殊用途划分

### 3. 实际项目中的分类示例

#### uflowBase包分类结构

```
uflowBase
├── Math
│   ├── Basic (基础运算)
│   ├── Float (浮点运算)
│   ├── Int (整数运算)
│   ├── Bool (布尔运算)
│   ├── Bits manipulation (位运算)
│   └── random (随机数)
├── Logic
│   ├── Comparison (比较)
│   └── Boolean (布尔逻辑)
├── Data
│   ├── Array (数组)
│   ├── String (字符串)
│   └── Dictionary (字典)
├── Flow
│   ├── Loops (循环)
│   ├── Conditionals (条件)
│   └── Sequence (序列)
├── I/O
│   ├── Input (输入)
│   └── Output (输出)
├── Viewers
│   └── Display (显示)
├── Debug
│   └── Console (控制台)
└── Utils
    ├── Convert (转换)
    └── Utility (工具)
```

#### uflowOpenCv包分类结构

```
uflowOpenCv
├── Inputs
│   ├── Image (图像输入)
│   ├── Video (视频输入)
│   └── Camera (摄像头)
├── Processing
│   ├── Filter (滤波)
│   ├── Transform (变换)
│   └── Morphology (形态学)
├── Analysis
│   ├── Feature (特征)
│   ├── Detection (检测)
│   └── Recognition (识别)
├── Viewers
│   └── Display (显示)
└── Utils
    ├── Convert (转换)
    └── Utility (工具)
```

## 实现步骤

### 1. 设计分类结构

```python
# 规划分类层级
categories = {
    "Math": {
        "Basic": ["add", "subtract", "multiply", "divide"],
        "Float": ["lerp", "clamp", "smoothstep"],
        "Int": ["modulo", "floor", "ceil"],
        "Bool": ["and", "or", "not", "xor"],
        "Bits": ["bitwiseAnd", "bitwiseOr", "bitwiseXor"],
        "random": ["randomFloat", "randomInt", "randomBool"]
    },
    "Logic": {
        "Comparison": ["equal", "notEqual", "greater", "less"],
        "Boolean": ["and", "or", "not", "nand", "nor"]
    }
}
```

### 2. 实现节点分类

```python
# 类节点
class MathAddNode(NodeBase):
    @staticmethod
    def category():
        return "Math|Basic"

# 函数式节点
@staticmethod
@IMPLEMENT_NODE(
    returns=("FloatPin", 0.0),
    meta={NodeMeta.CATEGORY: "Math|Basic", NodeMeta.KEYWORDS: ["add", "plus"]}
)
def add(a=("FloatPin", 0.0), b=("FloatPin", 0.0)):
    """Add two numbers."""
    return a + b
```

### 3. 测试分类效果

- 启动uflow
- 打开节点浏览器
- 检查分类层级是否正确显示
- 验证节点是否在正确的分类下

## 注意事项

### 1. 分类命名

- 使用英文命名，避免特殊字符
- 保持命名一致性和简洁性
- 避免过长的分类名称

### 2. 分类维护

- 定期整理和优化分类结构
- 保持分类的层次清晰
- 避免分类过于细分或过于粗糙

### 3. 向后兼容

- 修改分类名称时要考虑向后兼容性
- 提供迁移路径或保持旧分类名称

## 总结

uflow的二级分类系统通过管道符 `|` 实现层级分类，为节点提供了清晰的组织结构。通过合理设计分类层级和命名规范，可以大大提升用户体验和开发效率。关键是要保持分类的一致性和层次清晰，避免过度复杂化。
