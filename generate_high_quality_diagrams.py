# -*- coding: utf-8 -*-
"""
生成高质量视距计算示意图 (High-Quality RF Diagrams) - V2 Enhanced Visibility
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
import numpy as np
from pathlib import Path
from matplotlib.colors import LinearSegmentedColormap

# 设置中文字体和绘图风格
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300  # 高分辨率

output_dir = Path("assets/diagrams")
output_dir.mkdir(parents=True, exist_ok=True)

def create_gradient_background(ax, color_top, color_bottom):
    """创建渐变背景"""
    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))
    
    # 自定义色彩映射
    cmap = LinearSegmentedColormap.from_list('bg_gradient', [color_bottom, color_top])
    
    ax.imshow(gradient, aspect='auto', extent=[ax.get_xlim()[0], ax.get_xlim()[1], 
                                               ax.get_ylim()[0], ax.get_ylim()[1]], 
              cmap=cmap, origin='lower', zorder=-10)

def draw_earth_surface(ax, radius=100, center=(0, -100), width=200):
    """绘制带装饰的地球表面"""
    theta = np.linspace(-0.5, 0.5, 200)
    x = radius * np.sin(theta) + center[0]
    y = radius * np.cos(theta) + center[1]
    
    # 地面填充
    ax.fill_between(x, y, -400, color='#E8F5E9', zorder=-5) # 浅绿背景
    ax.plot(x, y, color='#2E7D32', linewidth=3, zorder=-4) # 地面轮廓 加粗
    
    # 添加经纬网格感
    for i in range(-5, 6):
        offset = i * 20
        ax.plot([offset, center[0]], [-20, center[1]], color='white', linewidth=1.5, alpha=0.4, zorder=-4)

def draw_antenna_tower(ax, x, y, h, color='#1976D2', label=None):
    """绘制精细的天线塔"""
    # 塔身 (三角形结构)
    tower_width = h * 0.4  # 加宽
    tower = patches.Polygon([
        (x - tower_width/2, y),
        (x + tower_width/2, y),
        (x, y + h)
    ], closed=True, facecolor='white', edgecolor=color, linewidth=2.5, zorder=5) # 加粗
    ax.add_patch(tower)
    
    # 内部交叉线
    ax.plot([x - tower_width/4, x + tower_width/4], [y + h/3, y + h/3], color=color, linewidth=1.5, zorder=5)
    ax.plot([x - tower_width/8, x + tower_width/8], [y + 2*h/3, y + 2*h/3], color=color, linewidth=1.5, zorder=5)
    
    # 天线罩/顶部
    ax.plot(x, y+h, marker='o', color='gold', markersize=9, markeredgecolor=color, markeredgewidth=1.5, zorder=6) # 加大
    
    # 标签
    if label:
        txt = ax.text(x, y + h + 3, label, ha='center', va='bottom', fontsize=14, fontweight='bold', color='#333333', zorder=10) # 字号增大
        txt.set_path_effects([path_effects.withStroke(linewidth=4, foreground='white')])

def draw_drone(ax, x, y, size=3, label=None): # 尺寸加大
    """绘制简单的无人机图标"""
    # 机身中心
    ax.add_patch(patches.Circle((x, y), size/2, color='#D32F2F', zorder=5))
    
    # 旋翼臂
    ax.plot([x-size, x+size], [y, y], color='#333', linewidth=2, zorder=5)
    ax.plot([x, x], [y-size, y+size], color='#333', linewidth=2, zorder=5)
    
    # 旋翼
    for dx, dy in [(-size, 0), (size, 0), (0, -size), (0, size)]:
        ax.add_patch(patches.Ellipse((x+dx, y+dy), size, size/3, color='#555', alpha=0.6, zorder=4))
        
    # 标签
    if label:
        txt = ax.text(x, y + size + 3, label, ha='center', va='bottom', fontsize=14, fontweight='bold', color='#D32F2F', zorder=10)
        txt.set_path_effects([path_effects.withStroke(linewidth=4, foreground='white')])

def setup_diagram(title):
    """初始化绘图环境"""
    fig, ax = plt.subplots(figsize=(12, 7)) # 尺寸加大
    ax.set_aspect('equal')
    ax.axis('off')
    
    # 设置显示范围以便绘制背景 (根据具体图调整)
    
    return fig, ax

# ==================== 1. 目标仰角计算 ====================
fig, ax = setup_diagram("目标仰角计算模型 (Elevation Analysis)")
ax.set_xlim(-20, 80)
ax.set_ylim(-20, 40)
create_gradient_background(ax, '#E3F2FD', '#FFFFFF')

plt.title("目标仰角计算模型 (Elevation Analysis)", fontsize=20, fontweight='bold', pad=25, color='#37474F')

# 地球
draw_earth_surface(ax, radius=300, center=(0, -300))

# 坐标点
ant_x, ant_y = 0, 0
target_dist = 60
target_y_raw = 25
# 修正后的目标高度位置 (模拟地球下沉效果)
earth_drop = (target_dist**2) / (2 * 300)
target_x = target_dist
target_y = target_y_raw - earth_drop

# 绘制物体
draw_antenna_tower(ax, ant_x, ant_y, 8, label="地面雷达")
draw_drone(ax, target_x, target_y, 3, label="空中目标")

# 视线
line_los = ax.plot([ant_x, target_x], [8, target_y], color='#FF5722', linestyle='--', linewidth=3, zorder=3) # 加粗

# 水平基准线
ax.plot([ant_x, target_dist], [8, 8], color='#90A4AE', linestyle=':', linewidth=2, zorder=2)
ax.text(target_dist+2, 8, "水平线", va='center', fontsize=12, color='#78909C')

# 角度标注
arc = patches.Arc((ant_x, 8), 40, 40, angle=0, theta1=0, 
                 theta2=np.degrees(np.arctan((target_y-8)/target_dist)), 
                 color='#1976D2', linewidth=3, zorder=4)
ax.add_patch(arc)
# 填充角度区域
wedge = patches.Wedge((ant_x, 8), 20, 0, np.degrees(np.arctan((target_y-8)/target_dist)), 
                     color='#2196F3', alpha=0.3, zorder=3)
ax.add_patch(wedge)

ax.text(ant_x + 22, 11, "仰角 θ", fontsize=15, color='#1565C0', fontweight='bold')

# 距离标注
ax.annotate("", xy=(ant_x, -5), xytext=(target_dist, -5),
            arrowprops=dict(arrowstyle='<->', color='#455A64', linewidth=2))
txt = ax.text(target_dist/2, -9, f"地面距离 d = {target_dist}", ha='center', fontsize=14, color='#455A64', fontweight='bold')
txt.set_path_effects([path_effects.withStroke(linewidth=4, foreground='white')])

# 保存
plt.tight_layout()
plt.savefig(output_dir / 'elevation_angle.png', bbox_inches='tight', dpi=300)
plt.close()

# ==================== 2. 地球曲率视距 ====================
fig, ax = setup_diagram("地球曲率视距 (Radio Horizon)")
ax.set_xlim(-30, 70)
ax.set_ylim(-30, 40)
create_gradient_background(ax, '#E3F2FD', '#FFFFFF')

plt.title("地球曲率视距 (Radio Horizon)", fontsize=20, fontweight='bold', pad=25, color='#37474F')

# 地球 (半径更小以夸大效果)
R = 150
center_y = -R
draw_earth_surface(ax, radius=R, center=(0, center_y))

# 天线
ant_h = 12 # 加高以便显示
draw_antenna_tower(ax, 0, 0, ant_h, color='#5E35B1', label="发射塔")

# 视线切线
# 切点位置：d = sqrt(2Rh)
# 这里手动计算切点坐标以便绘图
theta_horizon = np.arccos(R / (R + ant_h))
horizon_x = (R) * np.sin(theta_horizon)
horizon_y = (R) * np.cos(theta_horizon) + center_y

# 绘制视线
ax.plot([0, horizon_x*1.4], [ant_h, horizon_y - (horizon_y-ant_h)*0.4], 
        color='#FF9800', linestyle='--', linewidth=3, zorder=3)

# 标记切点
ax.plot(horizon_x, horizon_y, marker='X', color='#D84315', markersize=12, zorder=5)
ax.text(horizon_x, horizon_y+4, "视距极限\n(Horizon)", ha='center', fontsize=13, fontweight='bold', color='#D84315')

# 标注视距
ax.annotate("", xy=(0, ant_h/2), xytext=(horizon_x, horizon_y + (ant_h-horizon_y)/2),
            arrowprops=dict(arrowstyle='->', color='#5E35B1', linewidth=2, connectionstyle="arc3,rad=-0.2"))
txt = ax.text(horizon_x/2, ant_h + 3, "视线距离 d", ha='center', fontsize=15, color='#5E35B1', fontweight='bold')
txt.set_path_effects([path_effects.withStroke(linewidth=4, foreground='white')])

# 标注地球半径
ax.plot([0, 0], [0, center_y], color='#90A4AE', linestyle='-.', linewidth=1.5)
ax.text(2, center_y/2, "R (地球半径)", ha='left', fontsize=13, color='#607D8B', rotation=90)

plt.tight_layout()
plt.savefig(output_dir / 'horizon_distance.png', bbox_inches='tight', dpi=300)
plt.close()

# ==================== 3. 双站视距 ====================
fig, ax = setup_diagram("双站最大通视距离 (Two-Station LOS)")
ax.set_xlim(-60, 60)
ax.set_ylim(-30, 30)
create_gradient_background(ax, '#E3F2FD', '#FFFFFF')

plt.title("双站最大通视距离 (Two-Station LOS)", fontsize=20, fontweight='bold', pad=25, color='#37474F')

# 地球
R = 200
center_y = -R
draw_earth_surface(ax, radius=R, center=(0, center_y))

# 两个大圆弧上的站点
# 站点1角度
theta1 = -0.15
x1 = R * np.sin(theta1)
y1 = R * np.cos(theta1) + center_y
h1 = 10
# 站点1绘制 (需要旋转) - 这里简化为垂直绘制，因为角度很小
draw_antenna_tower(ax, x1, y1, h1, color='#0277BD', label="站点 A")

# 站点2角度
theta2 = 0.2
x2 = R * np.sin(theta2)
y2 = R * np.cos(theta2) + center_y
h2 = 14
draw_antenna_tower(ax, x2, y2, h2, color='#00695C', label="站点 B")

# 切点 (最高点)
# 视线相切于两站之间
horizon_x = 0
horizon_y = R + center_y # = 0

# 绘制连接线
# 线段1: 站1到切点
ax.plot([x1, horizon_x], [y1+h1, horizon_y], color='#FF5722', linestyle='--', linewidth=3, zorder=3)
# 线段2: 站2到切点
ax.plot([x2, horizon_x], [y2+h2, horizon_y], color='#FF5722', linestyle='--', linewidth=3, zorder=3)

# 标记切点
ax.plot(horizon_x, horizon_y, marker='*', color='#FFC107', markersize=15, markeredgecolor='#FF6F00', zorder=5)

# 标注
ax.text(x1/2, 6, "d1", ha='center', fontsize=14, color='#0277BD', fontweight='bold')
ax.text(x2/2, 7, "d2", ha='center', fontsize=14, color='#00695C', fontweight='bold')

txt = ax.text(0, 12, "最大通视距离 = d1 + d2", ha='center', fontsize=15, fontweight='bold', 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='#FF5722', alpha=0.9))

plt.tight_layout()
plt.savefig(output_dir / 'two_station.png', bbox_inches='tight', dpi=300)
plt.close()
