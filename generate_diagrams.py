# -*- coding: utf-8 -*-
"""
生成视距计算示意图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial']
plt.rcParams['axes.unicode_minus'] = False

output_dir = Path("assets/diagrams")
output_dir.mkdir(parents=True, exist_ok=True)

# ==================== 图1: 仰角计算示意图 ====================
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.set_aspect('equal')
ax.axis('off')

# 地球曲率
earth_radius = 100
theta_range = np.linspace(-0.1, 0.15, 100)
earth_x = earth_radius * np.sin(theta_range)
earth_y = earth_radius * np.cos(theta_range) - earth_radius
ax.plot(earth_x, earth_y, 'brown', linewidth=3, label='地球表面')
ax.fill_between(earth_x, earth_y, -20, color='lightgray', alpha=0.3)

# 天线位置
antenna_x = 0
antenna_h = 0.5
ax.plot([antenna_x, antenna_x], [0, antenna_h], 'b-', linewidth=4, label='天线')
ax.plot(antenna_x, antenna_h, 'bo', markersize=10)

# 目标位置
target_dist = 50
target_h = 10
# 考虑地球曲率
target_x = target_dist
target_y = target_h - (target_dist**2) / (2 * earth_radius)
ax.plot(target_x, target_y, 'r^', markersize=15, label='目标 (无人机)')

# 视线
ax.plot([antenna_x, target_x], [antenna_h, target_y], 'g--', linewidth=2, label='视线')

# 水平线
ax.plot([antenna_x, target_dist], [antenna_h, antenna_h], 'k:', linewidth=1, alpha=0.5)

# 仰角标注
angle_arc = patches.Arc((antenna_x, antenna_h), 15, 15, angle=0, 
                         theta1=0, theta2=np.degrees(np.arctan((target_y-antenna_h)/target_dist)),
                         color='blue', linewidth=2)
ax.add_patch(angle_arc)

# 标注
ax.annotate('h₁\n(天线高度)', xy=(antenna_x, antenna_h/2), 
            xytext=(-10, antenna_h/2), fontsize=11, ha='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

ax.annotate('h₂\n(目标高度)', xy=(target_x, target_y/2), 
            xytext=(target_x+5, target_y/2), fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

ax.annotate('d (水平距离)', xy=(target_dist/2, -2), fontsize=12, ha='center',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

ax.annotate('θ\n(仰角)', xy=(antenna_x+8, antenna_h+2), fontsize=12, color='blue',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))

ax.set_xlim(-15, 65)
ax.set_ylim(-15, 20)
ax.set_title('目标仰角计算示意图', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(output_dir / 'elevation_angle.png', bbox_inches='tight', facecolor='white')
# print("仰角计算示意图已生成")
plt.close()

# ==================== 图2: 地球曲率视距示意图 ====================
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.set_aspect('equal')
ax.axis('off')

# 地球
earth_radius = 80
theta_range = np.linspace(-0.3, 0.3, 100)
earth_x = earth_radius * np.sin(theta_range)
earth_y = earth_radius * np.cos(theta_range) - earth_radius
ax.plot(earth_x, earth_y, 'brown', linewidth=3)
ax.fill_between(earth_x, earth_y, -20, color='lightgray', alpha=0.3)

# 天线
antenna_h = 8
ax.plot([0, 0], [0, antenna_h], 'b-', linewidth=4)
ax.plot(0, antenna_h, 'bo', markersize=10)

# 视距切线
horizon_angle = np.sqrt(2 * antenna_h / earth_radius)
horizon_x = earth_radius * np.sin(horizon_angle)
horizon_y = earth_radius * np.cos(horizon_angle) - earth_radius

ax.plot([0, horizon_x], [antenna_h, horizon_y], 'r--', linewidth=2, label='视线方向')
ax.plot(horizon_x, horizon_y, 'ro', markersize=8)

# 视距弧线
arc_theta = np.linspace(0, horizon_angle, 30)
arc_x = earth_radius * np.sin(arc_theta)
arc_y = earth_radius * np.cos(arc_theta) - earth_radius
ax.plot(arc_x, arc_y, 'orange', linewidth=3, label='视距范围')

# 标注
ax.annotate('h\n(天线高度)', xy=(0, antenna_h/2), 
            xytext=(-12, antenna_h/2), fontsize=12, ha='right',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

ax.annotate('d (视距)', xy=(horizon_x/2-5, 5), fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))

ax.annotate('地平线', xy=(horizon_x, horizon_y), 
            xytext=(horizon_x+5, horizon_y-3), fontsize=11,
            arrowprops=dict(arrowstyle='->', color='red'))

ax.set_xlim(-20, 60)
ax.set_ylim(-15, 15)
ax.set_title('地球曲率视距示意图', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(output_dir / 'horizon_distance.png', bbox_inches='tight', facecolor='white')
# print("地球曲率视距示意图已生成")
plt.close()

# ==================== 图3: 双站视距示意图 ====================
fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
ax.set_aspect('equal')
ax.axis('off')

# 地球
earth_radius = 60
theta_range = np.linspace(-0.5, 0.5, 100)
earth_x = earth_radius * np.sin(theta_range)
earth_y = earth_radius * np.cos(theta_range) - earth_radius
ax.plot(earth_x, earth_y, 'brown', linewidth=3)
ax.fill_between(earth_x, earth_y, -15, color='lightgray', alpha=0.3)

# 站点1
h1 = 5
ax.plot([-25, -25], [-(25**2)/(2*earth_radius), -(25**2)/(2*earth_radius) + h1], 
        'b-', linewidth=4)
ax.plot(-25, -(25**2)/(2*earth_radius) + h1, 'bo', markersize=10)

# 站点2
h2 = 10
ax.plot([40, 40], [-(40**2)/(2*earth_radius), -(40**2)/(2*earth_radius) + h2],
        'b-', linewidth=4)
ax.plot(40, -(40**2)/(2*earth_radius) + h2, 'bo', markersize=10)

# 视线
ax.plot([-25, 40], [-(25**2)/(2*earth_radius) + h1, -(40**2)/(2*earth_radius) + h2],
        'g--', linewidth=2, label='视线')

# 标注
ax.annotate('站点1\nh₁', xy=(-25, -(25**2)/(2*earth_radius) + h1), 
            xytext=(-35, 5), fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='blue'))

ax.annotate('站点2\nh₂', xy=(40, -(40**2)/(2*earth_radius) + h2), 
            xytext=(48, 8), fontsize=11,
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
            arrowprops=dict(arrowstyle='->', color='blue'))

ax.annotate('d_max (最大通视距离)', xy=(7.5, 6), fontsize=12, ha='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))

ax.set_xlim(-45, 55)
ax.set_ylim(-15, 15)
ax.set_title('双站视距示意图', fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig(output_dir / 'two_station.png', bbox_inches='tight', facecolor='white')
# print("双站视距示意图已生成")
plt.close()

# print("全部示意图生成完成！存储路径: assets/diagrams/")
