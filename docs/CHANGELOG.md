## Theme4 — 基线 3.110.078

- 升级基线到官方 **3.110.078**（`ap / system / app / misc / watchface` 等保持官方，AVB 可过）
- 字体替换为 **苹方 PingFang SC**（Regular/Medium/Semibold，CFF→TrueType 转换 + 子集，`MiSansF-*` 为 221 码点兜底）
- `quickapp` 删除 7 个预装游戏：2048、找色块、24点、记忆卡牌、拳力挑战、小人过桥、打地鼠
- 新增 `tools/`：`vela_romfs.py`、`size_report.py`、`build_pingfang_font.py`、`build_rom.sh`
- 说明：launcher 切换动画为私有 EGMI 编译容器，无法从资源层修改（详见 `docs/ui-animation-plan.md`）

##上了release

