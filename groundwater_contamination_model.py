import numpy as np
import matplotlib.pyplot as plt
import math
import warnings

# 设置中文字体支持
def setup_chinese_font():
    """设置matplotlib的中文字体支持"""
    try:
        # Windows系统常用字体
        fonts = ['SimHei', 'Microsoft YaHei', 'SimSun', 'Arial Unicode MS', 'DejaVu Sans']
        
        for font in fonts:
            try:
                plt.rcParams['font.sans-serif'] = [font]
                plt.rcParams['axes.unicode_minus'] = False
                # 测试字体是否可用
                fig, ax = plt.subplots(figsize=(1, 1))
                ax.text(0.5, 0.5, '测试中文', fontsize=12)
                plt.close(fig)
                print(f"成功设置中文字体: {font}")
                return True
            except:
                continue
        
        print("警告: 未能设置中文字体，将使用默认字体")
        return False
    except Exception as e:
        print(f"字体设置错误: {e}")
        return False

# 设置字体
setup_chinese_font()

class GroundwaterContaminationModel:
    """一维瞬时泄漏地下水污染迁移模型"""
    
    def __init__(self, m, W, n, u, DL, lambda_decay=0.0):
        """
        初始化模型参数
        
        Args:
            m (float): 污染物泄漏质量 (g)
            W (float): 横截面积 (m^2)
            n (float): 有效孔隙度
            u (float): 地下水实际流速 (m/d)
            DL (float): 纵向弥散系数 (m^2/d)
            lambda_decay (float): 反应系数 (1/d), 默认为0
        """
        self.m = m
        self.W = W
        self.n = n
        self.u = u
        self.DL = DL
        self.lambda_decay = lambda_decay
        
        # 验证参数合理性
        self._validate_parameters()
    
    def _validate_parameters(self):
        """验证输入参数的合理性"""
        if self.m <= 0:
            raise ValueError("污染物质量必须大于0")
        if self.W <= 0:
            raise ValueError("横截面积必须大于0")
        if not (0 < self.n <= 1):
            raise ValueError("有效孔隙度必须在0-1之间")
        if self.u < 0:
            raise ValueError("地下水流速不能为负")
        if self.DL <= 0:
            raise ValueError("纵向弥散系数必须大于0")
        if self.lambda_decay < 0:
            raise ValueError("反应系数不能为负")
    
    def calculate_concentration(self, x, t):
        """
        计算指定时间和位置的污染物浓度
        
        方程: c(x,t) = [m / (2*n*W*sqrt(pi*DL*t))] * exp[-lambda*t - ((x-u*t)^2)/(4*DL*t)]
        
        Args:
            x (array-like): 预测点位置 (m)
            t (float): 预测时间 (d)
        
        Returns:
            array-like: 浓度 (mg/L)
        """
        # 处理边界条件
        if np.any(np.asarray(t) <= 0):
            return np.zeros_like(x)
        
        # 转换为numpy数组以支持向量化计算
        x = np.asarray(x)
        
        # 系数部分
        coeff = self.m / (2 * self.n * self.W * np.sqrt(np.pi * self.DL * t))
        
        # 指数部分
        decay_term = -self.lambda_decay * t
        transport_term = -((x - self.u * t)**2) / (4 * self.DL * t)
        
        # 避免数值溢出
        exponent = decay_term + transport_term
        
        # 对于过小的指数值，直接返回0以避免数值误差
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            concentration = coeff * np.exp(np.clip(exponent, -700, 700))
        
        # 确保浓度非负
        concentration = np.maximum(concentration, 0)
        
        return concentration
    
    def find_concentration_range(self, x, concentrations, limit):
        """
        找到浓度超过指定限值的空间范围
        
        Args:
            x (array): 位置数组
            concentrations (array): 浓度数组
            limit (float): 浓度限值
        
        Returns:
            tuple: (起始位置, 结束位置) 或 (None, None) 如果没有超标
        """
        indices = np.where(concentrations > limit)[0]
        if indices.size > 0:
            return x[indices[0]], x[indices[-1]]
        return None, None
    
    def analyze_results(self, x, concentrations, standard_limit, detection_limit):
        """
        分析计算结果并生成统计信息
        
        Args:
            x (array): 位置数组
            concentrations (array): 浓度数组
            standard_limit (float): 评价标准 (mg/L)
            detection_limit (float): 检出限 (mg/L)
        
        Returns:
            dict: 包含统计结果的字典
        """
        max_concentration = np.max(concentrations)
        max_position = x[np.argmax(concentrations)]
        
        # 超标范围
        exceed_start, exceed_end = self.find_concentration_range(x, concentrations, standard_limit)
        exceed_range = f"{exceed_start:.0f}m - {exceed_end:.0f}m" if exceed_start is not None else "无超标"
        
        # 影响范围
        influence_start, influence_end = self.find_concentration_range(x, concentrations, detection_limit)
        influence_range = f"{influence_start:.0f}m - {influence_end:.0f}m" if influence_start is not None else "无影响"
        
        return {
            'max_concentration': max_concentration,
            'max_position': max_position,
            'exceed_range': exceed_range,
            'influence_range': influence_range,
            'exceed_start': exceed_start,
            'exceed_end': exceed_end,
            'influence_start': influence_start,
            'influence_end': influence_end
        }
    
    def plot_single_time(self, t_pred, x_range, standard_limit, detection_limit, 
                        figsize=(12, 8), save_path=None):
        """
        绘制单一时间点的浓度分布图
        
        Args:
            t_pred (float): 预测时间 (天)
            x_range (array): 空间范围
            standard_limit (float): 评价标准
            detection_limit (float): 检出限
            figsize (tuple): 图形尺寸
            save_path (str): 保存路径，可选
        """
        concentrations = self.calculate_concentration(x_range, t_pred)
        results = self.analyze_results(x_range, concentrations, standard_limit, detection_limit)
        
        plt.figure(figsize=figsize)
        
        # 绘制浓度曲线
        plt.plot(x_range, concentrations, 'b-', linewidth=2.5, label=f't = {t_pred}天')
        
        # 标记评价标准线和检出限线
        plt.axhline(y=standard_limit, color='red', linestyle='--', linewidth=2, 
                   label=f'评价标准 ({standard_limit} mg/L)')
        plt.axhline(y=detection_limit, color='green', linestyle=':', linewidth=2, 
                   label=f'检出限 ({detection_limit} mg/L)')
        
        # 填充超标区域
        if results['exceed_start'] is not None:
            plt.fill_between(x_range, concentrations, standard_limit, 
                           where=(concentrations > standard_limit),
                           color='red', alpha=0.2, label='超标区域', interpolate=True)
        
        # 填充影响区域（但不超标的部分）
        if results['influence_start'] is not None:
            plt.fill_between(x_range, concentrations, detection_limit, 
                           where=((concentrations > detection_limit) & (concentrations <= standard_limit)),
                           color='orange', alpha=0.15, label='影响区域', interpolate=True)
        
        # 标记关键位置
        plume_center = self.u * t_pred
        plt.axvline(x=plume_center, color='gray', linestyle='-', alpha=0.7, linewidth=2,
                   label=f'污染羽中心 (x=ut={plume_center:.1f}m)')
        plt.axvline(x=0, color='black', linestyle='-', linewidth=2, label='注入点 (x=0)')
        
        # 标记最大浓度点
        plt.plot(results['max_position'], results['max_concentration'], 'ro', 
                markersize=8, label=f'最大浓度点 ({results["max_concentration"]:.3f} mg/L)')
        
        # 设置图表属性
        plt.title(f'一维瞬时泄漏模型 - 浓度空间分布 (t = {t_pred}天)', fontsize=14, fontweight='bold')
        plt.xlabel('距离 (m)', fontsize=12)
        plt.ylabel('浓度 (mg/L)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim(x_range[0], x_range[-1])
        plt.ylim(bottom=0, top=max(results['max_concentration'] * 1.1, standard_limit * 1.2))
        
        # 添加文本注释
        textstr = f'''模型参数:
质量: {self.m}g, 截面积: {self.W}m²
流速: {self.u}m/d, 孔隙度: {self.n}
弥散系数: {self.DL}m²/d, 反应系数: {self.lambda_decay}/d

结果统计:
最大浓度: {results["max_concentration"]:.3f} mg/L
超标范围: {results["exceed_range"]}
影响范围: {results["influence_range"]}'''
        
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=9,
                verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
        
        return results
    
    def plot_multiple_times(self, time_list, x_range, standard_limit, detection_limit, 
                          figsize=(12, 8), save_path=None):
        """
        绘制多个时间点的浓度分布对比图
        
        Args:
            time_list (list): 时间点列表
            x_range (array): 空间范围
            standard_limit (float): 评价标准
            detection_limit (float): 检出限
            figsize (tuple): 图形尺寸
            save_path (str): 保存路径，可选
        """
        plt.figure(figsize=figsize)
        
        colors = ['blue', 'lightblue', 'red', 'orange', 'purple']
        linestyles = ['-', '--', '-.', ':', '-']
        
        for i, t in enumerate(time_list):
            concentrations = self.calculate_concentration(x_range, t)
            color = colors[i % len(colors)]
            linestyle = linestyles[i % len(linestyles)]
            
            plt.plot(x_range, concentrations, color=color, linestyle=linestyle, 
                    linewidth=2, label=f't = {t}天')
        
        # 标记评价标准线和检出限线
        plt.axhline(y=standard_limit, color='red', linestyle='--', linewidth=1.5, 
                   label=f'评价标准 ({standard_limit} mg/L)')
        plt.axhline(y=detection_limit, color='green', linestyle=':', linewidth=1.5, 
                   label=f'检出限 ({detection_limit} mg/L)')
        
        # 标记注入点
        plt.axvline(x=0, color='black', linestyle='-', linewidth=1.5, label='注入点 (x=0)')
        
        # 设置图表属性
        plt.title('一维瞬时泄漏模型 - 多时间点浓度分布对比', fontsize=14, fontweight='bold')
        plt.xlabel('距离 (m)', fontsize=12)
        plt.ylabel('浓度 (mg/L)', fontsize=12)
        plt.legend(loc='best', fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.xlim(x_range[0], x_range[-1])
        plt.ylim(bottom=0)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()

def main():
    """主函数 - 演示模型使用"""
    
    # 设置模型参数（根据您的截图）
    model = GroundwaterContaminationModel(
        m=100.0,        # 污染物泄漏质量 (g)
        W=2.0,          # 横截面积 (m^2)
        n=0.3,          # 有效孔隙度
        u=0.1,          # 地下水实际流速 (m/d)
        DL=0.5,         # 纵向弥散系数 (m^2/d)
        lambda_decay=0.0 # 反应系数 (1/d)
    )
    
    # 设置评价标准
    standard_limit = 0.5   # 评价标准 (mg/L)
    detection_limit = 0.05 # 检出限 (mg/L)
    
    # 设置空间范围
    x_range = np.arange(-50, 101, 1)  # -50m 到 100m，步长1m
    
    print("=== 一维瞬时泄漏地下水污染迁移模型 ===\n")
    
    # 方案一：单一时间点分析
    print("方案一：指定时间不同位置计算")
    t_pred = 100.0
    results = model.plot_single_time(t_pred, x_range, standard_limit, detection_limit)
    
    print(f"\n--- 模拟结果统计 (时间: {t_pred}天) ---")
    print(f"最大浓度: {results['max_concentration']:.3f} mg/L")
    print(f"最大浓度位置: {results['max_position']:.1f} m")
    print(f"超标距离 (> {standard_limit} mg/L): {results['exceed_range']}")
    print(f"影响距离 (> {detection_limit} mg/L): {results['influence_range']}")
    
    # 方案二：多时间点对比（对应截图中的100, 200, 300天）
    print("\n方案二：多时间点对比分析")
    time_list = [100, 200, 300]
    model.plot_multiple_times(time_list, x_range, standard_limit, detection_limit)
    
    # 打印各时间点的统计结果
    print("\n--- 多时间点统计结果 ---")
    for t in time_list:
        concentrations = model.calculate_concentration(x_range, t)
        results_t = model.analyze_results(x_range, concentrations, standard_limit, detection_limit)
        print(f"t = {t}天: 最大浓度 = {results_t['max_concentration']:.3f} mg/L, "
              f"超标范围 = {results_t['exceed_range']}")

if __name__ == "__main__":
    main()
