#ifndef MENGDE_CORE_CELL_H_
#define MENGDE_CORE_CELL_H_

#include <cstdint>

#include "terrain.h"
#include "unit.h"

namespace mengde {
namespace core {

class Cell {
 public:
  Cell(Terrain*);
  Terrain*    GetTerrain();
  Terrain*    GetSecondaryTerrain();
  uint8_t     GetSecondaryCoverage() const;
  bool        HasSecondaryTerrain() const;
  Unit*       GetUnit();
  int         GetMoveCost(int);
  int         GetTerrainEffect(int);
  int         GetTerrainEffectThisCell();
  int         ApplyTerrainEffect(int, int);
  std::string GetTerrainName() const;
  std::string GetTerrainDisplayName() const;
  bool        IsUnitPlaced() const;
  void        SetUnit(Unit*);
  void        SetTerrainBlend(Terrain*, Terrain*, uint8_t);
  void        Empty() { unit_ = nullptr; }

 private:
  Terrain* terrain_;
  Terrain* secondary_terrain_;
  uint8_t  secondary_coverage_;
  Unit*    unit_;
};

}  // namespace core
}  // namespace mengde

#endif  // MENGDE_CORE_CELL_H_