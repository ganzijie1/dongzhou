"""Re-render the 1000-map corpus from reviewed MOD textures and sprites."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/"output/terrain_model/self_evolve_11"; CELL=36; SEED=20260812


def cell_crop(image,x,y,w,h):
 return image.crop((round(x*image.width/w),round(y*image.height/h),round((x+1)*image.width/w),round((y+1)*image.height/h))).convert("RGB")


def build_pools():
 d=json.loads((ROOT/"output/terrain_model/m008_large_v2_manifest.json").read_text(encoding="utf-8"));im=Image.open(ROOT/d["map"]).convert("RGB");mixed={tuple(x["position"])for x in d.get("terrain_layers",[])};pools={k:[]for k in("f","F","m","~")}
 for y,row in enumerate(d["terrain_rows"]):
  for x,c in enumerate(row):
   if c in pools and(x,y)not in mixed:pools[c].append(cell_crop(im,x,y,*d["grid"]))
 wd=json.loads((ROOT/"assets/lzc/map_sources/m058_ch35_manifest.json").read_text(encoding="utf-8"));wi=Image.open(ROOT/wd["map"]).convert("RGB")
 for y,row in enumerate(wd["terrain_rows"]):
  for x,c in enumerate(row):
   if c=="~":pools["~"].append(cell_crop(wi,x,y,*wd["grid"]))
 pools["g"]=[Image.open(ROOT/"assets/lzc/map_sources/haojing/grass.png").convert("RGB")]
 pools["f"].append(Image.open(ROOT/"assets/lzc/map_sources/haojing/earth.png").convert("RGB"))
 return pools


def random_crop(source,rng):
 if source.width<48 or source.height<48:return source.resize((CELL+12,CELL+12),Image.Resampling.LANCZOS)
 size=int(rng.integers(max(32,min(source.width,source.height)//6),max(49,min(source.width,source.height)//2)))
 size=min(size,source.width,source.height);x=int(rng.integers(0,max(1,source.width-size+1)));y=int(rng.integers(0,max(1,source.height-size+1)))
 return source.crop((x,y,x+size,y+size)).resize((CELL+12,CELL+12),Image.Resampling.LANCZOS)


def augment(im,rng):
 if rng.random()<.5:im=ImageOps.mirror(im)
 if rng.random()<.5:im=ImageOps.flip(im)
 im=ImageEnhance.Color(im).enhance(float(rng.uniform(.82,1.2)));im=ImageEnhance.Contrast(im).enhance(float(rng.uniform(.86,1.16)));im=ImageEnhance.Brightness(im).enhance(float(rng.uniform(.9,1.1)));return im


def snowify(im,heavy=True):
 gray=ImageOps.grayscale(im);white=Image.new("RGB",im.size,(232,238,235));return Image.blend(Image.merge("RGB",(gray,gray,gray)),white,.72 if heavy else .36)


def sprite(path,size):return Image.open(path).convert("RGBA").resize(size,Image.Resampling.LANCZOS)


def main():
 manifest_path=DATA/"manifest.json";d=json.loads(manifest_path.read_text(encoding="utf-8"));pools=build_pools();wall=sprite(ROOT/"assets/lzc/map_sources/haojing/wall-strip.png",(CELL,CELL));camp=sprite(ROOT/"assets/lzc/map_sources/changshao/camp.png",(CELL,CELL));fence=sprite(ROOT/"assets/lzc/terrain/fence-queshan-horizontal.png",(CELL,14));buildings=[sprite(p,(CELL+8,CELL+8))for p in sorted((ROOT/"assets/lzc/map_sources/haojing").glob("building-*.png"))]
 for entry in d["maps"]:
  rng=np.random.default_rng(SEED+int(entry["id"])*3571);w,h=entry["grid"];canvas=Image.new("RGBA",(w*CELL,h*CELL),(120,110,80,255));snow_weather=rng.random()<.32
  for y,row in enumerate(entry["rows"]):
   for x,c in enumerate(row):
    base_label=c if c in{"f","g","F","m","~"}else"f";source=pools[base_label][int(rng.integers(len(pools[base_label])))];tile=augment(random_crop(source,rng),rng)
    if c=="s":tile=snowify(tile,True)
    elif snow_weather and c in{"F","m"}:tile=snowify(tile,False)
    elif c=="v":tile=ImageEnhance.Brightness(ImageEnhance.Color(tile).enhance(.72)).enhance(1.45)
    tile=tile.convert("RGBA");canvas.alpha_composite(tile,(x*CELL-6,y*CELL-6))
    if c=="W":canvas.alpha_composite(wall,(x*CELL,y*CELL))
    elif c=="P":canvas.alpha_composite(fence,(x*CELL,y*CELL+CELL//2-fence.height//2))
    elif c=="e":canvas.alpha_composite(camp,(x*CELL,y*CELL))
    elif c=="C":
     b=buildings[int(rng.integers(len(buildings)))];canvas.alpha_composite(b,(x*CELL-4,y*CELL-4))
  result=canvas.convert("RGB").filter(ImageFilter.GaussianBlur(float(rng.uniform(0,.28))));result.save(ROOT/entry["image"],"PNG",optimize=True)
 print(f"re-rendered {len(d['maps'])} maps from reviewed MOD textures")


if __name__=="__main__":main()
