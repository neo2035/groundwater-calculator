import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from groundwater_contamination_model import GroundwaterContaminationModel, setup_chinese_font
import io
import base64

# 设置页面配置
st.set_page_config(
    page_title="地下水污染迁移计算器",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 设置中文字体
setup_chinese_font()

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 主标题
st.markdown('<h1 class="main-header">💧 地下水污染迁移计算器</h1>', unsafe_allow_html=True)

# 侧边栏 - 参数设置
st.sidebar.header("🔧 模型参数设置")

# 基本物理参数
st.sidebar.subheader("基本物理参数")
m = st.sidebar.number_input("污染物泄漏质量 m (g)", min_value=0.1, max_value=10000.0, value=100.0, step=10.0)
W = st.sidebar.number_input("横截面积 W (m²)", min_value=0.1, max_value=1000.0, value=2.0, step=0.1)
n = st.sidebar.slider("有效孔隙度 n", min_value=0.01, max_value=0.99, value=0.3, step=0.01)
u = st.sidebar.number_input("地下水实际流速 u (m/d)", min_value=0.001, max_value=10.0, value=0.1, step=0.01)
DL = st.sidebar.number_input("纵向弥散系数 DL (m²/d)", min_value=0.001, max_value=100.0, value=0.5, step=0.1)
lambda_decay = st.sidebar.number_input("反应系数 λ (1/d)", min_value=0.0, max_value=1.0, value=0.0, step=0.001, format="%.3f")

# 评价标准参数
st.sidebar.subheader("评价标准")
standard_limit = st.sidebar.number_input("评价标准 (mg/L)", min_value=0.001, max_value=100.0, value=0.5, step=0.01)
detection_limit = st.sidebar.number_input("检出限 (mg/L)", min_value=0.001, max_value=10.0, value=0.05, step=0.01)

# 计算范围设置
st.sidebar.subheader("计算设置")
xmin = st.sidebar.number_input("起始位置 (m)", min_value=-1000.0, max_value=1000.0, value=-50.0, step=10.0)
xmax = st.sidebar.number_input("结束位置 (m)", min_value=-1000.0, max_value=1000.0, value=100.0, step=10.0)
xstep = st.sidebar.selectbox("空间步长 (m)", options=[0.5, 1.0, 2.0, 5.0], index=1)

# 预设参数方案
st.sidebar.subheader("🎯 预设方案")
preset = st.sidebar.selectbox("选择预设参数", [
    "自定义",
    "典型砂土含水层",
    "粘土含水层", 
    "裂隙岩石含水层",
    "高渗透性含水层"
])

if preset != "自定义":
    if preset == "典型砂土含水层":
        m, W, n, u, DL = 100.0, 2.0, 0.25, 0.5, 1.0
    elif preset == "粘土含水层":
        m, W, n, u, DL = 100.0, 2.0, 0.15, 0.01, 0.1
    elif preset == "裂隙岩石含水层":
        m, W, n, u, DL = 100.0, 2.0, 0.05, 1.0, 5.0
    elif preset == "高渗透性含水层":
        m, W, n, u, DL = 100.0, 2.0, 0.35, 2.0, 10.0
    
    st.sidebar.info(f"已加载 {preset} 参数")

# 创建模型实例
try:
    model = GroundwaterContaminationModel(m, W, n, u, DL, lambda_decay)
    model_created = True
except Exception as e:
    st.error(f"参数错误: {e}")
    model_created = False

# 主界面标签页
if model_created:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 空间分布分析", "📈 时间变化分析", "🔍 敏感性分析", "📋 参数总览"])
    
    # 标签页1: 空间分布分析
    with tab1:
        st.header("方案一：指定时间的空间浓度分布")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("时间设置")
            time_mode = st.radio("选择时间模式", ["单一时间", "多时间对比"])
            
            if time_mode == "单一时间":
                t_single = st.number_input("预测时间 (天)", min_value=1.0, max_value=3650.0, value=100.0, step=1.0)
                times = [t_single]
            else:
                t1 = st.number_input("时间1 (天)", min_value=1.0, max_value=3650.0, value=100.0, step=1.0)
                t2 = st.number_input("时间2 (天)", min_value=1.0, max_value=3650.0, value=200.0, step=1.0)
                t3 = st.number_input("时间3 (天)", min_value=1.0, max_value=3650.0, value=300.0, step=1.0)
                times = [t1, t2, t3]
        
        with col2:
            # 生成空间范围
            x_range = np.arange(xmin, xmax + xstep, xstep)
            
            # 创建图表
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            linestyles = ['-', '--', '-.', ':', '-']
            
            results_list = []
            
            for i, t in enumerate(times):
                concentrations = model.calculate_concentration(x_range, t)
                results = model.analyze_results(x_range, concentrations, standard_limit, detection_limit)
                results_list.append((t, results))
                
                color = colors[i % len(colors)]
                linestyle = linestyles[i % len(linestyles)]
                
                ax.plot(x_range, concentrations, color=color, linestyle=linestyle, 
                       linewidth=2.5, label=f't = {t}天')
            
            # 添加评价标准线
            ax.axhline(y=standard_limit, color='red', linestyle='--', linewidth=2, 
                      label=f'评价标准 ({standard_limit} mg/L)')
            ax.axhline(y=detection_limit, color='green', linestyle=':', linewidth=2, 
                      label=f'检出限 ({detection_limit} mg/L)')
            
            # 标记关键位置
            if len(times) == 1:
                plume_center = u * times[0]
                ax.axvline(x=plume_center, color='gray', linestyle='-', alpha=0.7, 
                          label=f'污染羽中心 (x={plume_center:.1f}m)')
            
            ax.axvline(x=0, color='black', linestyle='-', linewidth=2, label='注入点 (x=0)')
            
            ax.set_title('污染物浓度空间分布', fontsize=16, fontweight='bold')
            ax.set_xlabel('距离 (m)', fontsize=14)
            ax.set_ylabel('浓度 (mg/L)', fontsize=14)
            ax.legend(fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(bottom=0)
            
            st.pyplot(fig)
        
        # 显示计算结果
        st.subheader("📊 计算结果统计")
        
        if len(times) == 1:
            t, results = results_list[0]
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("最大浓度", f"{results['max_concentration']:.3f} mg/L")
            with col2:
                st.metric("最大浓度位置", f"{results['max_position']:.1f} m")
            with col3:
                st.metric("超标范围", results['exceed_range'])
            with col4:
                st.metric("影响范围", results['influence_range'])
        else:
            # 多时间点结果表格
            df_results = pd.DataFrame([
                {
                    "时间 (天)": t,
                    "最大浓度 (mg/L)": f"{results['max_concentration']:.3f}",
                    "最大浓度位置 (m)": f"{results['max_position']:.1f}",
                    "超标范围": results['exceed_range'],
                    "影响范围": results['influence_range']
                }
                for t, results in results_list
            ])
            st.dataframe(df_results, use_container_width=True)
    
    # 标签页2: 时间变化分析
    with tab2:
        st.header("方案二：指定位置的时间浓度变化")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("位置设置")
            position_mode = st.radio("选择位置模式", ["单一位置", "多位置对比"])
            
            if position_mode == "单一位置":
                x_single = st.number_input("监测位置 (m)", min_value=xmin, max_value=xmax, value=10.0, step=1.0)
                positions = [x_single]
            else:
                x1 = st.number_input("位置1 (m)", min_value=xmin, max_value=xmax, value=5.0, step=1.0)
                x2 = st.number_input("位置2 (m)", min_value=xmin, max_value=xmax, value=10.0, step=1.0)
                x3 = st.number_input("位置3 (m)", min_value=xmin, max_value=xmax, value=20.0, step=1.0)
                positions = [x1, x2, x3]
            
            tmax = st.number_input("最大时间 (天)", min_value=10.0, max_value=3650.0, value=365.0, step=10.0)
            tstep = st.selectbox("时间步长 (天)", options=[0.5, 1.0, 2.0, 5.0], index=1)
        
        with col2:
            # 生成时间范围
            t_range = np.arange(tstep, tmax + tstep, tstep)
            
            # 创建穿透曲线图
            fig, ax = plt.subplots(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple']
            
            breakthrough_results = []
            
            for i, pos in enumerate(positions):
                concentrations = model.calculate_concentration(pos, t_range)
                color = colors[i % len(colors)]
                ax.plot(t_range, concentrations, color=color, linewidth=2.5, 
                       label=f'x = {pos} m')
                
                # 计算穿透时间
                detection_indices = np.where(concentrations > detection_limit)[0]
                detection_time = t_range[detection_indices[0]] if detection_indices.size > 0 else None
                
                exceed_indices = np.where(concentrations > standard_limit)[0]
                exceed_time = t_range[exceed_indices[0]] if exceed_indices.size > 0 else None
                
                max_conc = np.max(concentrations)
                max_time = t_range[np.argmax(concentrations)]
                
                breakthrough_results.append({
                    "位置 (m)": pos,
                    "首次检出时间 (天)": detection_time if detection_time else "未检出",
                    "首次超标时间 (天)": exceed_time if exceed_time else "未超标",
                    "峰值浓度 (mg/L)": f"{max_conc:.3f}",
                    "峰值时间 (天)": f"{max_time:.1f}"
                })
            
            # 添加评价标准线
            ax.axhline(y=standard_limit, color='red', linestyle='--', linewidth=2, 
                      label=f'评价标准 ({standard_limit} mg/L)')
            ax.axhline(y=detection_limit, color='green', linestyle=':', linewidth=2, 
                      label=f'检出限 ({detection_limit} mg/L)')
            
            ax.set_title('污染物浓度时间变化（穿透曲线）', fontsize=16, fontweight='bold')
            ax.set_xlabel('时间 (天)', fontsize=14)
            ax.set_ylabel('浓度 (mg/L)', fontsize=14)
            ax.legend(fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, tmax)
            ax.set_ylim(bottom=0)
            
            st.pyplot(fig)
        
        # 显示穿透分析结果
        st.subheader("📈 穿透分析结果")
        df_breakthrough = pd.DataFrame(breakthrough_results)
        st.dataframe(df_breakthrough, use_container_width=True)
    
    # 标签页3: 敏感性分析
    with tab3:
        st.header("参数敏感性分析")
        
        sensitivity_param = st.selectbox("选择敏感性分析参数", [
            "地下水流速 (u)",
            "纵向弥散系数 (DL)", 
            "反应系数 (λ)"
        ])
        
        analysis_time = st.number_input("分析时间 (天)", min_value=1.0, max_value=1000.0, value=100.0, step=1.0)
        
        # 生成敏感性分析图
        fig, ax = plt.subplots(figsize=(12, 8))
        x_range_sens = np.arange(-50, 101, 2)
        
        if sensitivity_param == "地下水流速 (u)":
            base_value = u
            factors = [0.5, 0.8, 1.0, 1.5, 2.0]
            param_name = "u"
            unit = "m/d"
            
            for factor in factors:
                test_value = base_value * factor
                model_temp = GroundwaterContaminationModel(m, W, n, test_value, DL, lambda_decay)
                concentrations = model_temp.calculate_concentration(x_range_sens, analysis_time)
                ax.plot(x_range_sens, concentrations, linewidth=2.5, 
                       label=f'{param_name} = {test_value:.2f} {unit}')
        
        elif sensitivity_param == "纵向弥散系数 (DL)":
            base_value = DL
            factors = [0.2, 0.5, 1.0, 2.0, 5.0]
            param_name = "DL"
            unit = "m²/d"
            
            for factor in factors:
                test_value = base_value * factor
                model_temp = GroundwaterContaminationModel(m, W, n, u, test_value, lambda_decay)
                concentrations = model_temp.calculate_concentration(x_range_sens, analysis_time)
                ax.plot(x_range_sens, concentrations, linewidth=2.5, 
                       label=f'{param_name} = {test_value:.2f} {unit}')
        
        elif sensitivity_param == "反应系数 (λ)":
            test_values = [0, 0.001, 0.005, 0.01, 0.02]
            param_name = "λ"
            unit = "1/d"
            
            for test_value in test_values:
                model_temp = GroundwaterContaminationModel(m, W, n, u, DL, test_value)
                concentrations = model_temp.calculate_concentration(x_range_sens, analysis_time)
                ax.plot(x_range_sens, concentrations, linewidth=2.5, 
                       label=f'{param_name} = {test_value:.3f} {unit}')
        
        ax.axhline(y=standard_limit, color='red', linestyle='--', linewidth=2, label='评价标准')
        ax.axhline(y=detection_limit, color='green', linestyle=':', linewidth=2, label='检出限')
        
        ax.set_title(f'{sensitivity_param} 敏感性分析 (t = {analysis_time}天)', fontsize=16, fontweight='bold')
        ax.set_xlabel('距离 (m)', fontsize=14)
        ax.set_ylabel('浓度 (mg/L)', fontsize=14)
        ax.legend(fontsize=12)
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        
        st.info("💡 敏感性分析帮助您了解不同参数对污染迁移的影响程度，为参数校正和不确定性分析提供依据。")
    
    # 标签页4: 参数总览
    with tab4:
        st.header("📋 当前模型参数总览")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔧 物理参数")
            params_df = pd.DataFrame({
                "参数": ["污染物质量", "横截面积", "有效孔隙度", "地下水流速", "纵向弥散系数", "反应系数"],
                "符号": ["m", "W", "n", "u", "DL", "λ"],
                "数值": [m, W, n, u, DL, lambda_decay],
                "单位": ["g", "m²", "-", "m/d", "m²/d", "1/d"]
            })
            st.dataframe(params_df, use_container_width=True)
        
        with col2:
            st.subheader("📏 评价标准")
            standards_df = pd.DataFrame({
                "标准": ["评价标准", "检出限"],
                "数值": [standard_limit, detection_limit],
                "单位": ["mg/L", "mg/L"]
            })
            st.dataframe(standards_df, use_container_width=True)
            
            st.subheader("📐 计算设置")
            settings_df = pd.DataFrame({
                "设置": ["起始位置", "结束位置", "空间步长"],
                "数值": [xmin, xmax, xstep],
                "单位": ["m", "m", "m"]
            })
            st.dataframe(settings_df, use_container_width=True)
        
        # 模型方程显示
        st.subheader("📐 数学模型")
        st.latex(r'''
        c(x,t) = \frac{m}{2nW\sqrt{\pi D_L t}} \exp\left[-\lambda t - \frac{(x-ut)^2}{4D_L t}\right]
        ''')
        
        st.markdown("""
        **方程说明：**
        - **对流项**: $(x-ut)$ 表示污染羽随地下水流动的迁移
        - **弥散项**: $D_L$ 控制污染物的扩散程度
        - **反应项**: $\lambda$ 表示污染物的降解或反应速率
        """)
        
        # 导出功能
        st.subheader("💾 结果导出")
        
        if st.button("📊 导出当前参数配置"):
            config_data = {
                "模型参数": {
                    "污染物质量_g": m,
                    "横截面积_m2": W,
                    "有效孔隙度": n,
                    "地下水流速_m_per_d": u,
                    "纵向弥散系数_m2_per_d": DL,
                    "反应系数_per_d": lambda_decay
                },
                "评价标准": {
                    "评价标准_mg_per_L": standard_limit,
                    "检出限_mg_per_L": detection_limit
                },
                "计算设置": {
                    "起始位置_m": xmin,
                    "结束位置_m": xmax,
                    "空间步长_m": xstep
                }
            }
            
            # 转换为JSON字符串
            import json
            config_json = json.dumps(config_data, ensure_ascii=False, indent=2)
            
            st.download_button(
                label="下载参数配置文件",
                data=config_json,
                file_name="groundwater_model_config.json",
                mime="application/json"
            )
            
            st.success("✅ 参数配置已准备好下载！")

else:
    st.error("❌ 请检查参数设置，确保所有参数都在合理范围内。")

# 页脚信息
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    💧 地下水污染迁移计算器 | 基于一维瞬时泄漏ADR模型 | 
    <a href='https://streamlit.io' target='_blank'>Powered by Streamlit</a>
</div>
""", unsafe_allow_html=True)
