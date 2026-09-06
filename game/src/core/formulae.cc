#include "formulae.h"

#include "cell.h"
#include "map.h"
#include "unit.h"
#include "unit_class.h"
#include "util/common.h"

namespace mengde {
namespace core {

Formulae::Formulae() {}

int Formulae::ComputeBasicAttackDamage(Map* m, Unit* unit_atk, Unit* unit_def, int force) {
  return ComputeBasicAttackDamageAt(m, unit_atk, unit_atk->GetPosition(), unit_def,
                                    unit_def->GetPosition(), force);
}

int Formulae::ComputeBasicAttackDamageAt(Map* m, Unit* unit_atk, Vec2D atk_pos,
                                         Unit* unit_def, Vec2D def_pos, int force) {
  const Attribute& a   = unit_atk->GetCurrentAttr();
  const Attribute& d   = unit_def->GetCurrentAttr();
  int              atk = m->GetCell(atk_pos)->ApplyTerrainEffect(unit_atk->GetClassIndex(), a.atk);
  int              def = m->GetCell(def_pos)->ApplyTerrainEffect(unit_def->GetClassIndex(), d.def);
  int damage = ComputeDamageBase(atk, def, unit_atk->GetLevel(), force);
  return ApplyRatio(damage, ComputeClassAdvantage(unit_atk, unit_def));
}

int Formulae::ComputeClassAdvantage(Unit* unit_atk, Unit* unit_def) {
  const string atk = unit_atk->GetClass()->GetId();
  const string def = unit_def->GetClass()->GetId();
  const bool atk_archer = atk == "Archer" || atk == "HorseArcher";
  const bool def_archer = def == "Archer" || def == "HorseArcher";
  if ((atk == "Cavalry" && def == "Infantry") ||
      (atk == "Infantry" && def_archer) ||
      (atk_archer && def == "Cavalry")) return 120;
  if ((def == "Cavalry" && atk == "Infantry") ||
      (def == "Infantry" && atk_archer) ||
      (def_archer && atk == "Cavalry")) return 80;
  return 100;
}

int Formulae::ComputeMagicDamage(Map* m, Unit* unit_atk, Unit* unit_def, int force) {
  UNUSED(m);
  const Attribute& a   = unit_atk->GetCurrentAttr();
  const Attribute& d   = unit_def->GetCurrentAttr();
  int              atk = a.itl;
  int              def = d.itl;
  return ComputeDamageBase(atk, def, unit_atk->GetLevel(), force);
}

int Formulae::ComputeBasicAttackAccuracy(Unit* unit_atk, Unit* unit_def, int cap) {
  const Attribute& a = unit_atk->GetCurrentAttr();
  const Attribute& d = unit_def->GetCurrentAttr();
  return ComputeAccuracyBase(a.dex, d.dex, cap);
}

int Formulae::ComputeMagicAccuracy(Unit* unit_atk, Unit* unit_def, int cap) {
  const Attribute& a = unit_atk->GetCurrentAttr();
  const Attribute& d = unit_def->GetCurrentAttr();
  return ComputeAccuracyBase(a.itl + a.mor, d.itl + d.mor, cap);
}

int Formulae::ComputeBasicAttackDouble(Unit* unit_atk, Unit* unit_def) {
  const Attribute& a = unit_atk->GetCurrentAttr();
  const Attribute& d = unit_def->GetCurrentAttr();
  return ComputeDoubleCriticalBase(a.dex, d.dex);
}

int Formulae::ComputeBasicAttackCritical(Unit* unit_atk, Unit* unit_def) {
  const Attribute& a = unit_atk->GetCurrentAttr();
  const Attribute& d = unit_def->GetCurrentAttr();
  return ComputeDoubleCriticalBase(a.mor, d.mor);
}

int Formulae::ComputeDamageBase(int atk, int def, int atk_lv, int force) {
  int damage = (atk - def) / 3 + atk_lv + 25;
  damage     = ApplyRatio(damage, force);
  return std::max(1, damage);
}

int Formulae::ComputeDoubleCriticalBase(int atk, int def) {
  int val = 0;
  if (atk >= def * 3) {
    val = 100;
  } else if (atk >= def * 2) {
    val = (atk - def * 2) * 80 / def + 20;
  } else if (atk >= def) {
    val = (atk - def) * 18 / def + 2;
  } else {
    val = 1;
  }
  return val;
}

int Formulae::ComputeAccuracyBase(int atk, int def, int cap) {
  int val = 0;
  if (atk >= def / 3) {
    val = std::min(100, (atk - def) * 10 / def + 90);
  } else if (atk >= def / 2) {
    int tdef = def / 2;
    val      = (atk - tdef) * 30 / tdef + 60;
  } else {
    int tdef = def / 3;
    val      = std::max(atk - tdef, 0) * 30 / tdef + 30;
  }
  val = ApplyRatio(val, cap);
  return val;
}

// ratio is a percentage value, 100 is default
int Formulae::ApplyRatio(int value, int ratio) { return value * ratio / 100; }

}  // namespace core
}  // namespace mengde
