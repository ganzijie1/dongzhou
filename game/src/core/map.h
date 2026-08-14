#ifndef MENGDE_CORE_MAP_H_
#define MENGDE_CORE_MAP_H_

#include <cstdint>
#include <set>

#include "resource_manager.h"
#include "util/common.h"

namespace mengde {
namespace core {

class Terrain;
class Cell;
class Unit;
class PathTree;

class Map {
 public:
  Map(const vector<string>&, const string&, TerrainManager*);
  ~Map();

 public:
  string        GetModelId();
  Vec2D         GetSize() { return size_; }
  Cell*         GetCell(int, int);
  Cell*         GetCell(Vec2D);
  bool          UnitInCell(Vec2D) const;
  Unit*         GetUnit(Vec2D);
  Terrain*      GetTerrain(Vec2D);
  Terrain*      GetSecondaryTerrain(Vec2D);
  uint8_t       GetSecondaryTerrainCoverage(Vec2D);
  void          SetTerrainBlend(Vec2D, Terrain*, Terrain*, uint8_t);
  int           ApplyTerrainEffect(Unit*, int);
  void          EmptyCell(Vec2D);
  void          MoveUnit(Vec2D, Vec2D);
  void          RemoveUnit(Vec2D);
  PathTree*     FindMovablePath(Unit*);
  vector<Vec2D> FindPathTo(Unit*, Vec2D);
  int           SerializeVec2D(Vec2D v) { return v.y * size_.x + v.x; }
  Vec2D         DeserializeVec2D(int v) { return Vec2D(v % size_.x, v / size_.x); }
  void          PlaceUnit(Unit*, Vec2D);
  bool          IsHostileAdjacent(Unit*, Vec2D);
  bool          IsHostilePlaced(Unit*, Vec2D);
  bool          IsValidCoords(Vec2D) const;
  void          BlockEdge(Vec2D, Vec2D);

 private:
  PathTree* FindPath(Unit*, Vec2D);
  bool      IsEdgeBlocked(Vec2D, Vec2D) const;
  std::pair<int, int> EdgeKey(Vec2D, Vec2D) const;

 private:
  Vec2D                  size_;
  vector<vector<Cell*> > grid_;
  string                 bitmap_path_;
  std::set<std::pair<int, int> > blocked_edges_;
};

}  // namespace core
}  // namespace mengde

#endif  // MENGDE_CORE_MAP_H_
