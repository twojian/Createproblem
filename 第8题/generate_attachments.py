import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.chart import LineChart, Reference, BarChart
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule
import os

BASE = r"d:\Projects\构建难题\第8题"

thin_border = Border(
    left=Side(style='thin'), right=Side(style='thin'),
    top=Side(style='thin'), bottom=Side(style='thin')
)
header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
header_font = Font(name="微软雅黑", bold=True, color="FFFFFF", size=10)
data_font = Font(name="微软雅黑", size=10)

def style_header(ws, row, max_col):
    for col in range(1, max_col + 1):
        cell = ws.cell(row=row, column=col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = thin_border

def style_data(ws, start_row, end_row, max_col):
    for r in range(start_row, end_row + 1):
        for c in range(1, max_col + 1):
            cell = ws.cell(row=r, column=c)
            cell.font = data_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
            cell.border = thin_border

def auto_width(ws, max_col):
    for col in range(1, max_col + 1):
        ws.column_dimensions[get_column_letter(col)].width = 18

def create_attachment5():
    wb = openpyxl.Workbook()

    # Sheet 1: A产线训练日志 (120 epochs)
    ws1 = wb.active
    ws1.title = "A产线训练日志"
    headers = ["Epoch", "TrainLoss", "TrainAcc", "ValLoss", "ValAcc", "LearningRate"]
    for i, h in enumerate(headers, 1):
        ws1.cell(row=1, column=i, value=h)
    style_header(ws1, 1, 6)

    import math, random
    random.seed(42)
    best_val_loss_epoch = 35
    for ep in range(1, 121):
        row = ep + 1
        train_loss = max(0.005, 2.5 * math.exp(-0.025 * ep) + 0.05 * random.random())
        train_acc = min(0.997, 0.65 + 0.35 * (1 - math.exp(-0.06 * ep)) + 0.005 * random.random())
        if ep <= best_val_loss_epoch:
            val_loss = 0.4 + 0.3 * math.exp(-0.06 * ep) + 0.05 * random.random()
            val_acc = 0.55 + 0.25 * (1 - math.exp(-0.06 * ep)) + 0.02 * random.random()
        else:
            overfit_factor = (ep - best_val_loss_epoch) * 0.003
            val_loss = 0.3 + overfit_factor + 0.04 * random.random()
            val_acc = 0.82 - overfit_factor * 2.5 + 0.015 * random.random()
        lr = 0.001 if ep <= 80 else 0.0001 if ep <= 110 else 0.00001

        ws1.cell(row=row, column=1, value=ep)
        ws1.cell(row=row, column=2, value=round(train_loss, 6))
        ws1.cell(row=row, column=3, value=round(train_acc, 4))
        ws1.cell(row=row, column=4, value=round(val_loss, 6))
        ws1.cell(row=row, column=5, value=round(val_acc, 4))
        ws1.cell(row=row, column=6, value=lr)
    style_data(ws1, 2, 121, 6)
    auto_width(ws1, 6)

    chart = LineChart()
    chart.title = "A产线训练-验证 Loss/Acc 曲线"
    chart.y_axis.title = "Loss / Accuracy"
    chart.x_axis.title = "Epoch"
    chart.height = 14
    chart.width = 24
    data_ref = Reference(ws1, min_col=2, max_col=5, min_row=1, max_row=121)
    chart.add_data(data_ref, titles_from_data=True)
    cats = Reference(ws1, min_col=1, min_row=2, max_row=121)
    chart.set_categories(cats)
    ws1.add_chart(chart, "H2")

    # Sheet 2: B产线逐类别评测
    ws2 = wb.create_sheet("B产线逐类别评测")
    headers2 = ["缺陷类别", "Precision", "Recall", "F1-Score", "TP", "FP", "FN", "TN"]
    for i, h in enumerate(headers2, 1):
        ws2.cell(row=1, column=i, value=h)
    style_header(ws2, 1, 8)

    class_data = [
        ("划痕", 0.612, 0.583, 0.597, 245, 155, 175, 2625),
        ("凹坑", 0.548, 0.521, 0.534, 198, 163, 182, 2657),
        ("氧化斑", 0.631, 0.598, 0.614, 215, 126, 145, 2714),
        ("毛刺", 0.502, 0.478, 0.490, 173, 172, 189, 2666),
        ("正常", 0.712, 0.735, 0.723, 1940, 786, 700, 5120),
    ]
    for i, (cls_name, p, r, f1, tp, fp, fn, tn) in enumerate(class_data):
        row = i + 2
        ws2.cell(row=row, column=1, value=cls_name)
        ws2.cell(row=row, column=2, value=round(p, 3))
        ws2.cell(row=row, column=3, value=round(r, 3))
        ws2.cell(row=row, column=4, value=round(f1, 3))
        ws2.cell(row=row, column=5, value=tp)
        ws2.cell(row=row, column=6, value=fp)
        ws2.cell(row=row, column=7, value=fn)
        ws2.cell(row=row, column=8, value=tn)
    style_data(ws2, 2, 6, 8)
    auto_width(ws2, 8)

    # Sheet 3: Checkpoint交叉评测
    ws3 = wb.create_sheet("Checkpoint交叉评测")
    headers3 = ["Epoch", "A产线ValAcc", "B产线ValAcc", "A-B差距"]
    for i, h in enumerate(headers3, 1):
        ws3.cell(row=1, column=i, value=h)
    style_header(ws3, 1, 4)

    for i, ep in enumerate(range(10, 130, 10)):
        row = i + 2
        if ep <= 40:
            a_acc = 0.60 + ep * 0.006 + 0.01 * random.random()
            b_acc = 0.58 + ep * 0.005 + 0.01 * random.random()
        else:
            a_acc = 0.84 - (ep - 40) * 0.003 + 0.01 * random.random()
            b_acc = 0.78 - (ep - 40) * 0.008 + 0.015 * random.random()
        ws3.cell(row=row, column=1, value=ep)
        ws3.cell(row=row, column=2, value=round(a_acc, 4))
        ws3.cell(row=row, column=3, value=round(b_acc, 4))
        ws3.cell(row=row, column=4, value=f"={get_column_letter(2)}{row}-{get_column_letter(3)}{row}")
    style_data(ws3, 2, 13, 4)
    auto_width(ws3, 4)

    path = os.path.join(BASE, "附件5-Baseline模型完整训练动态日志.xlsx")
    wb.save(path)
    print(f"附件5已生成: {path}")
    return path


def create_attachment6():
    wb = openpyxl.Workbook()

    # Sheet 1: Dropout实验
    ws1 = wb.active
    ws1.title = "Dropout实验"
    h1 = ["Dropout概率", "A线TrainAcc", "A线ValAcc", "B线ValAcc", "TrainLoss最终值", "ValLoss最终值", "收敛Epoch数"]
    for i, h in enumerate(h1, 1):
        ws1.cell(row=1, column=i, value=h)
    style_header(ws1, 1, 7)
    dropout_data = [
        ("p=0.3", 0.983, 0.786, 0.591, 0.023, 0.412, 105),
        ("p=0.5", 0.942, 0.821, 0.634, 0.087, 0.341, 118),
        ("p=0.7", 0.911, 0.795, 0.608, 0.142, 0.378, 120),
    ]
    for i, (dp, ta, va, bva, tl, vl, ep) in enumerate(dropout_data):
        row = i + 2
        ws1.cell(row=row, column=1, value=dp)
        ws1.cell(row=row, column=2, value=ta)
        ws1.cell(row=row, column=3, value=va)
        ws1.cell(row=row, column=4, value=bva)
        ws1.cell(row=row, column=5, value=tl)
        ws1.cell(row=row, column=6, value=vl)
        ws1.cell(row=row, column=7, value=ep)
    style_data(ws1, 2, 4, 7)
    auto_width(ws1, 7)

    # Sheet 2: L2正则化实验
    ws2 = wb.create_sheet("L2正则化实验")
    h2 = ["L2 Lambda", "A线TrainAcc", "A线ValAcc", "B线ValAcc", "TrainLoss最终值", "ValLoss最终值", "收敛Epoch数"]
    for i, h in enumerate(h2, 1):
        ws2.cell(row=1, column=i, value=h)
    style_header(ws2, 1, 7)
    l2_data = [
        ("lambda=1e-3", 0.895, 0.812, 0.621, 0.198, 0.356, 120),
        ("lambda=1e-4", 0.968, 0.803, 0.615, 0.061, 0.372, 108),
        ("lambda=1e-5", 0.981, 0.771, 0.588, 0.035, 0.418, 98),
    ]
    for i, (l2, ta, va, bva, tl, vl, ep) in enumerate(l2_data):
        row = i + 2
        ws2.cell(row=row, column=1, value=l2)
        ws2.cell(row=row, column=2, value=ta)
        ws2.cell(row=row, column=3, value=va)
        ws2.cell(row=row, column=4, value=bva)
        ws2.cell(row=row, column=5, value=tl)
        ws2.cell(row=row, column=6, value=vl)
        ws2.cell(row=row, column=7, value=ep)
    style_data(ws2, 2, 4, 7)
    auto_width(ws2, 7)

    # Sheet 3: BatchNorm变体实验
    ws3 = wb.create_sheet("BatchNorm变体实验")
    h3 = ["BN配置", "A线TrainAcc", "A线ValAcc", "B线ValAcc", "收敛Epoch数", "训练时间(h)"]
    for i, h in enumerate(h3, 1):
        ws3.cell(row=1, column=i, value=h)
    style_header(ws3, 1, 6)
    bn_data = [
        ("原始BN(ReLU前)", 0.987, 0.763, 0.585, 95, 6.2),
        ("BN前置ReLU", 0.972, 0.791, 0.612, 102, 6.5),
        ("BN后置ReLU", 0.978, 0.774, 0.598, 98, 6.3),
        ("替换为LayerNorm", 0.961, 0.798, 0.625, 110, 7.8),
        ("替换为GroupNorm(G=32)", 0.958, 0.805, 0.641, 115, 8.1),
    ]
    for i, (cfg, ta, va, bva, ep, time_h) in enumerate(bn_data):
        row = i + 2
        ws3.cell(row=row, column=1, value=cfg)
        ws3.cell(row=row, column=2, value=ta)
        ws3.cell(row=row, column=3, value=va)
        ws3.cell(row=row, column=4, value=bva)
        ws3.cell(row=row, column=5, value=ep)
        ws3.cell(row=row, column=6, value=time_h)
    style_data(ws3, 2, 6, 6)
    auto_width(ws3, 6)

    # Sheet 4: 组合策略实验
    ws4 = wb.create_sheet("组合策略实验")
    h4 = ["组合策略", "A线ValAcc", "B线ValAcc", "收敛Epoch数", "收敛稳定性"]
    for i, h in enumerate(h4, 1):
        ws4.cell(row=1, column=i, value=h)
    style_header(ws4, 1, 5)
    combo_data = [
        ("Dropout(p=0.5)+L2(lambda=1e-4)", 0.837, 0.652, 120, "不稳定-振荡"),
        ("Dropout(p=0.5)+LayerNorm", 0.825, 0.645, 118, "稳定"),
        ("Dropout(p=0.5)+GroupNorm", 0.831, 0.658, 120, "稳定"),
        ("L2(lambda=1e-4)+LayerNorm", 0.814, 0.638, 112, "稳定"),
        ("L2(lambda=1e-4)+GroupNorm", 0.819, 0.649, 114, "稳定"),
        ("Dropout+L2+原始BN(三层组合)", 0.828, 0.636, 120, "不稳定-振荡"),
    ]
    for i, (cfg, va, bva, ep, stab) in enumerate(combo_data):
        row = i + 2
        ws4.cell(row=row, column=1, value=cfg)
        ws4.cell(row=row, column=2, value=va)
        ws4.cell(row=row, column=3, value=bva)
        ws4.cell(row=row, column=4, value=ep)
        ws4.cell(row=row, column=5, value=stab)
    style_data(ws4, 2, 7, 5)
    auto_width(ws4, 5)

    # Sheet 5: 训练资源消耗
    ws5 = wb.create_sheet("训练资源消耗")
    h5 = ["策略配置", "GPU显存峰值(GB)", "单Epoch时间(s)", "总训练时间(h)"]
    for i, h in enumerate(h5, 1):
        ws5.cell(row=1, column=i, value=h)
    style_header(ws5, 1, 4)
    res_data = [
        ("Baseline(ResNet-50)", 8.2, 185, 6.1),
        ("Dropout(p=0.5)", 8.2, 192, 6.3),
        ("L2(lambda=1e-4)", 8.2, 188, 5.6),
        ("LayerNorm替换", 8.8, 215, 7.8),
        ("GroupNorm替换", 8.5, 208, 8.1),
        ("Dropout+L2组合", 8.2, 198, 8.5),
    ]
    for i, (cfg, gpu, tpe, total) in enumerate(res_data):
        row = i + 2
        ws5.cell(row=row, column=1, value=cfg)
        ws5.cell(row=row, column=2, value=gpu)
        ws5.cell(row=row, column=3, value=tpe)
        ws5.cell(row=row, column=4, value=total)
    style_data(ws5, 2, 7, 4)
    auto_width(ws5, 4)

    path = os.path.join(BASE, "附件6-正则化策略对比实验数据.xlsx")
    wb.save(path)
    print(f"附件6已生成: {path}")
    return path


def create_attachment7():
    wb = openpyxl.Workbook()

    # Sheet 1: 学习率消融
    sheets_config = [
        ("学习率消融", ["学习率", "A线ValAcc", "B线ValAcc", "收敛Epoch数", "ValLoss最终值"],
         [("1e-2", 0.721, 0.542, 45, 0.682),
          ("5e-3", 0.768, 0.584, 58, 0.523),
          ("1e-3", 0.837, 0.652, 95, 0.341),
          ("5e-4", 0.829, 0.648, 108, 0.352),
          ("1e-4", 0.791, 0.612, 120, 0.421),
          ("1e-5", 0.734, 0.568, 120, 0.612)]),
        ("BatchSize消融", ["BatchSize", "A线ValAcc", "B线ValAcc", "收敛Epoch数", "GPU显存(GB)"],
         [("16", 0.834, 0.651, 120, 15.2),
          ("32", 0.837, 0.652, 118, 10.8),
          ("64", 0.835, 0.648, 105, 8.2),
          ("128", 0.822, 0.635, 92, 7.5)]),
        ("权重初始化方式", ["初始化方式", "A线ValAcc", "B线ValAcc", "收敛Epoch数"],
         [("Kaiming Normal", 0.837, 0.652, 118),
          ("Kaiming Uniform", 0.833, 0.649, 114),
          ("Xavier Normal", 0.818, 0.638, 120),
          ("Xavier Uniform", 0.815, 0.635, 120)]),
        ("数据增强策略", ["数据增强策略", "A线ValAcc", "B线ValAcc", "收敛Epoch数"],
         [("无增强", 0.837, 0.652, 118),
          ("随机翻转", 0.841, 0.661, 115),
          ("随机裁剪", 0.834, 0.655, 112),
          ("色彩抖动", 0.838, 0.648, 120),
          ("组合增强(Flip+Crop+Jitter)", 0.846, 0.672, 120)]),
        ("优化器对比", ["优化器", "A线ValAcc", "B线ValAcc", "收敛Epoch数", "单Epoch时间(s)"],
         [("SGD+Momentum(0.9)", 0.837, 0.652, 118, 198),
          ("SGD+Momentum(0.9)+WeightDecay", 0.835, 0.655, 112, 202),
          ("AdamW", 0.831, 0.648, 85, 195),
          ("Adam", 0.828, 0.642, 78, 193)]),
    ]

    first = True
    for sheet_name, headers, data_rows in sheets_config:
        if first:
            ws = wb.active
            ws.title = sheet_name
            first = False
        else:
            ws = wb.create_sheet(sheet_name)
        for i, h in enumerate(headers, 1):
            ws.cell(row=1, column=i, value=h)
        style_header(ws, 1, len(headers))
        for j, row_data in enumerate(data_rows):
            row = j + 2
            for k, val in enumerate(row_data):
                ws.cell(row=row, column=k+1, value=val)
        style_data(ws, 2, 1 + len(data_rows), len(headers))
        auto_width(ws, len(headers))

    path = os.path.join(BASE, "附件7-超参数敏感性与消融实验记录.xlsx")
    wb.save(path)
    print(f"附件7已生成: {path}")
    return path


def create_attachment8():
    html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>ResNet-50 缺陷检测模型架构规范与产线数据集特征说明书</title>
<style>
body{font-family:"Microsoft YaHei",sans-serif;max-width:1100px;margin:0 auto;padding:20px;color:#333;line-height:1.7}
h1{color:#1a5276;border-bottom:3px solid #2980b9;padding-bottom:8px}
h2{color:#2471a3;border-bottom:2px solid #85c1e9;padding-bottom:5px;margin-top:30px}
h3{color:#2e86c1;margin-top:20px}
table{border-collapse:collapse;width:100%;margin:15px 0;font-size:14px}
th{background:#2980b9;color:#fff;padding:10px 8px;text-align:center}
td{padding:8px;text-align:center;border:1px solid #d4e6f1}
tr:nth-child(even){background:#eaf2f8}
.info-box{background:#d6eaf8;border-left:4px solid #2980b9;padding:12px 18px;margin:15px 0}
.warning-box{background:#fdebd0;border-left:4px solid #e67e22;padding:12px 18px;margin:15px 0}
.code{background:#f4f4f4;padding:2px 6px;border-radius:3px;font-family:Consolas,monospace;font-size:13px}
</style>
</head>
<body>
<h1>ResNet-50 缺陷检测模型架构规范与产线数据集特征说明书</h1>
<p><strong>文档版本：</strong>v2.1 | <strong>编制日期：</strong>2026年5月18日 | <strong>编制部门：</strong>某公司工业AI事业部</p>

<h2>一、模型架构详细配置</h2>
<h3>1.1 主干网络：ResNet-50</h3>
<table>
<tr><th>层级</th><th>输出尺寸</th><th>配置详情</th><th>BN状态</th></tr>
<tr><td>Input</td><td>2048×1536×3</td><td>RGB图像，归一化mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225]</td><td>-</td></tr>
<tr><td>Conv1</td><td>1024×768×64</td><td>7×7 conv, stride=2, padding=3</td><td>BN(ReLU前) ✓</td></tr>
<tr><td>MaxPool</td><td>512×384×64</td><td>3×3, stride=2, padding=1</td><td>-</td></tr>
<tr><td>Layer1(ResBlock×3)</td><td>256×192×256</td><td>[1×1,64]-[3×3,64]-[1×1,256] ×3, stride=1</td><td>BN(ReLU前) ✓</td></tr>
<tr><td>Layer2(ResBlock×4)</td><td>128×96×512</td><td>[1×1,128]-[3×3,128]-[1×1,512] ×4, stride=2</td><td>BN(ReLU前) ✓</td></tr>
<tr><td>Layer3(ResBlock×6)</td><td>64×48×1024</td><td>[1×1,256]-[3×3,256]-[1×1,1024] ×6, stride=2</td><td>BN(ReLU前) ✓</td></tr>
<tr><td>Layer4(ResBlock×3)</td><td>32×24×2048</td><td>[1×1,512]-[3×3,512]-[1×1,2048] ×3, stride=2</td><td>BN(ReLU前) ✓</td></tr>
<tr><td>AvgPool</td><td>1×1×2048</td><td>AdaptiveAvgPool2d(1,1)</td><td>-</td></tr>
<tr><td>FC</td><td>2048→1024</td><td>Linear(2048,1024) + ReLU</td><td>-</td></tr>
<tr><td>Dropout</td><td>1024</td><td>p=0.0(默认关闭，实验中可变)</td><td>-</td></tr>
<tr><td>FC_Cls</td><td>1024→5</td><td>Linear(1024,5) + Softmax</td><td>-</td></tr>
</table>

<div class="info-box">
<strong>说明：</strong>所有卷积层的BatchNorm均位于Conv之后、ReLU之前。全连接层不含BatchNorm层。Dropout层默认关闭(p=0)，实验中根据正则化策略动态调整。
</div>

<h3>1.2 训练超参数基准配置</h3>
<table>
<tr><th>参数</th><th>默认值</th><th>说明</th></tr>
<tr><td>优化器</td><td>SGD + Momentum(0.9)</td><td>Nesterov=False</td></tr>
<tr><td>初始学习率</td><td>0.001</td><td>第80epoch降至1e-4，第110epoch降至1e-5</td></tr>
<tr><td>Batch Size</td><td>32</td><td>单GPU(NVIDIA A100-40GB)</td></tr>
<tr><td>Weight Decay</td><td>0.0</td><td>L2正则化实验时启用</td></tr>
<tr><td>Epochs</td><td>120</td><td>EarlyStopping=15(ValLoss不下降则停止)</td></tr>
<tr><td>Loss Function</td><td>CrossEntropyLoss</td><td>无类别权重</td></tr>
<tr><td>数据增强(训练)</td><td>RandomHorizontalFlip(0.5)+RandomRotation(±10°)</td><td>基础增强仅用于训练集</td></tr>
<tr><td>输入尺寸</td><td>2048×1536</td><td>保持原始分辨率</td></tr>
</table>

<h2>二、产线数据集特征分析</h2>
<h3>2.1 数据集规模与划分</h3>
<table>
<tr><th>数据集</th><th>采集时间</th><th>产线</th><th>总样本数</th><th>训练集</th><th>验证集</th></tr>
<tr><td>A产线数据</td><td>2025年9月-10月</td><td>A产线</td><td>8,400</td><td>6,700</td><td>1,700</td></tr>
<tr><td>B产线数据</td><td>2026年1月-2月</td><td>B产线</td><td>3,200</td><td>-</td><td>3,200(全量评测)</td></tr>
</table>

<h3>2.2 类别分布(A产线训练集)</h3>
<table>
<tr><th>缺陷类别</th><th>训练集样本数</th><th>验证集样本数</th><th>占比</th><th>不平衡比(相对最少类)</th></tr>
<tr><td>划痕(Scratch)</td><td>2,144</td><td>536</td><td>32.0%</td><td>4.98x</td></tr>
<tr><td>凹坑(Dent)</td><td>1,876</td><td>469</td><td>28.0%</td><td>4.36x</td></tr>
<tr><td>氧化斑(Oxidation)</td><td>1,206</td><td>301</td><td>18.0%</td><td>2.80x</td></tr>
<tr><td>毛刺(Burr)</td><td>1,044</td><td>261</td><td>15.6%</td><td>2.43x</td></tr>
<tr><td>正常(Normal)</td><td>430</td><td>133</td><td>6.4%</td><td>1.00x(基准)</td></tr>
</table>

<div class="warning-box">
<strong>注意：</strong>"正常"类别严重欠采样(仅6.4%)，可能导致模型偏向于将样本预测为缺陷类。建议训练时对正常类施加2-4倍权重或进行过采样。
</div>

<h3>2.3 图像质量统计指标</h3>
<table>
<tr><th>指标</th><th>A产线(均值±标准差)</th><th>B产线(均值±标准差)</th><th>差异</th></tr>
<tr><td>平均亮度</td><td>128.5 ± 22.3</td><td>156.8 ± 31.7</td><td>+22.0% (B更亮)</td></tr>
<tr><td>对比度(RMS)</td><td>48.2 ± 12.5</td><td>35.6 ± 14.8</td><td>-26.1% (B对比度更低)</td></tr>
<tr><td>模糊度(Laplacian方差)</td><td>152.3 ± 45.6</td><td>98.7 ± 52.3</td><td>-35.2% (B更模糊)</td></tr>
<tr><td>有效标注区域占比</td><td>78.5% ± 8.2%</td><td>82.1% ± 7.6%</td><td>+4.6%</td></tr>
<tr><td>平均图像文件大小</td><td>1.85 MB</td><td>2.12 MB</td><td>+14.6%</td></tr>
</table>

<div class="warning-box">
<strong>关键差异：</strong>B产线图像的平均亮度比A产线高22%，对比度低26%，模糊度高35%。这三项差异表明两产线存在显着的数据分布偏移(Domain Shift)，是模型在B产线泛化性能骤降的主要环境因素。
</div>

<h3>2.4 标注一致性评估</h3>
<table>
<tr><th>数据集</th><th>质检员数量</th><th>Fleiss' Kappa</th><th>一致性等级</th><th>说明</th></tr>
<tr><td>A产线</td><td>3人(工龄≥3年)</td><td>0.823</td><td>几乎完美一致</td><td>A产线数据标注质量高</td></tr>
<tr><td>B产线</td><td>3人(工龄≥3年)</td><td>0.741</td><td>实质性一致</td><td>B产线部分样本(氧化斑vs正常)存在标注歧义</td></tr>
</table>

<p><strong>标注歧义分析：</strong>B产线中氧化斑类与正常类样本的标注一致性最低(Kappa=0.61)，主要原因是B产线光照偏亮导致轻微氧化痕迹与正常表面纹理在视觉上难以区分。建议在B产线评测报告中单独标注"氧化斑vs正常"混淆对的F1分数。</p>

<h2>三、模型容量与数据复杂度匹配分析</h2>
<table>
<tr><th>分析维度</th><th>数值</th><th>判断</th></tr>
<tr><td>ResNet-50总参数量</td><td>23.5M (不含FC头5M)</td><td>-</td></tr>
<tr><td>训练集样本数</td><td>6,700</td><td>-</td></tr>
<tr><td>样本/参数比</td><td>0.24:1</td><td class="code">极低，强烈倾向过拟合</td></tr>
<tr><td>有效类别数</td><td>5类</td><td>-</td></tr>
<tr><td>类内视觉方差(A产线)</td><td>中低(可控产线环境)</td><td>存在过拟合训练分布的风险</td></tr>
<tr><td>类间视觉方差(A vs B产线)</td><td>高(光照、对比度、模糊度差异显着)</td><td>跨产线泛化困难</td></tr>
</table>

<div class="info-box">
<strong>结论：</strong>样本/参数比极低(0.24:1)是该模型过拟合风险的结构性根源，正则化策略选型必须优先考虑这一问题。同时B产线数据分布偏移意味着即使解决了A产线过拟合，也需要Domain Adaptation或数据增强来提升跨产线泛化。
</div>
</body>
</html>"""

    path = os.path.join(BASE, "附件8-当前模型架构规范与产线数据集特征说明书.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"附件8已生成: {path}")
    return path


if __name__ == "__main__":
    os.makedirs(BASE, exist_ok=True)
    create_attachment5()
    create_attachment6()
    create_attachment7()
    create_attachment8()
    print("\n所有附件5-8生成完毕。")