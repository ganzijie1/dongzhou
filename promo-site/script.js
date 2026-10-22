const scenes = {
  city: {
    image: "assets/battle-city.webp",
    alt: "宋都城门与军营战场",
    kicker: "城池 · 营帐 · 正面突破",
    title: "宋都攻防",
    description: "城门压缩正面，营区提供整备空间；进攻路线清晰，但每一步都暴露在守军视野中。",
  },
  camp: {
    image: "assets/battle-camp.webp",
    alt: "山地、竹林、营寨与河道交错的战场",
    kicker: "山脊 · 竹林 · 营寨",
    title: "山地营寨",
    description: "高地切断视线，竹林限制展开；营寨不只是装饰，而是攻防节奏和补给路线的一部分。",
  },
  river: {
    image: "assets/battle-river.webp",
    alt: "河流、道路和营地组成的宽阔战场",
    kicker: "河流 · 渡口 · 双营对峙",
    title: "河谷对阵",
    description: "左右营区隔岸呼应，中部空间决定主力会战；越过浅滩之前，先决定哪条粮道必须守住。",
  },
  plain: {
    image: "assets/battle-plain.webp",
    alt: "山脉与河网环绕的旷野战场",
    kicker: "旷野 · 山口 · 大军展开",
    title: "旷野决战",
    description: "开阔地给骑兵和战车留下速度，也让侧翼暴露。远处山口与水网决定迂回能否成功。",
  },
};

const header = document.querySelector("[data-header]");
const stage = document.querySelector(".battle-stage");
const battleImage = document.querySelector("[data-battle-image]");
const battleKicker = document.querySelector("[data-battle-kicker]");
const battleTitle = document.querySelector("[data-battle-title]");
const battleDescription = document.querySelector("[data-battle-description]");

const syncHeader = () => {
  header.classList.toggle("is-scrolled", window.scrollY > 24);
};

syncHeader();
window.addEventListener("scroll", syncHeader, { passive: true });

document.querySelectorAll("[data-scene]").forEach((button) => {
  button.addEventListener("click", () => {
    const scene = scenes[button.dataset.scene];
    if (!scene || button.classList.contains("is-active")) return;

    document.querySelectorAll("[data-scene]").forEach((tab) => {
      const active = tab === button;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
    });

    stage.classList.add("is-changing");
    window.setTimeout(() => {
      battleImage.src = scene.image;
      battleImage.alt = scene.alt;
      battleKicker.textContent = scene.kicker;
      battleTitle.textContent = scene.title;
      battleDescription.textContent = scene.description;
      stage.classList.remove("is-changing");
    }, 150);
  });
});

const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.12 },
);

document.querySelectorAll("[data-reveal]").forEach((element) => observer.observe(element));
