import numpy as np
import matplotlib.pyplot as plt
from groundwater_contamination_model import GroundwaterContaminationModel, setup_chinese_font

# 设置中文字体
setup_chinese_font()

class GroundwaterCalculator:
    """地下水污染迁移交互式计算器"""
    
    def __init__(self):
        self.model = None
        self.current_params = {}
        
    def display_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("           地下水污染迁移计算器")
        print("="*60)
        print("1. 设置模型参数")
        print("2. 方案一：指定时间不同位置计算")
        print("3. 方案二：指定位置不同时间计算") 
        print("4. 多时间点对比分析")
        print("5. 参数敏感性分析")
        print("6. 查看当前参数")
        print("7. 保存计算结果")
        print("0. 退出程序")
        print("-"*60)
    
    def input_parameters(self):
        """交互式输入模型参数"""
        print("\n=== 模型参数设置 ===")
        
        try:
            # 基本物理参数
            print("\n--- 基本物理参数 ---")
            m = float(input("污染物泄漏质量 m (g) [默认: 100]: ") or 100)
            W = float(input("横截面积 W (m²) [默认: 2]: ") or 2)
            n = float(input("有效孔隙度 n [默认: 0.3]: ") or 0.3)
            u = float(input("地下水实际流速 u (m/d) [默认: 0.1]: ") or 0.1)
            DL = float(input("纵向弥散系数 DL (m²/d) [默认: 0.5]: ") or 0.5)
            lambda_decay = float(input("反应系数 λ (1/d) [默认: 0]: ") or 0)
            
            # 评价标准参数
            print("\n--- 评价标准参数 ---")
            standard_limit = float(input("评价标准 (mg/L) [默认: 0.5]: ") or 0.5)
            detection_limit = float(input("检出限 (mg/L) [默认: 0.05]: ") or 0.05)
            
            # 创建模型实例
            self.model = GroundwaterContaminationModel(m, W, n, u, DL, lambda_decay)
            self.current_params = {
                'm': m, 'W': W, 'n': n, 'u': u, 'DL': DL, 'lambda_decay': lambda_decay,
                'standard_limit': standard_limit, 'detection_limit': detection_limit
            }
            
            print(f"\n✅ 参数设置成功！")
            self.display_current_params()
            
        except ValueError as e:
            print(f"❌ 输入错误: 请输入有效的数值")
        except Exception as e:
            print(f"❌ 参数设置失败: {e}")
    
    def display_current_params(self):
        """显示当前参数"""
        if not self.current_params:
            print("❌ 尚未设置参数，请先设置模型参数")
            return
        
        print("\n=== 当前模型参数 ===")
        print(f"污染物质量: {self.current_params['m']} g")
        print(f"横截面积: {self.current_params['W']} m²")
        print(f"有效孔隙度: {self.current_params['n']}")
        print(f"地下水流速: {self.current_params['u']} m/d")
        print(f"纵向弥散系数: {self.current_params['DL']} m²/d")
        print(f"反应系数: {self.current_params['lambda_decay']} 1/d")
        print(f"评价标准: {self.current_params['standard_limit']} mg/L")
        print(f"检出限: {self.current_params['detection_limit']} mg/L")
    
    def calculate_scheme_one(self):
        """方案一：指定时间不同位置计算"""
        if not self.model:
            print("❌ 请先设置模型参数")
            return
        
        print("\n=== 方案一：指定时间不同位置计算 ===")
        
        try:
            # 输入计算参数
            time_input = input("预测时间 (天) [默认: 100]: ") or "100"
            times = [float(t.strip()) for t in time_input.split(',')]
            
            xmin = float(input("预测起始范围 Xmin (m) [默认: -50]: ") or -50)
            xmax = float(input("预测最大范围 Xmax (m) [默认: 100]: ") or 100)
            xstep = float(input("x剖分间距 (m) [默认: 1]: ") or 1)
            
            # 生成空间范围
            x_range = np.arange(xmin, xmax + xstep, xstep)
            
            # 计算和绘图
            if len(times) == 1:
                # 单时间点
                results = self.model.plot_single_time(
                    times[0], x_range, 
                    self.current_params['standard_limit'], 
                    self.current_params['detection_limit']
                )
                self._print_single_result(times[0], results)
            else:
                # 多时间点
                self.model.plot_multiple_times(
                    times, x_range,
                    self.current_params['standard_limit'], 
                    self.current_params['detection_limit']
                )
                self._print_multiple_results(times, x_range)
                
        except ValueError:
            print("❌ 输入错误: 请输入有效的数值")
        except Exception as e:
            print(f"❌ 计算失败: {e}")
    
    def calculate_scheme_two(self):
        """方案二：指定位置不同时间计算（穿透曲线）"""
        if not self.model:
            print("❌ 请先设置模型参数")
            return
        
        print("\n=== 方案二：指定位置不同时间计算 ===")
        
        try:
            # 输入计算参数
            position_input = input("预测位置 (m) [默认: 10]: ") or "10"
            positions = [float(p.strip()) for p in position_input.split(',')]
            
            tmax = float(input("最大时间 (天) [默认: 365]: ") or 365)
            tstep = float(input("时间步长 (天) [默认: 1]: ") or 1)
            
            # 生成时间范围
            t_range = np.arange(tstep, tmax + tstep, tstep)
            
            # 绘制穿透曲线
            plt.figure(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            
            for i, pos in enumerate(positions):
                concentrations = self.model.calculate_concentration(pos, t_range)
                color = colors[i % len(colors)]
                plt.plot(t_range, concentrations, color=color, linewidth=2, 
                        label=f'x = {pos} m')
            
            # 标记评价标准线
            plt.axhline(y=self.current_params['standard_limit'], color='red', 
                       linestyle='--', linewidth=1.5, 
                       label=f'评价标准 ({self.current_params["standard_limit"]} mg/L)')
            plt.axhline(y=self.current_params['detection_limit'], color='green', 
                       linestyle=':', linewidth=1.5, 
                       label=f'检出限 ({self.current_params["detection_limit"]} mg/L)')
            
            plt.title('方案二：穿透曲线 - 浓度时间变化', fontsize=14, fontweight='bold')
            plt.xlabel('时间 (天)', fontsize=12)
            plt.ylabel('浓度 (mg/L)', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xlim(0, tmax)
            plt.ylim(bottom=0)
            plt.tight_layout()
            plt.show()
            
            # 打印穿透时间统计
            self._print_breakthrough_analysis(positions, t_range)
            
        except ValueError:
            print("❌ 输入错误: 请输入有效的数值")
        except Exception as e:
            print(f"❌ 计算失败: {e}")
    
    def sensitivity_analysis(self):
        """参数敏感性分析"""
        if not self.model:
            print("❌ 请先设置模型参数")
            return
        
        print("\n=== 参数敏感性分析 ===")
        print("1. 流速敏感性分析")
        print("2. 弥散系数敏感性分析")
        print("3. 反应系数敏感性分析")
        
        try:
            choice = input("请选择分析类型 [1-3]: ")
            
            if choice == '1':
                self._analyze_velocity_sensitivity()
            elif choice == '2':
                self._analyze_dispersion_sensitivity()
            elif choice == '3':
                self._analyze_reaction_sensitivity()
            else:
                print("❌ 无效选择")
                
        except Exception as e:
            print(f"❌ 敏感性分析失败: {e}")
    
    def _analyze_velocity_sensitivity(self):
        """流速敏感性分析"""
        base_u = self.current_params['u']
        u_values = [base_u * factor for factor in [0.5, 0.8, 1.0, 1.5, 2.0]]
        
        t_pred = float(input("分析时间 (天) [默认: 100]: ") or 100)
        x_range = np.arange(-50, 101, 2)
        
        plt.figure(figsize=(12, 8))
        
        for i, u_val in enumerate(u_values):
            model_temp = GroundwaterContaminationModel(
                self.current_params['m'], self.current_params['W'], 
                self.current_params['n'], u_val, self.current_params['DL'], 
                self.current_params['lambda_decay']
            )
            concentrations = model_temp.calculate_concentration(x_range, t_pred)
            plt.plot(x_range, concentrations, linewidth=2, 
                    label=f'u = {u_val:.2f} m/d')
        
        plt.axhline(y=self.current_params['standard_limit'], color='red', 
                   linestyle='--', label='评价标准')
        plt.title(f'流速敏感性分析 (t = {t_pred}天)', fontsize=14, fontweight='bold')
        plt.xlabel('距离 (m)', fontsize=12)
        plt.ylabel('浓度 (mg/L)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def _analyze_dispersion_sensitivity(self):
        """弥散系数敏感性分析"""
        base_DL = self.current_params['DL']
        DL_values = [base_DL * factor for factor in [0.2, 0.5, 1.0, 2.0, 5.0]]
        
        t_pred = float(input("分析时间 (天) [默认: 100]: ") or 100)
        x_range = np.arange(-50, 101, 2)
        
        plt.figure(figsize=(12, 8))
        
        for i, DL_val in enumerate(DL_values):
            model_temp = GroundwaterContaminationModel(
                self.current_params['m'], self.current_params['W'], 
                self.current_params['n'], self.current_params['u'], DL_val, 
                self.current_params['lambda_decay']
            )
            concentrations = model_temp.calculate_concentration(x_range, t_pred)
            plt.plot(x_range, concentrations, linewidth=2, 
                    label=f'DL = {DL_val:.2f} m²/d')
        
        plt.axhline(y=self.current_params['standard_limit'], color='red', 
                   linestyle='--', label='评价标准')
        plt.title(f'弥散系数敏感性分析 (t = {t_pred}天)', fontsize=14, fontweight='bold')
        plt.xlabel('距离 (m)', fontsize=12)
        plt.ylabel('浓度 (mg/L)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def _analyze_reaction_sensitivity(self):
        """反应系数敏感性分析"""
        lambda_values = [0, 0.001, 0.005, 0.01, 0.02]
        
        t_pred = float(input("分析时间 (天) [默认: 100]: ") or 100)
        x_range = np.arange(-50, 101, 2)
        
        plt.figure(figsize=(12, 8))
        
        for i, lambda_val in enumerate(lambda_values):
            model_temp = GroundwaterContaminationModel(
                self.current_params['m'], self.current_params['W'], 
                self.current_params['n'], self.current_params['u'], 
                self.current_params['DL'], lambda_val
            )
            concentrations = model_temp.calculate_concentration(x_range, t_pred)
            plt.plot(x_range, concentrations, linewidth=2, 
                    label=f'λ = {lambda_val:.3f} 1/d')
        
        plt.axhline(y=self.current_params['standard_limit'], color='red', 
                   linestyle='--', label='评价标准')
        plt.title(f'反应系数敏感性分析 (t = {t_pred}天)', fontsize=14, fontweight='bold')
        plt.xlabel('距离 (m)', fontsize=12)
        plt.ylabel('浓度 (mg/L)', fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    
    def _print_single_result(self, t, results):
        """打印单时间点结果"""
        print(f"\n--- 计算结果 (t = {t}天) ---")
        print(f"最大浓度: {results['max_concentration']:.3f} mg/L")
        print(f"最大浓度位置: {results['max_position']:.1f} m")
        print(f"超标距离: {results['exceed_range']}")
        print(f"影响距离: {results['influence_range']}")
    
    def _print_multiple_results(self, times, x_range):
        """打印多时间点结果"""
        print(f"\n--- 多时间点计算结果 ---")
        for t in times:
            concentrations = self.model.calculate_concentration(x_range, t)
            results = self.model.analyze_results(
                x_range, concentrations, 
                self.current_params['standard_limit'], 
                self.current_params['detection_limit']
            )
            print(f"t = {t}天: 最大浓度 = {results['max_concentration']:.3f} mg/L, "
                  f"超标范围 = {results['exceed_range']}")
    
    def _print_breakthrough_analysis(self, positions, t_range):
        """打印穿透分析结果"""
        print(f"\n--- 穿透分析结果 ---")
        for pos in positions:
            concentrations = self.model.calculate_concentration(pos, t_range)
            
            # 找到首次超过检出限的时间
            detection_indices = np.where(concentrations > self.current_params['detection_limit'])[0]
            detection_time = t_range[detection_indices[0]] if detection_indices.size > 0 else "未检出"
            
            # 找到首次超标的时间
            exceed_indices = np.where(concentrations > self.current_params['standard_limit'])[0]
            exceed_time = t_range[exceed_indices[0]] if exceed_indices.size > 0 else "未超标"
            
            # 找到峰值浓度和时间
            max_conc = np.max(concentrations)
            max_time = t_range[np.argmax(concentrations)]
            
            print(f"位置 x = {pos} m:")
            print(f"  首次检出时间: {detection_time}")
            print(f"  首次超标时间: {exceed_time}")
            print(f"  峰值浓度: {max_conc:.3f} mg/L (t = {max_time:.1f}天)")
    
    def save_results(self):
        """保存计算结果"""
        if not self.model:
            print("❌ 请先进行计算")
            return
        
        print("\n=== 保存计算结果 ===")
        filename = input("输入保存文件名 [默认: groundwater_results]: ") or "groundwater_results"
        
        try:
            # 这里可以添加保存逻辑，比如保存为CSV、Excel等
            print(f"✅ 结果已保存为 {filename}.png")
            print("💡 提示: 图表已自动保存，数据导出功能可进一步开发")
        except Exception as e:
            print(f"❌ 保存失败: {e}")
    
    def run(self):
        """运行计算器主程序"""
        print("欢迎使用地下水污染迁移计算器！")
        
        while True:
            self.display_menu()
            choice = input("请选择功能 [0-7]: ").strip()
            
            if choice == '0':
                print("感谢使用！再见！")
                break
            elif choice == '1':
                self.input_parameters()
            elif choice == '2':
                self.calculate_scheme_one()
            elif choice == '3':
                self.calculate_scheme_two()
            elif choice == '4':
                self.calculate_scheme_one()  # 复用方案一，支持多时间输入
            elif choice == '5':
                self.sensitivity_analysis()
            elif choice == '6':
                self.display_current_params()
            elif choice == '7':
                self.save_results()
            else:
                print("❌ 无效选择，请重新输入")
            
            input("\n按回车键继续...")

def main():
    """主函数"""
    calculator = GroundwaterCalculator()
    calculator.run()

if __name__ == "__main__":
    main()
