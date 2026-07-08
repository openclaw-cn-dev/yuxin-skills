# 技能同步 SOP — 从 Mac 同步到新智能体

## 场景
当新建智能体需要继承现有同事的技能知识时使用。

## 同步流程

### Step 1: 确定需要同步的技能

```bash
# 列出现有 Hermes 技能
ls ~/.hermes/skills/

# 找出与本智能体职责相关的技能
# 例: 旺财需要 cad-automation, ras-3d-engineering
```

### Step 2: 复制到仓库

```bash
# 复制技能到仓库
cp -r ~/.hermes/skills/<skill-name> /tmp/yuxin-skills/skills/<skill-name>/

# 如果是新机器, 在部署脚本中包含技能复制
```

### Step 3: 在部署中引用

在部署脚本中:
```bash
# 从 yuxin-skills 仓库复制技能
cp -r skills/<skill-name> ~/.hermes/skills/
```

### Step 4: 更新 README

在 README 的技能清单中添加新技能。
