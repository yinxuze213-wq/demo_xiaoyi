const fallbackData = {
  generated_at: "2026-05-23T00:00:00+08:00",
  date_iso: "2026-05-23",
  date_label: "2026.05.23",
  weekday_label: "星期六",
  site_title: "今日能量小卡片",
  hero_title: "今天也要被温柔照顾",
  hero_subtitle: "天气、运势、纪念日和一点偏爱，都放在这里了。",
  theme: {
    name: "草莓气泡",
    mood: "甜甜的、但不吵",
    effect: "petal",
    sticker: "strawberry",
    vars: {}
  },
  weather: {
    city: "韶关",
    summary: "今天的天气正在准备中",
    temperature: "--",
    outfit: "出门前看一眼实时天气，穿舒服一点。"
  },
  relationship: {
    days_together: "--",
    line: "在一起的天数正在计算中。",
    anniversary: { days_left: "--", line: "纪念日提醒正在准备中。" }
  },
  birthdays: [
    { label: "她", nickname: "小仪", date: "10.22", days_left: "--", line: "生日倒计时正在准备中。" },
    { label: "我", nickname: "小尹", date: "02.13", days_left: "--", line: "生日倒计时正在准备中。" }
  ],
  festivals: {
    next: { name: "六一儿童节", kind: "可爱", date_label: "06.01", days_left: "--", tone: "适合买小零食、小玩具，哄她开心一下。" },
    items: []
  },
  events: [],
  horoscopes: {
    girlfriend: {
      label: "她",
      nickname: "小仪",
      sign: "天秤座",
      keyword: "被偏爱",
      summary: "天秤座今日关键词是「被偏爱」。今天适合先照顾心情，再处理事情。",
      overall: 4,
      love: 5,
      mood: 4,
      energy_score: 4,
      lucky_color: "草莓粉",
      lucky_color_hex: "#f06f91",
      lucky_number: "7",
      lucky_item: "热饮",
      energy: "能量适中，适合稳稳推进",
      love_tip: "今天适合把喜欢说得具体一点。",
      work_tip: "适合先做最容易推进的一件事。"
    },
    boyfriend: {
      label: "我",
      nickname: "小尹",
      sign: "水瓶座",
      keyword: "慢慢来",
      summary: "水瓶座今日关键词是「慢慢来」。把难的事情拆成一小步，会比硬撑更顺。",
      overall: 4,
      love: 4,
      mood: 4,
      energy_score: 4,
      lucky_color: "海盐蓝",
      lucky_color_hex: "#5aa7c8",
      lucky_number: "6",
      lucky_item: "一首轻音乐",
      energy: "能量偏柔软，适合少一点硬撑",
      love_tip: "适合轻轻陪着，不急着讲道理。",
      work_tip: "今天不要把任务排太满。"
    }
  },
  today_guide: {
    suitable: ["喝一杯温热的东西", "认真吃一顿饭", "听一首轻音乐", "早点洗漱"],
    avoid: ["空腹喝冰的", "临睡前一直刷手机", "和自己较劲太久", "为了赶进度不吃饭"],
    care: ["穿舒服一点就好。", "今天先做最重要的一件事，剩下的慢慢补。"]
  },
  daily_capsule: {
    title: "草莓气泡小安排",
    items: [
      { label: "约会灵感", value: "一起散步，买一杯她喜欢的饮料" },
      { label: "照片任务", value: "拍今天的天空" },
      { label: "今日小食", value: "一杯热饮" },
      { label: "提前准备", value: "可以提前准备一个小惊喜。" }
    ]
  },
  boyfriend_message: {
    title: "男朋友的小提醒",
    text: "今天想让你先把自己照顾好。饭要好好吃，水要记得喝，累了就停一下，我会一直站在你这边。",
    wishes: ["今天希望你可以喝一杯温热的东西。", "吃饭、喝水、休息都要排进今天。", "晚上尽量早点放下手机。"]
  },
  quote: "把普通的今天，也过成值得记住的一天。",
  music: {
    mode: "generated",
    title: "晨光钢琴盒",
    subtitle: "明亮、轻快、像早晨的窗边",
    tempo: 96,
    waveform: "sine",
    scale: [261.63, 293.66, 329.63, 392.0, 440.0, 523.25],
    seed: "2026-05-23:generated"
  },
  footer: "不用立刻回复，打开看看就好。"
};

let currentData = fallbackData;

const $ = (id) => document.getElementById(id);

function setText(id, value) {
  const node = $(id);
  if (node) node.textContent = value ?? "";
}

function hashString(value) {
  let hash = 2166136261;
  for (let i = 0; i < String(value).length; i += 1) {
    hash ^= String(value).charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function mulberry32(seed) {
  return function next() {
    let t = seed += 0x6D2B79F5;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function createNode(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function fillList(id, items) {
  const list = $(id);
  if (!list) return;
  list.innerHTML = "";
  (Array.isArray(items) ? items : []).forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
}

function applyTheme(theme = {}) {
  const vars = theme.vars || {};
  Object.entries(vars).forEach(([name, value]) => {
    document.documentElement.style.setProperty(name, value);
  });
  const sticker = $("theme-sticker");
  if (sticker) sticker.dataset.sticker = theme.sticker || "strawberry";
}

function renderBirthdays(birthdays) {
  const list = $("birthday-list");
  if (!list) return;
  list.innerHTML = "";
  (Array.isArray(birthdays) ? birthdays : []).forEach((birthday) => {
    const card = createNode("article", "birthday-item");
    card.appendChild(createNode("p", "label", birthday.label || "Birthday"));
    card.appendChild(createNode("h3", "", `${birthday.nickname || "生日"}生日`));

    const meta = createNode("div", "birthday-meta");
    meta.appendChild(createNode("span", "birthday-date", birthday.date || "--"));
    meta.appendChild(createNode("strong", "birthday-days", `${birthday.days_left ?? "--"}天`));
    card.appendChild(meta);

    card.appendChild(createNode("p", "", birthday.line || "生日倒计时正在准备中。"));
    list.appendChild(card);
  });
}

function scoreRow(label, score) {
  const safe = Math.max(1, Math.min(5, Number(score) || 3));
  const row = createNode("div", "score-row");
  row.appendChild(createNode("span", "", label));
  const bar = document.createElement("em");
  const fill = document.createElement("i");
  fill.style.setProperty("--score", `${safe * 20}%`);
  bar.appendChild(fill);
  row.appendChild(bar);
  row.appendChild(createNode("b", "", String(safe)));
  return row;
}

function renderFortunes(horoscopes) {
  const list = $("fortune-list");
  if (!list) return;
  list.innerHTML = "";
  ["girlfriend", "boyfriend"].forEach((key) => {
    const fortune = horoscopes?.[key];
    if (!fortune) return;
    const card = createNode("article", "fortune-card");
    card.style.setProperty("--fortune-color", fortune.lucky_color_hex || "var(--accent)");

    const top = createNode("div", "fortune-top");
    top.appendChild(createNode("span", "fortune-role", `${fortune.label || ""} · ${fortune.sign || ""}`));
    top.appendChild(createNode("h3", "", `${fortune.nickname || fortune.sign || "今日"}运势`));
    top.appendChild(createNode("span", "fortune-keyword", fortune.keyword || "慢慢来"));
    card.appendChild(top);

    card.appendChild(createNode("p", "", fortune.summary || ""));

    const scores = createNode("div", "score-list");
    scores.appendChild(scoreRow("综合", fortune.overall));
    scores.appendChild(scoreRow("感情", fortune.love));
    scores.appendChild(scoreRow("心情", fortune.mood));
    scores.appendChild(scoreRow("能量", fortune.energy_score));
    card.appendChild(scores);

    const lucky = createNode("div", "lucky-row");
    const color = createNode("div");
    color.appendChild(createNode("small", "", "幸运色"));
    color.appendChild(createNode("strong", "", fortune.lucky_color || "--"));
    const number = createNode("div");
    number.appendChild(createNode("small", "", "幸运数字"));
    number.appendChild(createNode("strong", "", fortune.lucky_number || "--"));
    const item = createNode("div");
    item.appendChild(createNode("small", "", "幸运物"));
    item.appendChild(createNode("strong", "", fortune.lucky_item || "--"));
    const energy = createNode("div");
    energy.appendChild(createNode("small", "", "今日状态"));
    energy.appendChild(createNode("strong", "", fortune.energy || "--"));
    lucky.appendChild(color);
    lucky.appendChild(number);
    lucky.appendChild(item);
    lucky.appendChild(energy);
    card.appendChild(lucky);

    const detail = createNode("div", "fortune-detail");
    detail.appendChild(createNode("p", "", fortune.love_tip || ""));
    detail.appendChild(createNode("p", "", fortune.work_tip || ""));
    card.appendChild(detail);

    list.appendChild(card);
  });
}

function renderEvents(events) {
  const list = $("event-list");
  if (!list) return;
  list.innerHTML = "";
  (Array.isArray(events) ? events : []).slice(0, 6).forEach((event) => {
    const p = document.createElement("p");
    p.textContent = event;
    list.appendChild(p);
  });
}

function renderFestivals(festivals) {
  const list = $("festival-list");
  if (!list) return;
  list.innerHTML = "";
  const items = Array.isArray(festivals?.items) ? festivals.items : [];
  items.slice(0, 6).forEach((festival, index) => {
    const card = createNode("article", `festival-item${index === 0 ? " is-next" : ""}`);
    const top = createNode("div", "festival-top");
    top.appendChild(createNode("span", "", festival.kind || "节日"));
    top.appendChild(createNode("b", "", festival.date_label || "--"));
    card.appendChild(top);
    card.appendChild(createNode("h3", "", festival.name || "节日"));
    const days = createNode("div", "festival-days");
    days.appendChild(createNode("strong", "", `${festival.days_left ?? "--"}`));
    days.appendChild(createNode("span", "", "天"));
    card.appendChild(days);
    card.appendChild(createNode("p", "", festival.tone || festival.line || "适合提前准备一点小惊喜。"));
    list.appendChild(card);
  });
}

function renderCapsule(capsule) {
  setText("capsule-title", capsule?.title || "今天的小安排");
  const list = $("capsule-list");
  if (!list) return;
  list.innerHTML = "";
  (Array.isArray(capsule?.items) ? capsule.items : []).forEach((item) => {
    const card = createNode("article", "capsule-item");
    card.appendChild(createNode("span", "", item.label || "今日"));
    card.appendChild(createNode("strong", "", item.value || ""));
    list.appendChild(card);
  });
}

function renderCare(items) {
  const list = $("care-list");
  if (!list) return;
  list.innerHTML = "";
  (Array.isArray(items) ? items : []).forEach((item) => {
    const p = document.createElement("p");
    p.textContent = item;
    list.appendChild(p);
  });
}

function render(data) {
  currentData = { ...fallbackData, ...data };
  applyTheme(currentData.theme);
  document.title = currentData.site_title || "今日能量小卡片";

  setText("date-label", currentData.date_label);
  setText("weekday-label", currentData.weekday_label);
  setText("hero-title", currentData.hero_title);
  setText("hero-subtitle", currentData.hero_subtitle);
  setText("hero-days", currentData.relationship?.days_together);
  setText("theme-name", currentData.theme?.name);
  const nextFestival = currentData.festivals?.next;
  setText("hero-festival", nextFestival ? `${nextFestival.name} ${nextFestival.days_left}天` : "今日小节日");
  setText("hero-music", currentData.music?.title);

  setText("music-title", currentData.music?.title);
  setText("music-subtitle", currentData.music?.subtitle || currentData.music?.artist || "今日轻音乐");

  setText("weather-city", currentData.weather?.city);
  setText("weather-summary", currentData.weather?.summary);
  setText("temperature", currentData.weather?.temperature);
  setText("outfit", currentData.weather?.outfit);

  setText("days-together", currentData.relationship?.days_together);
  setText("relationship-line", currentData.relationship?.line);
  setText("anniversary-days", currentData.relationship?.anniversary?.days_left);
  setText("anniversary-line", currentData.relationship?.anniversary?.line);

  renderBirthdays(currentData.birthdays);
  renderFestivals(currentData.festivals);
  renderEvents(currentData.events);
  renderFortunes(currentData.horoscopes);
  renderCapsule(currentData.daily_capsule);

  fillList("suitable-list", currentData.today_guide?.suitable);
  fillList("avoid-list", currentData.today_guide?.avoid);
  renderCare(currentData.today_guide?.care);

  setText("message-title", currentData.boyfriend_message?.title);
  setText("boyfriend-text", currentData.boyfriend_message?.text);
  fillList("wish-list", currentData.boyfriend_message?.wishes);
  setText("quote", currentData.quote);
  setText("footer-text", currentData.footer);

  const generated = currentData.generated_at
    ? `更新于 ${new Date(currentData.generated_at).toLocaleString("zh-CN", { hour12: false })}`
    : "今日卡片已准备好";
  setText("generated-at", generated);
  updateSky(currentData);
}

async function loadData() {
  try {
    const response = await fetch(`./data.json?v=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    render(data);
  } catch {
    render(fallbackData);
  }
}

const skyState = {
  canvas: null,
  ctx: null,
  width: 0,
  height: 0,
  ratio: 1,
  particles: [],
  colors: ["#f06f91", "#52aeb3", "#f4bd4f", "#8a79c8"],
  effect: "petal",
  rng: mulberry32(hashString("fallback")),
  reduceMotion: window.matchMedia("(prefers-reduced-motion: reduce)").matches
};

function themeColors() {
  const styles = getComputedStyle(document.documentElement);
  return ["--accent", "--accent-2", "--accent-3", "--accent-4"]
    .map((name) => styles.getPropertyValue(name).trim())
    .filter(Boolean);
}

function resetParticles() {
  const state = skyState;
  if (!state.canvas || !state.ctx) return;
  const ratio = Math.min(window.devicePixelRatio || 1, 2);
  state.ratio = ratio;
  state.width = window.innerWidth;
  state.height = window.innerHeight;
  state.canvas.width = Math.floor(state.width * ratio);
  state.canvas.height = Math.floor(state.height * ratio);
  state.canvas.style.width = `${state.width}px`;
  state.canvas.style.height = `${state.height}px`;
  state.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  state.particles = [];

  const count = Math.min(92, Math.max(38, Math.floor(state.width * state.height / 15000)));
  for (let i = 0; i < count; i += 1) {
    const random = state.rng;
    state.particles.push({
      x: random() * state.width,
      y: random() * state.height,
      size: 4 + random() * 12,
      speed: 0.12 + random() * 0.42,
      drift: -0.24 + random() * 0.48,
      spin: random() * Math.PI,
      spinSpeed: -0.012 + random() * 0.024,
      alpha: 0.16 + random() * 0.34,
      color: state.colors[Math.floor(random() * state.colors.length)] || "#f06f91"
    });
  }
}

function drawStar(ctx, x, y, radius) {
  ctx.beginPath();
  for (let i = 0; i < 10; i += 1) {
    const angle = -Math.PI / 2 + i * Math.PI / 5;
    const r = i % 2 === 0 ? radius : radius * 0.42;
    const px = x + Math.cos(angle) * r;
    const py = y + Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();
}

function drawParticle(ctx, particle, effect) {
  ctx.save();
  ctx.translate(particle.x, particle.y);
  ctx.rotate(particle.spin);
  ctx.globalAlpha = particle.alpha;
  ctx.fillStyle = particle.color;
  ctx.strokeStyle = particle.color;
  ctx.lineWidth = 1.4;
  if (effect === "bubble") {
    ctx.globalAlpha = particle.alpha * 0.72;
    ctx.beginPath();
    ctx.arc(0, 0, particle.size * 0.52, 0, Math.PI * 2);
    ctx.stroke();
  } else if (effect === "star") {
    drawStar(ctx, 0, 0, particle.size * 0.52);
  } else if (effect === "moon") {
    ctx.beginPath();
    ctx.arc(0, 0, particle.size * 0.52, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "destination-out";
    ctx.beginPath();
    ctx.arc(particle.size * 0.22, -particle.size * 0.1, particle.size * 0.52, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalCompositeOperation = "source-over";
  } else if (effect === "leaf") {
    ctx.beginPath();
    ctx.ellipse(0, 0, particle.size * 0.38, particle.size * 0.72, 0, 0, Math.PI * 2);
    ctx.fill();
  } else {
    ctx.beginPath();
    ctx.ellipse(0, 0, particle.size * 0.42, particle.size * 0.72, 0, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();
}

function skyFrame() {
  const state = skyState;
  if (!state.ctx) return;
  state.ctx.clearRect(0, 0, state.width, state.height);
  for (const particle of state.particles) {
    drawParticle(state.ctx, particle, state.effect);
    if (!state.reduceMotion) {
      particle.y -= particle.speed;
      particle.x += particle.drift;
      particle.spin += particle.spinSpeed;
      if (particle.y < -24) {
        particle.y = state.height + 24;
        particle.x = state.rng() * state.width;
      }
      if (particle.x < -24) particle.x = state.width + 24;
      if (particle.x > state.width + 24) particle.x = -24;
    }
  }
  requestAnimationFrame(skyFrame);
}

function setupSky() {
  skyState.canvas = $("sky");
  if (!skyState.canvas) return;
  skyState.ctx = skyState.canvas.getContext("2d");
  resetParticles();
  skyFrame();
  window.addEventListener("resize", resetParticles, { passive: true });
}

function updateSky(data) {
  skyState.effect = data.theme?.effect || "petal";
  skyState.colors = themeColors();
  skyState.rng = mulberry32(hashString(`${data.date_iso || ""}:${skyState.effect}`));
  resetParticles();
}

function setupMusic() {
  const button = $("music-toggle");
  const text = $("music-text");
  if (!button || !text) return;

  let context = null;
  let master = null;
  let timer = null;
  let audio = null;
  let playing = false;
  let rng = mulberry32(hashString("music"));

  function setPlaying(next) {
    playing = next;
    document.body.classList.toggle("music-on", playing);
    button.setAttribute("aria-pressed", String(playing));
    text.textContent = playing ? "暂停今日 BGM" : "开启今日 BGM";
  }

  function stopGenerated() {
    if (timer) window.clearInterval(timer);
    timer = null;
  }

  function stopTrack() {
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    audio = null;
  }

  function stop() {
    stopGenerated();
    stopTrack();
    setPlaying(false);
  }

  function tone(freq, when, duration, velocity = 0.075) {
    const music = currentData.music || {};
    const osc = context.createOscillator();
    const gain = context.createGain();
    const filter = context.createBiquadFilter();
    osc.type = music.waveform || "sine";
    osc.frequency.value = freq;
    filter.type = "lowpass";
    filter.frequency.value = 1600;
    gain.gain.setValueAtTime(0, when);
    gain.gain.linearRampToValueAtTime(velocity, when + 0.04);
    gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
    osc.connect(filter);
    filter.connect(gain);
    gain.connect(master);
    osc.start(when);
    osc.stop(when + duration + 0.05);
  }

  function playPhrase() {
    const music = currentData.music || fallbackData.music;
    const scale = Array.isArray(music.scale) && music.scale.length ? music.scale : fallbackData.music.scale;
    const tempo = Number(music.tempo) || 86;
    const beat = 60 / tempo;
    const now = context.currentTime + 0.04;
    for (let i = 0; i < 8; i += 1) {
      const note = scale[Math.floor(rng() * scale.length)];
      const octave = rng() > 0.82 ? 2 : 1;
      const when = now + i * beat * 0.62;
      tone(note * octave, when, beat * 1.08, 0.055 + rng() * 0.04);
      if (i % 3 === 0) tone(scale[0] / 2, when, beat * 1.7, 0.035);
    }
  }

  async function startGenerated() {
    const music = currentData.music || fallbackData.music;
    context = context || new (window.AudioContext || window.webkitAudioContext)();
    await context.resume();
    if (!master) {
      master = context.createGain();
      master.gain.value = 0.52;
      master.connect(context.destination);
    }
    rng = mulberry32(hashString(music.seed || currentData.date_iso || "music"));
    playPhrase();
    const beat = 60 / (Number(music.tempo) || 86);
    timer = window.setInterval(playPhrase, Math.max(1800, beat * 8 * 620));
  }

  async function startTrack() {
    const music = currentData.music || {};
    audio = new Audio(music.src);
    audio.loop = true;
    audio.volume = 0.56;
    await audio.play();
  }

  async function start() {
    try {
      const music = currentData.music || fallbackData.music;
      if (music.mode === "track" && music.src) await startTrack();
      else await startGenerated();
      setPlaying(true);
    } catch {
      text.textContent = "音乐需要再点一次";
      setPlaying(false);
    }
  }

  button.addEventListener("click", async () => {
    if (playing) stop();
    else await start();
  });
}

render(fallbackData);
setupSky();
setupMusic();
loadData();
