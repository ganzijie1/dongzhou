from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageStat
import generate_chapter43_maps as common
import generate_chapter47_maps as natural

ROOT=Path(__file__).resolve().parents[1]; CELL=48

def rows(width,height,mode):
    out=[]
    for y in range(height):
        row=[]
        for x in range(width):
            border=min(x,width-1-x,y,height-1-y)
            if mode=="suiyang":
                if abs(y-18)<=1 and x<31: t="w"
                elif border<=2 and (x+y*2)%5<2: t="F"
                elif x<20 and y in (10,26): t="m"
                else: t="g" if (x*2+y)%9<2 else "f"
            else:
                if 4<=x<=13 and y<=9: t="w" if (x+y)%3 else "g"
                elif 15<=y<=20 and 10<=x<=38: t="g"
                elif abs(y-(18-x//10))<=1: t="w"
                elif border<=2 and (x+y*3)%4<2: t="F"
                elif y>=25 and (x*2+y)%5<2: t="F"
                else: t="f" if (x+y)%6 else "g"
            row.append(t)
        out.append(row)
    return out

def place(r,cells,t):
    for x,y in cells:r[y][x]=t

def render(source,r):
    im=Image.open(ROOT/"output/imagegen"/source).convert("RGB")
    return natural.natural_overlay(natural.cover_resize(im,(len(r[0])*CELL,len(r)*CELL)),r)

def save(map_id,suffix,source,prompt,im,r,deploy,mission,walls=set(),gates=set(),regions=None):
    rs=["".join(x) for x in r]
    data={"map":f"assets/lzc/map/{map_id}.png","source_base":f"output/imagegen/{source}","prompt_file":f"output/imagegen/{prompt}","grid":[len(r[0]),len(r)],"cell_pixels":CELL,"terrain_rows":rs,"terrain_protocol":{"version":2,"blendable":["f","g","F","w","m"],"structure_mixing":False},"terrain_layers":[],"terrain_source":"GPT Image 2 natural base plus reviewed programmatic source-of-truth geometry","structure_regions":regions or {},"camp_icon_cells":[],"camp_cells":[],"fence_cells":[],"fence_geometry":"no fences in this battlefield","wall_cells":[list(x) for x in sorted(walls)],"gates":[{"name":"suiyang_west_gate","cells":[list(x) for x in sorted(gates)]}] if gates else [],"castle_cells":[],"supply_sites":[],"blocked_edges":[],"deployments":deploy,"mission":mission,"visual_grid_in_game":False}
    im.convert("RGB").save(ROOT/f"assets/lzc/map/{map_id}.png","PNG",compress_level=3)
    (ROOT/f"assets/lzc/map_sources/{map_id}_{suffix}_manifest.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
    common.review_image(im,r,{"walls":walls,"fences":set(),"gates":gates,"sites":set()},deploy,ROOT/f"output/terrain_model/{map_id}_{suffix}_review.png")
    pred={"map":data["map"],"grid":data["grid"],"backend":"reviewed-contract-with-dinov3-evidence-slot","threshold":.72,"auto_apply":False,"review_required":[],"note":"Classifier evidence cannot overwrite reviewed structure or Lua terrain rows."}
    (ROOT/f"output/terrain_model/{map_id}_{suffix}_prediction.json").write_text(json.dumps(pred,ensure_ascii=False,indent=2),encoding="utf-8")
    stat=ImageStat.Stat(im.convert("RGB"));assert im.size==(len(r[0])*CELL,len(r)*CELL) and max(stat.var)>100
    print(map_id,data["grid"],im.size,[round(v,2) for v in stat.var])

def suiyang():
    w,h=54,36;r=rows(w,h,"suiyang");bounds=(31,3,52,33);gates={(31,17),(31,18)};walls=common.rectangle_perimeter(*bounds)-gates;inside={(x,y) for y in range(4,33) for x in range(32,52)}
    place(r,inside,"i");place(r,walls,"W");place(r,gates,"G")
    deploy=[{"name":"ChuZhuangWang51","force":1,"position":[8,18]},{"name":"GongZiCe51","force":1,"position":[20,18]},{"name":"ShenShuShi55","force":1,"position":[12,14]},{"name":"HuaYuan50","force":3,"position":[44,18]}]
    im=render("chapter55-suiyang-base-gpt2.png",r);common.draw_walls(im,walls,bounds)
    draw=ImageDraw.Draw(im,"RGBA");draw.ellipse((18*CELL,14*CELL,24*CELL,21*CELL),fill=(122,94,61,100))
    save("m087","ch55a","chapter55-suiyang-base-gpt2.png","m087_prompt.txt",im,r,deploy,{"type":"suiyang_siege_pressure","hold_turns":5,"peace":"HuaYuan50 raids ZiFan mound at night"},walls,gates,{"suiyang_city":[[31,3],[52,33]],"chu_earthen_mound":[[18,14],[24,21]]})

def qingcao():
    w,h=48,32;r=rows(w,h,"qingcao")
    deploy=[{"name":"WeiKe55","force":1,"position":[8,18]},{"name":"WeiQi54","force":1,"position":[10,22]},{"name":"DuHui55","force":3,"position":[39,17]}]
    im=render("chapter55-qingcao-base-gpt2.png",r)
    save("m088","ch55b","chapter55-qingcao-base-gpt2.png","m088_prompt.txt",im,r,deploy,{"type":"qingcao_slope_ambush","trigger":[24,18],"target":"DuHui55","outcome":"captured_then_executed","old_man":"ties_grass_at_trigger"})

def main():
    for p in (ROOT/"assets/lzc/map",ROOT/"assets/lzc/map_sources",ROOT/"output/terrain_model"):p.mkdir(parents=True,exist_ok=True)
    suiyang();qingcao()
if __name__=="__main__":main()
