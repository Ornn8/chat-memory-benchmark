# Spot check — DSH-DREAM v0.3.6 (Raw-turn Retrieval Configuration)

Ten questions were sampled with a fixed seed and stratified across the six coarse dimensions. The sample is deterministic and can be regenerated with `python spot_check.py`.

- Source: `results.jsonl` / `judgments.jsonl`
- Seed: `20261110`; requested: `10`
- Pass rule: all `required` true, no `forbidden_hits`, no `unknown_asserted`, and no error flag.

## Summary

| Item | Value |
| --- | --- |
| Sampled | 10 |
| Pass / fail | 8 / 2 |
| Pass-rule consistency | 10 / 10 |
| Dimensions covered | Boundaries / privacy, Commitments / plans, Corrections / changes, Facts, Hypotheses / insufficient data, Time |

## Manual review

All 10 pass/fail verdicts match the recorded `required` / error-flag state, so
the judge bookkeeping is internally consistent. The manual read found two
wording problems in the judge reasons; neither changes the verdict:

1. **`P01-CASE-003/d15`** — the judge calls the birthday `7月12` “fabricated”,
   but that date is present in the retrieved memory. The fail is still correct
   because the answer wrongly denies the known name and age. The
   `fabricated_date` flag is a false positive.
2. **`P14-CASE-added-relative/d15`** — the judge says the answer misstates the
   first window move as 5/25, but the 5/27 turn's “前天” is indeed 5/25. The
   pass is correct; the last clause of the judge reason is wrong.

This is a judge-bookkeeping consistency check, not a second independent
semantic review. The notes above are kept so maintainers can see the two
borderline reasons rather than treating the judge as error-free.

## 1. `P12-ADD-006/d15` — PASS

- **Persona:** P12
- **Dimensions:** Facts
- **Tags:** 职业, 第三方事实
- **Question:** 我在核对联系人备注：之前说阿梅是做哪一行的？
- **System answer:** 阿梅是做包装设计的，之前还带了两张纸样给你挑。
- **Judge reason:** 回答准确说明阿梅做包装设计，并提及带纸样，符合证据F1，无违规。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-16 19:36` · assistant_message: 省一顿锅碗也挺好哈。打包的菜没给你放香菜吧，你那个备注可得写清楚。
- `2026-05-07 14:29` · assistant_message: 分开以后核对会轻松点，别忘了放到固定位置。
- `2026-05-07 21:22` · assistant_message: 雨棚这事你之前说先悬着，也没催你。进货怕不对版的话，收货时当面点一遍，单子对着看，心里就踏实些。明天要不顺手问一句房东？

## 2. `P17-CASE-043/d03` — PASS

- **Persona:** P17
- **Dimensions:** Corrections / changes
- **Tags:** 没解释的矛盾
- **Question:** 我说过储物间钥匙有哪两种对不上的情况，现在能确定原因吗？
- **System answer:** 你8月2号说过：前一天讲的是已经把储物间钥匙交给物业，可第二天翻抽屉又很确定钥匙一直放家里，你自己也没弄明白哪句记错了。至于原因，现在还是确定不了，我不替你猜。
- **Judge reason:** 回答准确复述两种矛盾说法并承认原因未明，未编造额外细节。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-06 09:19` · assistant_message: 好，先停在卡上的林字，不急着说寄件人是谁。
- `2026-05-01 21:02` · assistant_message: 行，我的线头清单还是三条：谁拿了道具、谁说了假话、哪句话重复出现。你对着这三条看，纽扣现在在谁手里、老褚那句别问夜船算不算假话，先挑一条往下写。
- `2026-05-31 18:35` · assistant_message: 钥匙拿回来就好，换锁这事别拖，今晚就换踏实。是之前一直放在别人那儿的那把？

## 3. `P20-CASE-030/d03` — PASS

- **Persona:** P20
- **Dimensions:** Facts, Commitments / plans
- **Tags:** 职业, 第三方事实, 带条件或期限的偏好和边界
- **Question:** 林潇做什么工作？她通常只在什么时段晨跑？
- **System answer:** 林潇是南岗社区图书室的管理员。晨跑她只跑上午九点前，过了点就不跑，说太阳一上来晒得慌。
- **Judge reason:** 回答准确说明林潇在社区图书室管书，且只在上午九点前晨跑，符合required要求。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-06-25 22:05` · user_message: 对了，跟你说个事。第二次试读会今儿在南岗社区图书室办的，林潇和顾南星都来了。林潇带了旧报纸的线索过来，顾南星负责打孔装订，忙了一下午。比上回强点，这回总算不是一个人干坐着。
- `2026-06-25 22:05` · assistant_message: 这回人多点了，林潇带旧报纸线索、顾南星打孔装订，各管一摊，比上回一个人坐着强。旧报纸那线索是往哪个方向指的？你要想细说就说，不想细说就搁着。
- `2026-06-27 23:16` · assistant_message: 晚上好，秦渡。跑完腿回来瘫着正常，稿子没动先放着。试读会那些我也按老习惯记着呢，我还是先编号再聊，你上回那段试读会我也是按一二三记的——一，林潇带来的旧报纸线索；二，顾南星打孔装订；三，各管一摊忙了一下午。你想先顺哪条，我给它贴个日子。

## 4. `P16-CASE-added-gift_boundary/d00` — PASS

- **Persona:** P16
- **Dimensions:** Boundaries / privacy
- **Tags:** 敏感的事, 边界
- **Question:** 给今晚驻唱写一句公开介绍，怎么称呼她？
- **System answer:** 用“阿桐”就行，今晚节目单上印的也是这个。
- **Judge reason:** 回答用艺名阿桐称呼，满足要求；未提家人不知情等私事，无编造或越界。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-12 14:25` · user_message: 下午好，第一次用这个，先自我介绍一下吧。我叫祁野，25，在渝中区半坡酒馆做晚班调酒师。
- `2026-04-16 22:53` · user_message: 嗯，她那人听了更烦。对了，窗外头今晚没飘雨嘛
- `2026-04-20 13:32` · assistant_message: 那我猜岔了，记下，改成想喝才喝。那今晚打算吃点啥汤？

## 5. `P14-CASE-added-relative/d15` — PASS

- **Persona:** P14
- **Dimensions:** Time
- **Tags:** 相对日期, 时间题
- **Question:** 那盆香草第一回搬到窗边具体是哪天？
- **System answer:** 你说的是迷迭香吧？第一次搬到窗边是5月25号，那天你刚买回来，说先放阳台，还在琢磨窗边会不会太晒。
- **Judge reason:** 回答给出5月25日，与required一致；但证据显示5月25日只是刚买回放阳台，5月27日才说前天搬到窗边，回答把首次移窗边误述为5月25日。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-13 12:22` · user_message: 小满，中午刚坐下歇会儿。六点半的闹钟真把我叫起来了，地铁那几站挤得脚都没地方放，到院里刚好赶上会。会上也没什么新鲜的，就是说进度，我手上这版今天先收个尾。上午对图对得眼睛发花，那么多线叠在一块儿，看久了都分不清哪根是哪根，改到后面全靠比对。中午在附近随便吃了份饭，青椒炒得有点老，饭倒是吃干净了。其实周一一上午这么过下来，人已经有点木，下午还有一摊事等着。行吧，先歇十分钟再说。
- `2026-04-20 16:32` · user_message: 下午接着弄，一杯热水放手边，凉了又续，续到第三回才想起来喝。那两笔挪完了，剩下都是细部，盯久了眼睛发花，就起来在窗边站会儿。楼下不知道谁家在收废品，喇叭喊了两趟，声音从这头挪到那头，也不吵，就是一下一下的，把人从图上拽出来。快递中午到了，一个小盒子，拆开搁桌角，也没什么大用，看着顺眼。这种下午过得快，一晃就四点多。人有点乏，脑子还转，就是转得慢。行吧，再撑一会儿，把手上这点收了就回家。
- `2026-04-26 13:56` · user_message: 中午随便吃了点，窗外今天晴，风也不大。上午把阳台那盆绿萝换了水，剪掉两根烂叶，也就这点正事。下午本来想躺着，脑子又转到社区那套老房上。上个月的加固草图我给赵启明了，他改了两回，今天算最后定下来，要换两根钢梁，楼梯那块还是按原先说的加。这事拖了快一个月，落纸那一下我心里挺踏实。说真的，交到赵启明手上我放心，他做事不算快，但东西不会丢。你说我是不是该学着点，别什么都自己攥着。

## 6. `P01-NEW-009/d45` — FAIL

- **Persona:** P01
- **Dimensions:** Commitments / plans, Hypotheses / insufficient data
- **Tags:** 资料不足, 没说完要跟进的事
- **Question:** 我正填旧书登记表，那本《海边的钟》作者这一栏该怎么填？
- **System answer:** 你之前说过那本《海边的钟》卖家没写作者，我也没查到作者是谁。要不先翻翻扉页看看有没有写？
- **Judge reason:** 回答只确认卖家没写作者并建议查扉页，未给出“历史没有作者信息，可以问卖家”这一要点。
- **Required:** False
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-16 04:15` · user_message: 没写收件人 那怎么送
- `2026-04-18 19:02` · assistant_message: 嗯？你爸怎么了
- `2026-04-26 19:18` · assistant_message: 7月12，公历。行，我不翻阴历那本。

## 7. `P01-CASE-003/d15` — FAIL

- **Persona:** P01
- **Dimensions:** Facts
- **Tags:** 用户的基本信息
- **Question:** 填个表
我全名咋写
多大来着
- **System answer:** 你全名是哪几个字，你一直没跟我说过，我不记得。年龄你也没提过，我不确定。生日倒是记着：7月12，公历。
- **Judge reason:** 证据已给出姓名沈知夏和24岁，回答却否认说过，且编造生日7月12日。
- **Required:** False, False
- **Forbidden hits:** none
- **Unknown asserted:** 0
- **Error flags:** wrong_denial, fabricated_date

**Retrieved top 3:**

- `2026-04-14 09:39` · assistant_message: 一夜没睡是虚。对了，你名字是哪几个字，我一直没细问
- `2026-04-16 04:12` · assistant_message: 开个头：潮汐镇有个夜班邮差叫阿眠，半夜在邮局开窗那会儿，信筒里多了一封没写收件人的信。信封上贴着一枚蓝邮票，摸着像刚晒过太阳
- `2026-04-18 00:42` · assistant_message: 行，说好了，三个一个不少。到时候我来讨

## 8. `P17-CASE-020/d03` — PASS

- **Persona:** P17
- **Dimensions:** Corrections / changes, Commitments / plans, Time
- **Tags:** 时间约定, 时间题, 带条件或期限的偏好和边界, 没解释的矛盾
- **Question:** 我这次戒奶茶原来说到几号、哪天能喝？我记得13号还有最后一次提醒，怎么回事？
- **System answer:** 你原来说的是戒到5月10号，5月11号就解禁能喝了。

13号那次提醒确实有点乱——你5月8号就特意说过只到10号、11号解禁，我13号还说了句“最后一次提醒”，那是我说岔了，不是你又延长了。
- **Judge reason:** 回答准确说明戒到5月10日、11日解禁，并承认13号提醒与先前说法矛盾且未编造原因，符合要求。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-03 22:40` · user_message: 差不多吧。我还说呢，要是戒奶茶成功就请你喝一整月奶茶——说完想起来你压根喝不了，这不白说嘛。
- `2026-05-07 19:59` · assistant_message: 戒奶茶好啊，不过每晚都靠我盯着，那我从今晚起每晚提醒你一次。5月10号结束，记下了。今天这头一天，算你过关。
- `2026-05-07 19:59` · user_message: 今天卷宗又是整到快八点才回来，眼睛干得不行。对了跟你说个事，从5月4号那天起这周我戒奶茶，到5月10号，你每晚提醒我一下

## 9. `P20-CASE-027/d15` — PASS

- **Persona:** P20
- **Dimensions:** Commitments / plans, Hypotheses / insufficient data
- **Tags:** 没说完要跟进的事, 计划, 资料不足
- **Question:** 明信片收纳那件事当时停在哪一步，下一步准备先做什么？
- **System answer:** 明信片那事停在“盒子先不买，等你量完尺寸再挑”，明信片还放抽屉里。下一步就是先量尺寸。
- **Judge reason:** 回答准确复述：尺寸未量、盒子暂不买、明信片放抽屉、下一步先量尺寸，符合要求且未编造未知信息。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-15 23:28` · user_message: 行，今晚先到这。明儿还得早起，争取早点躺下。故事的事我记着呢，你也别忘。夜里再翻出什么乱七八糟的，我就当没看见，硬躺。
- `2026-04-19 22:18` · user_message: 对，明儿就老实吃清淡的，不跟自己较劲。吃完这会儿坐回桌前，想着把长篇正经往下推，可心里有点空，对着空文档就发愣，一个字也落不下去。得先拿笔在纸上写点什么才踏实，不然就这么干坐着耗一晚上。
- `2026-04-30 21:30` · user_message: 行，收下了，这三条够我应付苏编了。还有件事，下周二我想把家里那两本旧杂志拿去南岗社区图书室那个交换架，看看能不能换到一张哈尔滨老街地图，一直想弄一张挂墙上，老道里那种画得细的。

## 10. `P17-CASE-031/d45` — PASS

- **Persona:** P17
- **Dimensions:** Boundaries / privacy
- **Tags:** 称呼条件
- **Question:** 我读社区普法稿时怎么叫你，平时闲聊又怎么叫？
- **System answer:** 读普法稿的时候你叫我小稿，平时闲聊还是叫小满。
- **Judge reason:** 回答准确说明读普法稿时叫小稿、日常闲聊叫小满，符合要求且无违规。
- **Required:** True
- **Forbidden hits:** none
- **Unknown asserted:** none
- **Error flags:** none

**Retrieved top 3:**

- `2026-04-10 22:18` · assistant_message: 行，书宁。谈女士这称呼确实太正式了，跟盖章似的。那以后就这么叫。
- `2026-05-06 18:21` · user_message: 社区读书会公告原来写的是书宁，我想改成谈书宁。私下聊天你照旧叫我书宁就好。
- `2026-05-06 23:07` · assistant_message: 搭档？这称呼听着还挺正式。怎么突然想起这么叫，是阿桔那段要往下走了？
