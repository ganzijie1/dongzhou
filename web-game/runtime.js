(() => {
  "use strict";

  const STAGE_SCRIPT_VERSION = "20261105-dialogue3";

  function isLuaProxy(value) {
    return typeof value === "function" && value[Symbol.toStringTag] === "Fengari object";
  }

  class DongzhouLuaRuntime {
    constructor(manifest) {
      this.manifest = manifest;
      this.api = null;
      this.loadedStage = null;
    }

    async init() {
      const configSource = await fetch("scenario/config.lua").then((response) => {
        if (!response.ok) throw new Error(`配置载入失败：${response.status}`);
        return response.text();
      });
      fengari.load(configSource, "dongzhou/config.lua")();
      fengari.load(
        'Enum={force={own="own",enemy="enemy",ally="ally"},status={victory="victory",defeat="defeat",undecided="undecided"}}',
        "web-enum"
      )();
    }

    async loadStage(record, api) {
      this.api = api;
      this.resetStageGlobals();
      const source = await fetch(`scenario/stage/${record.file}?v=${STAGE_SCRIPT_VERSION}`).then((response) => {
        if (!response.ok) throw new Error(`关卡 ${record.id} 载入失败：${response.status}`);
        return response.text();
      });
      fengari.load(source, `dongzhou/stage/${record.file}`)();
      this.loadedStage = record.id;
    }

    resetStageGlobals() {
      const source = this.manifest.stageGlobals.map((name) => `${name}=nil`).join(";");
      fengari.load(source, "reset-stage-globals")();
    }

    invoke(name) {
      if (!this.api || !this.loadedStage) return undefined;
      const fn = fengari.load(`return ${name}`, `read:${name}`)();
      if (!isLuaProxy(fn)) return undefined;
      return fn.apply(this.api, []);
    }
  }

  window.DongzhouLuaRuntime = DongzhouLuaRuntime;
  window.luaPoint = (value) => {
    if (isLuaProxy(value)) return [Number(value.get(1)), Number(value.get(2))];
    if (Array.isArray(value)) return [Number(value[0]), Number(value[1])];
    return [Number(value?.[1] ?? value?.x ?? 0), Number(value?.[2] ?? value?.y ?? 0)];
  };
})();
