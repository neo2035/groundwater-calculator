# 一维瞬时泄漏地下水污染迁移模型

## 项目简介

本项目实现了一个用于预测地下水污染迁移的经典模型——**一维瞬时泄漏模型**。该模型基于对流-弥散-反应方程（Advection-Dispersion-Reaction Equation, ADR）的解析解，用于计算污染物在含水层中的时空分布。

## 数学模型

模型基于以下解析解方程：

```
c(x,t) = [m / (2*n*W*√(π*DL*t))] * exp[-λt - (x-ut)²/(4*DL*t)]
```

其中：
- `c(x,t)`: 时间t、位置x处的污染物浓度 (mg/L)
- `m`: 污染物泄漏质量 (g)
- `W`: 横截面积 (m²)
- `n`: 有效孔隙度
- `u`: 地下水实际流速 (m/d)
- `DL`: 纵向弥散系数 (m²/d)
- `λ`: 反应系数 (1/d)
- `x`: 预测点位置 (m)
- `t`: 预测时间 (d)

## 物理过程

模型综合考虑了三个主要的物理化学过程：

1. **对流 (Advection)**: 污染物随地下水整体流动的迁移
2. **水动力弥散 (Dispersion)**: 由含水层非均质性导致的扩散现象
3. **反应/降解 (Reaction)**: 污染物的化学反应、生物降解等

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```python
from groundwater_contamination_model import GroundwaterContaminationModel
import numpy as np

# 创建模型实例
model = GroundwaterContaminationModel(
    m=100.0,        # 污染物泄漏质量 (g)
    W=2.0,          # 横截面积 (m²)
    n=0.3,          # 有效孔隙度
    u=0.1,          # 地下水实际流速 (m/d)
    DL=0.5,         # 纵向弥散系数 (m²/d)
    lambda_decay=0.0 # 反应系数 (1/d)
)

# 设置空间范围和评价标准
x_range = np.arange(-50, 101, 1)
standard_limit = 0.5   # 评价标准 (mg/L)
detection_limit = 0.05 # 检出限 (mg/L)

# 单时间点分析
results = model.plot_single_time(100, x_range, standard_limit, detection_limit)

# 多时间点对比
model.plot_multiple_times([100, 200, 300], x_range, standard_limit, detection_limit)
```

### 运行完整示例

```bash
python groundwater_contamination_model.py
```

## 功能特性

- ✅ **面向对象设计**: 清晰的类结构，易于扩展和维护
- ✅ **参数验证**: 自动验证输入参数的合理性
- ✅ **数值稳定性**: 处理数值溢出和边界条件
- ✅ **中文字体支持**: 自动检测和设置中文字体
- ✅ **多种可视化**: 单时间点分析和多时间点对比
- ✅ **结果统计**: 自动计算最大浓度、超标范围、影响范围
- ✅ **图表导出**: 支持高分辨率图片保存

## 输出结果

程序会生成以下结果：

1. **可视化图表**:
   - 浓度空间分布曲线
   - 评价标准线和检出限线
   - 超标区域和影响区域填充
   - 关键位置标记（注入点、污染羽中心、最大浓度点）

2. **统计信息**:
   - 最大浓度及其位置
   - 超标距离范围
   - 影响距离范围

## 应用场景

- 地下水污染风险评估
- 污染场地修复设计
- 环境影响评价
- 监测井布设优化
- 污染羽迁移预测

## 注意事项

1. 模型假设含水层为均质、各向同性
2. 适用于保守污染物或一级反应动力学
3. 输入参数应符合实际水文地质条件
4. 建议结合现场监测数据进行模型校正

## 许可证

本项目仅供学习和研究使用。
