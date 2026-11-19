# 模板

新建一套：在 `cases/<系列>/` 下建一个分组目录（微信表情包里是角色名，用英文小写加连字符），把 `pack.json`、`pack.md` 拷进去。

新建一个案例：把 `case/` 拷成 `<编号>-<动作>/`，例如 `wx-001-nod/`。

## case.json 字段

| 字段 | 说明 |
|---|---|
| `id` | 系列前缀 + 三位编号，本系列内唯一。微信表情包用 `wx-` |
| `title` | 案例名 |
| `meaning` | 含义词，≤4 个字，同套不重复 |
| `tags` | 情绪或场景标签，给索引和站筛选用 |
| `route` | `atlas`（图集轻动效）、`frames`（六帧序列图）、`native`（原生 GIF） |
| `inspired_by` | 从灵感池来的案例才填：灵感编号，如 `insp-003`。这条灵感必须已审批通过，否则 `build_index.py` 报错 |
| `remix_of` | 复刻案例才填：原 GIF 的路径或出处。`remix_build.py` 会自动写 |
| `engine` | 引擎、型号、档位、渠道（ChatGPT / Codex / API）。工具没告诉你型号或档位时填 `null`，不要照抄模板里的型号 |
| `cost` | 出图次数（含废稿）和实测金额。拿不到金额填 `null`。几张表情共用一张图集时，图集的次数和金额记在 `pack.json` 的 `generation_count`，案例里写 `"shared": "atlas"` 并把 `generations` 记为 0 |
| `checks` | 三栏分开：`technical` 机检通过、`visual` 视觉自查、`approved` 用户认可 |
| `status` | `draft` 草稿、`ready` 成品、`submitted` 已提交、`published` 已上架、`rejected` 被拒 |

系列和分组不用填，索引脚本从目录路径读。

加完案例后运行：

```bash
python3 tools/build_index.py
```
