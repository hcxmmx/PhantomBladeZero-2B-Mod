# 工程与打包

## 当前工程

- UE5.7，制作机使用5.7.4；MSVC v14314.44。安装UE编辑器和C++工具链后，用下面的脚本编译编辑器模块。
- `HcxEditor` 是编辑器模块，用于生成标准UE蓝图节点；没有额外的运行时自定义DLL。
- 先备份，再修改 `ABPT_2B_Adult`、`ABP_2B_Adult`、`WBP_GaitTuning28` 和 `WBP_SkirtControls34`。
- 当前最终状态已保存在uasset里。不要直接重复执行历史的48/49/50生成函数，它们属于分阶段迁移，并非全部可重复调用。
- `model/2B-chest110.blend` 与FBX是最终模型：后续49–51只改运行图和默认值，未再改网格。名称保留处理阶段编号。

## 必要构建

在仓库根目录用PowerShell执行（编辑器路径按本机填写）：

```powershell
./tools/build.ps1 -UnrealRoot 'D:/Epic Games/UE_5.7'
./tools/cook.ps1 -UnrealRoot 'D:/Epic Games/UE_5.7'
python ./tools/package.py --unreal-root 'D:/Epic Games/UE_5.7'
```

脚本只编译、烹饪或生成本地三件套，不会部署到游戏或上传。此整理后的工程未在全新机器上重新跑完整构建；发布的玩家包直接来自已部署的0.2.51。

## 编辑器外部引用

没有附带游戏原主角的导入网格 `SK_SourceHun`，以及游戏原始材质/动画。保留了所需骨架数据、IK设置、编辑器占位材质及物理占位引用。原主角预览或从头重做自动映射时，需自行在 `/Game/Hcx2B/SK_SourceHun` 准备参考网格。游戏原版动画、材质由已安装游戏提供。

即使补齐编辑器参考，也不要把这些参考资源直接打进玩家包。当前 `metadata/cook-allowlist.json` 按已使用的打包范围列出可发布的项目内资源。

## 运行结构

- 实际显示替换：`/HuaShira/Characters/Hero/Hero_Hun/SkinParts/Hun_Hair_Band`。
- 当前可见模型后处理：`/Game/Hcx2B/ABP_2B_Adult`，父模板`ABPT_2B_Adult`。
- 地面移动/待机有独立的IK及平滑权重，攻击等状态沿用原有适配逻辑。
- 4个裙骨AnimDynamics加有限腿部避让；无Chaos Cloth资产进入当前包。
- 胸部使用两个仅竖直方向的SpringBone，并叠加轻微同步起伏；F9默认1.2/160。
- **保留原游戏 `PA_Hun` 的运行时引用**。工程里的同名物理占位文件只供编辑器解析，不进入玩家包；曾经覆盖/移除该引用导致无法正常受击。
- 原游戏材质路径、材质参数和虚拟纹理设置有关联。仅打包20个目标贴图覆盖，不打包占位材质、游戏骨架和原游戏物理资产。

## 历史脚本

`history/tools/` 记录关键步骤，路径已改为存档内相对位置。脚本仍可能依赖没有归档的中间FBX、早期Blender文件及阶段性JSON；用于阅读和继续开发，不承诺依次执行就能从零还原。原GTA模型可从Credits链接获取，第三方工具从其原项目获取。
