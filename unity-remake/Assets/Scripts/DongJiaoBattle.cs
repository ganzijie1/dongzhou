using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace DongZhou.UnityRemake
{
    public static class DongJiaoRules
    {
        public static readonly string[] Terrain =
        {
            "FFFrrmmmmrrFFPweebe", "FFFrrmmmmrrFFPeeeee", "FFFrrmmmmrrFgPfeeee",
            "wFFrrrrFFFrFgwPPPwP", "wwwFFFrrrrrFFwwFFFF", "wwwggrmmmmrFFwwwFFF",
            "wwwgrrmmmmrFFwwwFFF", "wwwgrrmmmmrFFwwwFFF", "wwwgrrmmmmrFFwwwFFF",
            "wwwwgrrrrrrFFwweFFF", "wcwggggggggggwwwFFF", "~~wwwwwwwwwwwwcFFFF",
            "g~~~~bwwwwwwwwwFFFF", "FFF~~wwwwwwwwwwFFFF"
        };

        public const int Width = 19;
        public const int Height = 14;

        public static bool IsPassable(char terrain) => terrain != 'r' && terrain != 'W' && terrain != '~' && terrain != 'P';

        public static bool IsPassable(int x, int y) =>
            x >= 0 && x < Width && y >= 0 && y < Height && IsPassable(Terrain[y][x]);

        public static int Distance(Vector2Int a, Vector2Int b) => Math.Abs(a.x - b.x) + Math.Abs(a.y - b.y);
    }

    public sealed class DongJiaoBattle : MonoBehaviour
    {
        private sealed class Unit
        {
            public string Name;
            public bool Enemy;
            public Vector2Int Cell;
            public int Hp;
            public int MaxHp;
            public int Move;
            public int Power;
            public bool Acted;
            public bool Moved;
            public bool Alive => Hp > 0;
        }

        private static readonly Vector2Int[] Directions =
        {
            Vector2Int.left, Vector2Int.right, Vector2Int.up, Vector2Int.down
        };

        private readonly List<Unit> units = new List<Unit>();
        private readonly List<string> battleLog = new List<string>();
        private readonly HashSet<Vector2Int> reachable = new HashSet<Vector2Int>();
        private readonly HashSet<Vector2Int> claimedSites = new HashSet<Vector2Int>();
        private readonly Vector2Int[] supplySites =
        {
            new Vector2Int(1, 10), new Vector2Int(5, 12), new Vector2Int(14, 11),
            new Vector2Int(15, 9), new Vector2Int(17, 0)
        };

        private readonly string[] introPages =
        {
            "周宣王中兴之后征姜戎败于千亩，王心日益多疑。童谣传唱“檿弧箕箙，几亡周国”，宣王遂严禁桑弓箕袋，并搜捕宫中弃女。",
            "司市官杜伯多年搜访无果。宣王因恶梦迁怒，执意将杜伯处死；左儒以死相谏，也未能挽回王命。",
            "杜伯含冤伏诛，左儒收尸后自刎。杜伯临死立誓：若死者有知，三年之内必使周王知道滥杀忠良的报应。",
            "三年后，宣王率百官东郊游猎。怪风骤起，白马素车迎面而来，杜伯持赤弓白矢，左儒随车索命。",
            "军令：操纵杜伯、左儒冲破王师。杜伯与周宣王相邻攻击可触发单挑；任一义士阵亡即告失败。"
        };

        private Texture2D mapTexture;
        private Texture2D pixel;
        private Font uiFont;
        private GUIStyle titleStyle;
        private GUIStyle headingStyle;
        private GUIStyle bodyStyle;
        private GUIStyle smallStyle;
        private GUIStyle centeredStyle;
        private GUIStyle buttonStyle;
        private Unit selected;
        private Rect viewport;
        private Rect boardRect;
        private Vector2 pan;
        private float zoom = 1f;
        private bool dragging;
        private Vector2 dragOrigin;
        private bool playerTurn = true;
        private bool showGrid = true;
        private bool battleEnded;
        private bool victory;
        private bool duelTriggered;
        private int turn = 1;
        private int medicine = 2;
        private int storyPage;
        private bool storyOpen = true;
        private string status = "选择杜伯或左儒开始行动";

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Bootstrap()
        {
            if (FindObjectOfType<DongJiaoBattle>() != null)
                return;
            var root = new GameObject("DongJiao Battle Controller");
            DontDestroyOnLoad(root);
            root.AddComponent<DongJiaoBattle>();
        }

        private void Awake()
        {
            mapTexture = Resources.Load<Texture2D>("EastHunt");
            pixel = new Texture2D(1, 1, TextureFormat.RGBA32, false);
            pixel.SetPixel(0, 0, Color.white);
            pixel.Apply();
            uiFont = Font.CreateDynamicFontFromOSFont(
                new[] { "Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Arial" }, 18);
            ResetBattle();
        }

        private void ResetBattle()
        {
            units.Clear();
            AddUnit("杜伯", false, 2, 6, 130, 5, 44);
            AddUnit("左儒", false, 2, 8, 120, 5, 34);
            AddUnit("周宣王", true, 16, 1, 145, 5, 37);
            AddUnit("尹吉甫", true, 15, 1, 110, 4, 29);
            AddUnit("召虎", true, 17, 1, 125, 5, 34);
            AddUnit("王师甲士", true, 12, 1, 100, 4, 25);
            AddUnit("王师甲士", true, 15, 2, 100, 4, 25);
            AddUnit("王师甲士", true, 17, 2, 100, 4, 25);
            AddUnit("王师甲士", true, 17, 3, 100, 4, 25);
            battleLog.Clear();
            claimedSites.Clear();
            reachable.Clear();
            selected = null;
            turn = 1;
            medicine = 2;
            playerTurn = true;
            battleEnded = false;
            victory = false;
            duelTriggered = false;
            storyPage = 0;
            storyOpen = true;
            zoom = 1f;
            pan = Vector2.zero;
            status = "选择杜伯或左儒开始行动";
            AddLog("东郊猎场怪风骤起，白马素车现于王师之前。", new Color(0.93f, 0.82f, 0.56f));
        }

        private void AddUnit(string name, bool enemy, int x, int y, int hp, int move, int power)
        {
            units.Add(new Unit { Name = name, Enemy = enemy, Cell = new Vector2Int(x, y), Hp = hp, MaxHp = hp, Move = move, Power = power });
        }

        private void OnGUI()
        {
            EnsureStyles();
            DrawBackdrop();
            DrawTopBar();
            DrawSidebar();
            DrawBattlefield();
            DrawBottomLog();
            HandlePointer(Event.current);
            if (storyOpen)
                DrawStoryModal();
            if (battleEnded)
                DrawResultModal();
        }

        private void EnsureStyles()
        {
            if (titleStyle != null)
                return;
            GUI.skin.font = uiFont;
            titleStyle = NewStyle(25, FontStyle.Bold, new Color(0.95f, 0.87f, 0.66f), TextAnchor.MiddleLeft);
            headingStyle = NewStyle(18, FontStyle.Bold, Color.white, TextAnchor.MiddleLeft);
            bodyStyle = NewStyle(16, FontStyle.Normal, new Color(0.92f, 0.92f, 0.89f), TextAnchor.UpperLeft);
            bodyStyle.wordWrap = true;
            smallStyle = NewStyle(13, FontStyle.Normal, new Color(0.77f, 0.79f, 0.76f), TextAnchor.MiddleLeft);
            smallStyle.wordWrap = true;
            smallStyle.richText = true;
            centeredStyle = NewStyle(16, FontStyle.Bold, Color.white, TextAnchor.MiddleCenter);
            centeredStyle.wordWrap = true;
            buttonStyle = new GUIStyle(GUI.skin.button)
            {
                font = uiFont, fontSize = 15, fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter, wordWrap = true, padding = new RectOffset(8, 8, 5, 5)
            };
        }

        private GUIStyle NewStyle(int size, FontStyle weight, Color color, TextAnchor anchor) => new GUIStyle
        {
            font = uiFont, fontSize = size, fontStyle = weight, normal = { textColor = color }, alignment = anchor
        };

        private void DrawBackdrop()
        {
            GUI.color = new Color(0.075f, 0.082f, 0.075f);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), pixel);
            GUI.color = Color.white;
        }

        private void DrawTopBar()
        {
            Fill(new Rect(0, 0, Screen.width, 64), new Color(0.13f, 0.12f, 0.095f));
            GUI.Label(new Rect(20, 8, 500, 48), "东郊索命", titleStyle);
            string phase = playerTurn ? "我军行动" : "王师行动";
            GUI.Label(new Rect(Screen.width - 360, 10, 330, 44), $"第 {turn}/18 回合  ·  {phase}", headingStyle);
            Fill(new Rect(0, 63, Screen.width, 1), new Color(0.65f, 0.5f, 0.24f));
        }

        private void DrawSidebar()
        {
            const float width = 260;
            Fill(new Rect(0, 64, width, Screen.height - 64), new Color(0.10f, 0.11f, 0.10f));
            GUI.Label(new Rect(18, 78, 225, 28), "军令", headingStyle);
            GUI.Label(new Rect(18, 108, 225, 65), "击破周宣王车驾护军\n杜伯、左儒不得阵亡", bodyStyle);
            Fill(new Rect(18, 180, 224, 1), new Color(0.28f, 0.3f, 0.27f));

            float y = 194;
            foreach (Unit unit in units.Where(item => !item.Enemy))
            {
                DrawRosterUnit(unit, new Rect(18, y, 224, 62));
                y += 70;
            }

            GUI.Label(new Rect(18, y + 4, 224, 26), "战况", headingStyle);
            GUI.Label(new Rect(18, y + 34, 224, 54), status, smallStyle);
            y += 98;

            if (GUI.Button(new Rect(18, y, 108, 40), $"金疮药  {medicine}", buttonStyle))
                UseMedicine();
            if (GUI.Button(new Rect(134, y, 108, 40), "结束回合", buttonStyle) && playerTurn && !battleEnded && !storyOpen)
                EndPlayerTurn();
            y += 48;
            if (GUI.Button(new Rect(18, y, 108, 38), showGrid ? "隐藏网格" : "显示网格", buttonStyle))
                showGrid = !showGrid;
            if (GUI.Button(new Rect(134, y, 108, 38), "重新开始", buttonStyle))
                ResetBattle();
            y += 48;
            GUI.Label(new Rect(18, y, 224, 70), "滚轮缩放战场\n中键或右键拖动画面\n左键选择、移动、攻击", smallStyle);
        }

        private void DrawRosterUnit(Unit unit, Rect rect)
        {
            Fill(rect, unit == selected ? new Color(0.28f, 0.23f, 0.14f) : new Color(0.15f, 0.16f, 0.145f));
            GUI.Label(new Rect(rect.x + 10, rect.y + 6, 100, 23), unit.Name, headingStyle);
            GUI.Label(new Rect(rect.x + 126, rect.y + 7, 86, 22), unit.Alive ? (unit.Acted ? "已行动" : "待命") : "阵亡", smallStyle);
            DrawHealth(new Rect(rect.x + 10, rect.y + 37, 202, 14), unit);
        }

        private void DrawBattlefield()
        {
            viewport = new Rect(260, 64, Mathf.Max(280, Screen.width - 260), Mathf.Max(260, Screen.height - 184));
            GUI.BeginGroup(viewport);
            float fit = Mathf.Min(viewport.width / DongJiaoRules.Width, viewport.height / DongJiaoRules.Height);
            float cell = fit * zoom;
            Vector2 baseSize = new Vector2(cell * DongJiaoRules.Width, cell * DongJiaoRules.Height);
            Vector2 origin = new Vector2((viewport.width - baseSize.x) * 0.5f, (viewport.height - baseSize.y) * 0.5f) + pan;
            boardRect = new Rect(origin.x, origin.y, baseSize.x, baseSize.y);
            if (mapTexture != null)
                GUI.DrawTexture(boardRect, mapTexture, ScaleMode.ScaleAndCrop, false);
            else
                Fill(boardRect, new Color(0.27f, 0.34f, 0.22f));
            DrawTerrainTint(cell);
            DrawReachable(cell);
            DrawGrid(cell);
            DrawSupplySites(cell);
            DrawUnits(cell);
            GUI.EndGroup();
        }

        private void DrawTerrainTint(float cell)
        {
            for (int y = 0; y < DongJiaoRules.Height; y++)
            for (int x = 0; x < DongJiaoRules.Width; x++)
            {
                char terrain = DongJiaoRules.Terrain[y][x];
                Color color = Color.clear;
                if (!DongJiaoRules.IsPassable(terrain)) color = new Color(0.12f, 0.12f, 0.12f, 0.34f);
                else if (terrain == 'e') color = new Color(0.82f, 0.62f, 0.18f, 0.18f);
                else if (terrain == 'c' || terrain == 'b') color = new Color(0.4f, 0.72f, 0.48f, 0.18f);
                if (color.a > 0) Fill(CellRect(x, y, cell), color);
            }
        }

        private void DrawReachable(float cell)
        {
            if (selected == null || selected.Acted || !playerTurn)
                return;
            foreach (Vector2Int point in reachable)
                Fill(CellRect(point.x, point.y, cell), new Color(0.25f, 0.78f, 0.52f, 0.28f));
            foreach (Unit enemy in units.Where(item => item.Enemy && item.Alive && DongJiaoRules.Distance(selected.Cell, item.Cell) == 1))
                Fill(CellRect(enemy.Cell.x, enemy.Cell.y, cell), new Color(0.9f, 0.24f, 0.18f, 0.34f));
        }

        private void DrawGrid(float cell)
        {
            if (!showGrid) return;
            Color line = new Color(0.94f, 0.9f, 0.72f, 0.19f);
            for (int x = 0; x <= DongJiaoRules.Width; x++) Fill(new Rect(boardRect.x + x * cell, boardRect.y, 1, boardRect.height), line);
            for (int y = 0; y <= DongJiaoRules.Height; y++) Fill(new Rect(boardRect.x, boardRect.y + y * cell, boardRect.width, 1), line);
        }

        private void DrawSupplySites(float cell)
        {
            foreach (Vector2Int site in supplySites)
            {
                Rect rect = CellRect(site.x, site.y, cell);
                Color color = claimedSites.Contains(site) ? new Color(0.5f, 0.5f, 0.45f, 0.7f) : new Color(0.94f, 0.73f, 0.22f, 0.9f);
                Fill(new Rect(rect.center.x - cell * 0.13f, rect.center.y - cell * 0.13f, cell * 0.26f, cell * 0.26f), color);
            }
        }

        private void DrawUnits(float cell)
        {
            foreach (Unit unit in units.Where(item => item.Alive))
            {
                Rect rect = CellRect(unit.Cell.x, unit.Cell.y, cell);
                float inset = Mathf.Max(3, cell * 0.12f);
                Rect token = new Rect(rect.x + inset, rect.y + inset, rect.width - inset * 2, rect.height - inset * 2);
                Fill(token, unit.Enemy ? new Color(0.18f, 0.34f, 0.58f, 0.97f) : new Color(0.72f, 0.19f, 0.16f, 0.97f));
                if (unit == selected)
                {
                    DrawOutline(new Rect(token.x - 3, token.y - 3, token.width + 6, token.height + 6), new Color(1f, 0.82f, 0.3f), 3);
                }
                GUIStyle label = new GUIStyle(centeredStyle) { fontSize = Mathf.Clamp(Mathf.RoundToInt(cell * 0.26f), 11, 18) };
                GUI.Label(token, unit.Name, label);
                DrawHealth(new Rect(token.x, token.yMax - 5, token.width, 5), unit);
            }
        }

        private Rect CellRect(int x, int y, float cell) => new Rect(boardRect.x + x * cell, boardRect.y + y * cell, cell, cell);

        private void DrawBottomLog()
        {
            Rect rect = new Rect(260, Screen.height - 120, Screen.width - 260, 120);
            Fill(rect, new Color(0.08f, 0.085f, 0.078f));
            Fill(new Rect(rect.x, rect.y, rect.width, 1), new Color(0.35f, 0.31f, 0.22f));
            GUI.Label(new Rect(rect.x + 16, rect.y + 8, 90, 24), "战报", headingStyle);
            int first = Mathf.Max(0, battleLog.Count - 3);
            for (int i = first; i < battleLog.Count; i++)
                GUI.Label(new Rect(rect.x + 94, rect.y + 7 + (i - first) * 32, rect.width - 110, 28), battleLog[i], smallStyle);
        }

        private void HandlePointer(Event current)
        {
            if (storyOpen || battleEnded)
                return;
            Vector2 local = current.mousePosition - viewport.position;
            bool overViewport = viewport.Contains(current.mousePosition);
            if (overViewport && current.type == EventType.ScrollWheel)
            {
                float old = zoom;
                zoom = Mathf.Clamp(zoom - current.delta.y * 0.08f, 0.75f, 2.1f);
                if (!Mathf.Approximately(old, zoom)) pan *= zoom / old;
                current.Use();
            }
            if (overViewport && (current.button == 1 || current.button == 2) && current.type == EventType.MouseDown)
            {
                dragging = true;
                dragOrigin = current.mousePosition;
                current.Use();
            }
            if (dragging && current.type == EventType.MouseDrag)
            {
                pan += current.mousePosition - dragOrigin;
                dragOrigin = current.mousePosition;
                current.Use();
            }
            if (dragging && current.type == EventType.MouseUp)
            {
                dragging = false;
                current.Use();
            }
            if (!overViewport || current.button != 0 || current.type != EventType.MouseDown || !playerTurn)
                return;
            float cell = boardRect.width / DongJiaoRules.Width;
            int x = Mathf.FloorToInt((local.x - boardRect.x) / cell);
            int y = Mathf.FloorToInt((local.y - boardRect.y) / cell);
            if (x >= 0 && x < DongJiaoRules.Width && y >= 0 && y < DongJiaoRules.Height)
                ClickCell(new Vector2Int(x, y));
            current.Use();
        }

        private void ClickCell(Vector2Int cell)
        {
            Unit clicked = UnitAt(cell);
            if (clicked != null && !clicked.Enemy && !clicked.Acted)
            {
                selected = clicked;
                BuildReachable();
                status = $"{clicked.Name}：移动 {clicked.Move}，攻击 {clicked.Power}";
                return;
            }
            if (selected == null || selected.Acted)
                return;
            if (clicked != null && clicked.Enemy && DongJiaoRules.Distance(selected.Cell, clicked.Cell) == 1)
            {
                Attack(selected, clicked, true);
                selected.Acted = true;
                selected = null;
                reachable.Clear();
                CheckEndConditions();
                return;
            }
            if (clicked == null && reachable.Contains(cell) && !selected.Moved)
            {
                selected.Cell = cell;
                selected.Moved = true;
                BuildReachable();
                status = $"{selected.Name}已移动，可攻击相邻王师或结束行动";
                ClaimSupply(selected);
            }
        }

        private void BuildReachable()
        {
            reachable.Clear();
            if (selected == null || selected.Moved) return;
            var queue = new Queue<(Vector2Int Cell, int Cost)>();
            queue.Enqueue((selected.Cell, 0));
            reachable.Add(selected.Cell);
            while (queue.Count > 0)
            {
                var node = queue.Dequeue();
                if (node.Cost >= selected.Move) continue;
                foreach (Vector2Int direction in Directions)
                {
                    Vector2Int next = node.Cell + direction;
                    if (!DongJiaoRules.IsPassable(next.x, next.y) || reachable.Contains(next) || UnitAt(next) != null) continue;
                    reachable.Add(next);
                    queue.Enqueue((next, node.Cost + 1));
                }
            }
            reachable.Remove(selected.Cell);
        }

        private void Attack(Unit attacker, Unit defender, bool allowCounter)
        {
            if (attacker.Name == "杜伯" && defender.Name == "周宣王" && !duelTriggered)
            {
                duelTriggered = true;
                defender.Hp = 0;
                foreach (Unit enemy in units.Where(unit => unit.Enemy && unit.Alive)) enemy.Hp = Mathf.Max(1, enemy.Hp - 18);
                AddLog("杜伯赤弓白矢逼近王驾，周宣王负伤退阵，王师震动！", new Color(1f, 0.78f, 0.28f));
                status = "史实单挑触发：周宣王已退出战场";
                return;
            }
            int damage = Mathf.Max(12, attacker.Power + UnityEngine.Random.Range(-5, 7));
            defender.Hp = Mathf.Max(0, defender.Hp - damage);
            AddLog($"{attacker.Name}攻击{defender.Name}，造成 {damage} 点伤害。", attacker.Enemy ? new Color(0.58f, 0.72f, 0.96f) : new Color(0.96f, 0.66f, 0.52f));
            if (!defender.Alive)
            {
                AddLog($"{defender.Name}退出战场。", Color.white);
                return;
            }
            if (allowCounter && DongJiaoRules.Distance(attacker.Cell, defender.Cell) == 1)
            {
                int counter = Mathf.Max(8, defender.Power / 2 + UnityEngine.Random.Range(-3, 4));
                attacker.Hp = Mathf.Max(0, attacker.Hp - counter);
                AddLog($"{defender.Name}反击，{attacker.Name}损失 {counter} 点兵力。", new Color(0.8f, 0.82f, 0.78f));
            }
        }

        private void EndPlayerTurn()
        {
            foreach (Unit unit in units.Where(item => !item.Enemy && item.Alive && !item.Acted)) unit.Acted = true;
            selected = null;
            reachable.Clear();
            playerTurn = false;
            status = "王师开始行动";
            EnemyTurn();
        }

        private void EnemyTurn()
        {
            foreach (Unit enemy in units.Where(item => item.Enemy && item.Alive).ToList())
            {
                Unit target = units.Where(item => !item.Enemy && item.Alive).OrderBy(item => DongJiaoRules.Distance(item.Cell, enemy.Cell)).FirstOrDefault();
                if (target == null) break;
                if (DongJiaoRules.Distance(enemy.Cell, target.Cell) > 1)
                    MoveToward(enemy, target.Cell);
                if (DongJiaoRules.Distance(enemy.Cell, target.Cell) == 1)
                    Attack(enemy, target, true);
                CheckEndConditions();
                if (battleEnded) return;
            }
            turn++;
            if (turn > 18)
            {
                EndBattle(false, "十八回合已尽，白马素车隐入怪风。沉冤未能昭雪。");
                return;
            }
            foreach (Unit unit in units.Where(item => !item.Enemy && item.Alive))
            {
                unit.Acted = false;
                unit.Moved = false;
            }
            playerTurn = true;
            status = "我军行动：选择杜伯或左儒";
        }

        private void MoveToward(Unit unit, Vector2Int goal)
        {
            var queue = new Queue<Vector2Int>();
            var previous = new Dictionary<Vector2Int, Vector2Int>();
            queue.Enqueue(unit.Cell);
            previous[unit.Cell] = unit.Cell;
            Vector2Int destination = unit.Cell;
            int bestDistance = DongJiaoRules.Distance(unit.Cell, goal);
            while (queue.Count > 0)
            {
                Vector2Int current = queue.Dequeue();
                int distance = DongJiaoRules.Distance(current, goal);
                if (distance < bestDistance)
                {
                    bestDistance = distance;
                    destination = current;
                }
                if (distance == 1)
                {
                    destination = current;
                    break;
                }
                foreach (Vector2Int direction in Directions)
                {
                    Vector2Int next = current + direction;
                    if (previous.ContainsKey(next) || !DongJiaoRules.IsPassable(next.x, next.y)) continue;
                    Unit occupant = UnitAt(next);
                    if (occupant != null && occupant != unit) continue;
                    previous[next] = current;
                    queue.Enqueue(next);
                }
            }
            var path = new List<Vector2Int>();
            while (destination != unit.Cell)
            {
                path.Add(destination);
                destination = previous[destination];
            }
            path.Reverse();
            if (path.Count > 0)
                unit.Cell = path[Mathf.Min(unit.Move - 1, path.Count - 1)];
        }
        private void ClaimSupply(Unit unit)
        {
            if (!supplySites.Contains(unit.Cell) || claimedSites.Contains(unit.Cell)) return;
            claimedSites.Add(unit.Cell);
            int amount = unit.Cell == new Vector2Int(15, 9) ? 20 : 15;
            unit.Hp = Mathf.Min(unit.MaxHp, unit.Hp + amount);
            medicine++;
            AddLog($"{unit.Name}占领补给点，恢复 {amount} 点兵力并获得金疮药。", new Color(0.58f, 0.9f, 0.56f));
        }

        private void UseMedicine()
        {
            if (storyOpen || battleEnded || !playerTurn || medicine <= 0 || selected == null || !selected.Alive) return;
            if (selected.Hp >= selected.MaxHp) { status = $"{selected.Name}兵力已满"; return; }
            medicine--;
            selected.Hp = Mathf.Min(selected.MaxHp, selected.Hp + 60);
            selected.Acted = true;
            AddLog($"{selected.Name}使用金疮药，恢复兵力。", new Color(0.58f, 0.9f, 0.56f));
            selected = null;
            reachable.Clear();
        }

        private void CheckEndConditions()
        {
            if (battleEnded) return;
            Unit duBo = units.First(unit => unit.Name == "杜伯");
            Unit zuoRu = units.First(unit => unit.Name == "左儒");
            if (!duBo.Alive || !zuoRu.Alive)
            {
                EndBattle(false, "王师势众，白马素车隐入风中；杜伯之冤仍未昭雪。");
                return;
            }
            if (units.All(unit => !unit.Enemy || !unit.Alive))
                EndBattle(true, "一声弓响，赤光掠过。宣王中箭伏于车中，百官惊散，王师撤回镐京。");
        }

        private void EndBattle(bool won, string message)
        {
            battleEnded = true;
            victory = won;
            selected = null;
            reachable.Clear();
            status = won ? "胜利：东郊沉冤得雪" : "失败";
            AddLog(message, won ? new Color(1f, 0.82f, 0.35f) : new Color(0.94f, 0.46f, 0.4f));
        }

        private Unit UnitAt(Vector2Int cell) => units.FirstOrDefault(unit => unit.Alive && unit.Cell == cell);

        private void DrawStoryModal()
        {
            Fill(new Rect(0, 0, Screen.width, Screen.height), new Color(0, 0, 0, 0.68f));
            float width = Mathf.Min(760, Screen.width - 40);
            float height = Mathf.Min(370, Screen.height - 40);
            Rect panel = new Rect((Screen.width - width) * 0.5f, (Screen.height - height) * 0.5f, width, height);
            Fill(panel, new Color(0.12f, 0.115f, 0.095f, 0.98f));
            DrawOutline(panel, new Color(0.65f, 0.5f, 0.24f), 2);
            GUI.Label(new Rect(panel.x + 28, panel.y + 20, panel.width - 56, 38), "第一回 · 周宣王闻谣轻杀　杜大夫化厉鸣冤", titleStyle);
            GUI.Label(new Rect(panel.x + 34, panel.y + 82, panel.width - 68, panel.height - 160), introPages[storyPage], bodyStyle);
            GUI.Label(new Rect(panel.x + 34, panel.yMax - 58, 120, 36), $"{storyPage + 1} / {introPages.Length}", smallStyle);
            string label = storyPage + 1 == introPages.Length ? "出阵" : "继续";
            if (GUI.Button(new Rect(panel.xMax - 154, panel.yMax - 64, 120, 40), label, buttonStyle))
            {
                if (storyPage + 1 < introPages.Length) storyPage++;
                else storyOpen = false;
            }
        }

        private void DrawResultModal()
        {
            Fill(new Rect(0, 0, Screen.width, Screen.height), new Color(0, 0, 0, 0.62f));
            Rect panel = new Rect((Screen.width - 560) * 0.5f, (Screen.height - 290) * 0.5f, 560, 290);
            Fill(panel, new Color(0.12f, 0.115f, 0.095f, 0.99f));
            DrawOutline(panel, victory ? new Color(0.76f, 0.59f, 0.22f) : new Color(0.62f, 0.22f, 0.18f), 3);
            GUIStyle resultTitle = new GUIStyle(titleStyle) { alignment = TextAnchor.MiddleCenter, fontSize = 32 };
            GUI.Label(new Rect(panel.x + 20, panel.y + 24, panel.width - 40, 54), victory ? "东郊索命 · 胜" : "东郊索命 · 败", resultTitle);
            string text = victory
                ? "宣王负伤撤回镐京，今日所见被严令封口。那名被抱往褒城的女婴，也正一步步走近周室。"
                : "白马素车隐入风中。东郊围猎仍在继续，杜伯之冤却不会就此消散。";
            GUI.Label(new Rect(panel.x + 45, panel.y + 94, panel.width - 90, 92), text, bodyStyle);
            if (GUI.Button(new Rect(panel.center.x - 70, panel.yMax - 68, 140, 42), "再战一次", buttonStyle)) ResetBattle();
        }

        private void DrawHealth(Rect rect, Unit unit)
        {
            Fill(rect, new Color(0.08f, 0.08f, 0.075f));
            float ratio = unit.MaxHp == 0 ? 0 : Mathf.Clamp01((float)unit.Hp / unit.MaxHp);
            Fill(new Rect(rect.x + 1, rect.y + 1, Mathf.Max(0, (rect.width - 2) * ratio), rect.height - 2),
                ratio > 0.5f ? new Color(0.34f, 0.68f, 0.32f) : ratio > 0.25f ? new Color(0.82f, 0.61f, 0.22f) : new Color(0.76f, 0.2f, 0.16f));
        }

        private void AddLog(string message, Color color)
        {
            battleLog.Add($"<color=#{ColorUtility.ToHtmlStringRGB(color)}>{message}</color>");
            if (battleLog.Count > 30) battleLog.RemoveAt(0);
        }

        private void Fill(Rect rect, Color color)
        {
            Color previous = GUI.color;
            GUI.color = color;
            GUI.DrawTexture(rect, pixel);
            GUI.color = previous;
        }

        private void DrawOutline(Rect rect, Color color, float thickness)
        {
            Fill(new Rect(rect.x, rect.y, rect.width, thickness), color);
            Fill(new Rect(rect.x, rect.yMax - thickness, rect.width, thickness), color);
            Fill(new Rect(rect.x, rect.y, thickness, rect.height), color);
            Fill(new Rect(rect.xMax - thickness, rect.y, thickness, rect.height), color);
        }
    }
}
