# 多角色场景提示词指南

## 问题背景

在「滥竽充数」项目中，scene_01 和 scene_04 中国王的服饰与南郭先生完全相同，导致角色无法区分。

## 根本原因

SenseNova 每张图独立生成，当 prompt 中只描述一个角色时，其他角色会随机生成。如果未明确区分不同角色的服饰特征，AI 会倾向于使用相似的默认服饰。

## 解决方案

### 1. 为每个角色创建独立的角色描述块

**南郭先生（平民）**：
```
A specific Chinese man from ancient times, middle-aged about 40 years old, 
short and thin build, wearing traditional ancient Chinese rustic robes - 
loose long brown tunic with wide sleeves reaching below knees, 
traditional black cloth belt around waist, black cloth trousers, 
simple black cloth shoes, plain black hair tied in a simple topknot 
with a black ribbon, pale thin face, small narrow eyes, 
short straight black eyebrows, small straight nose, thin lips, 
short sparse black beard and mustache, high cheekbones, 
nervous worried expression, humble peasant appearance, 
ancient Chinese peasant clothing style
```

**齐宣王/齐泯王（帝王）**：
```
A majestic Chinese king from ancient times, sitting on an ornate golden throne, 
wearing traditional Chinese imperial robes - bright yellow silk dragon robe 
with elaborate dragon embroidery, wide sleeves, traditional black silk belt 
with jade ornaments, black silk trousers, formal black silk shoes, 
black hair styled in an elaborate imperial crown with jade ornaments 
and red tassels, dignified serious face, well-groomed features, 
imperial appearance, ancient Chinese royal court style
```

### 2. 在 prompt 中明确角色位置关系

```python
prompt = f"""{KING}, sitting on an ornate golden throne in a large ancient Chinese palace hall. 
In front of him, hundreds of musicians are playing traditional Chinese instruments together. 
The King watches with a pleased expression, enjoying the music. 
NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH anywhere in the image. 
Anime style, digital illustration, soft lighting, cinematic composition, 
detailed background, emotional storytelling, high quality, 8k"""
```

### 3. 服饰颜色区分原则

| 角色类型 | 主色调 | 配饰 |
|----------|--------|------|
| 帝王 | 明黄色（龙袍） | 玉饰、红流苏、龙纹 |
| 官员 | 深蓝色/紫色 | 玉佩、官帽 |
| 平民 | 棕色/灰色/土色 | 布腰带、简单发髻 |
| 士兵 | 红色/黑色 | 铠甲、头盔 |

### 4. 验证清单

- [ ] 每个角色有独立的角色描述块
- [ ] 服饰颜色明显区分（帝王黄 vs 平民棕）
- [ ] 位置关系明确（sitting on throne, standing in front, etc.）
- [ ] 添加 "NO TEXT, NO WORDS, NO LETTERS, NO ENGLISH" 约束
- [ ] 生成后检查各场景角色一致性

## 经验教训

1. **不要依赖 AI 自动区分角色** — 必须明确描述每个角色的特征
2. **服饰颜色是最有效的区分手段** — 帝王用黄色，平民用棕色/灰色
3. **位置关系描述很重要** — 帮助 AI 理解角色之间的空间关系
4. **生成后必须检查** — 即使 prompt 正确，SenseNova 仍可能生成相似角色