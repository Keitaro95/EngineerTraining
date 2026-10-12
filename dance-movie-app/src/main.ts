import "./style.css";
import { LocalPlayer, YouTubePlayer, loadYouTubeApi, parseYouTubeId, type Player } from "./players";

const $ = <T extends HTMLElement>(id: string) => document.getElementById(id) as T;

const urlForm = $<HTMLFormElement>("url-form");
const urlInput = $<HTMLInputElement>("url-input");
const fileInput = $<HTMLInputElement>("file-input");
const message = $<HTMLParagraphElement>("message");
const stage = $<HTMLElement>("stage");
const localVideo = $<HTMLVideoElement>("local-video");
const controls = $<HTMLElement>("controls");
const playBtn = $<HTMLButtonElement>("play");
const mirror = $<HTMLInputElement>("mirror");
const seek = $<HTMLInputElement>("seek");
const current = $<HTMLSpanElement>("current");
const durationEl = $<HTMLSpanElement>("duration");
const speed = $<HTMLInputElement>("speed");
const speedValue = $<HTMLOutputElement>("speed-value");
const emuNote = $<HTMLParagraphElement>("emu-note");
const playerBox = $<HTMLDivElement>("player");
const fullscreenBtn = $<HTMLButtonElement>("fullscreen");
const loopABtn = $<HTMLButtonElement>("loop-a");
const loopBBtn = $<HTMLButtonElement>("loop-b");
const loopATime = $<HTMLSpanElement>("loop-a-time");
const loopBTime = $<HTMLSpanElement>("loop-b-time");
const loopCount = $<HTMLInputElement>("loop-count");
const loopToggle = $<HTMLButtonElement>("loop-toggle");
const loopStatus = $<HTMLSpanElement>("loop-status");

let player: Player | null = null;
let seeking = false;

/** 区間ループの状態。played は終了点に到達した回数 */
const loop = { a: null as number | null, b: null as number | null, active: false, played: 0 };
/** 前フレームの再生位置。終了点を「またいだ」瞬間を検出するのに使う */
let prevTime = 0;

const YT_ERRORS: Record<number, string> = {
  2: "URLの形式が正しくありません。",
  5: "この動画はブラウザで再生できません。",
  100: "動画が見つかりません（削除済みか非公開です）。",
  101: "この動画は埋め込み再生が許可されていません。動画ファイルを開いて再生してください。",
  150: "この動画は埋め込み再生が許可されていません。動画ファイルを開いて再生してください。",
};

function showMessage(text: string | null) {
  message.hidden = !text;
  message.textContent = text ?? "";
}

function formatTime(sec: number) {
  const s = Math.max(0, Math.floor(sec));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const ss = String(s % 60).padStart(2, "0");
  return h ? `${h}:${String(m).padStart(2, "0")}:${ss}` : `${m}:${ss}`;
}

function resetPlayer() {
  player?.destroy();
  player = null;
  // YT.Player は div を iframe に置き換えるので、毎回作り直す
  stage.querySelector("#yt-player")?.remove();
  stage.querySelector("iframe")?.remove();
  const div = document.createElement("div");
  div.id = "yt-player";
  stage.prepend(div);
  localVideo.hidden = true;
  stage.classList.remove("loaded");
  loop.a = loop.b = null;
  stopLoop();
  controls.hidden = true;
}

function onPlayerReady(p: Player) {
  player = p;
  stage.classList.add("loaded");
  controls.hidden = false;
  applyRate();
}

function applyRate() {
  const rate = Number(speed.value);
  speedValue.textContent = `${rate.toFixed(2)}x`;
  player?.setRate(rate);
  emuNote.hidden = !player?.isEmulating();
}

async function loadYouTube(id: string) {
  resetPlayer();
  showMessage(null);
  try {
    await loadYouTubeApi();
  } catch (e) {
    showMessage((e as Error).message);
    return;
  }
  let ytPlayer: YouTubePlayer | null = null;
  new YT.Player("yt-player", {
    videoId: id,
    width: "100%",
    height: "100%",
    playerVars: { controls: 0, disablekb: 1, playsinline: 1, rel: 0, iv_load_policy: 3 },
    events: {
      onReady: (e) => {
        ytPlayer = new YouTubePlayer(e.target);
        onPlayerReady(ytPlayer);
      },
      onStateChange: (e) => ytPlayer?.handleStateChange(e.data),
      onError: (e) => showMessage(YT_ERRORS[e.data] ?? `再生エラー (${e.data})`),
    },
  });
}

function loadFile(file: File) {
  resetPlayer();
  showMessage(null);
  localVideo.src = URL.createObjectURL(file);
  localVideo.hidden = false;
  localVideo.addEventListener("loadedmetadata", () => onPlayerReady(new LocalPlayer(localVideo)), { once: true });
  localVideo.addEventListener("error", () => showMessage("この動画ファイルはブラウザで再生できません。"), { once: true });
}

urlForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const id = parseYouTubeId(urlInput.value);
  if (!id) {
    showMessage("YouTubeのURLを認識できませんでした。");
    return;
  }
  void loadYouTube(id);
});

fileInput.addEventListener("change", () => {
  const file = fileInput.files?.[0];
  if (file) loadFile(file);
  fileInput.value = "";
});

function togglePlay() {
  if (!player) return;
  if (player.isPlaying()) player.pause();
  else player.play();
}

/** 手動シークではループ回数を数えないよう、prevTime も移動先に合わせる */
function seekTo(seconds: number) {
  if (!player) return;
  prevTime = seconds;
  player.seek(seconds);
}

function skip(sec: number) {
  if (!player) return;
  seekTo(Math.min(Math.max(player.currentTime() + sec, 0), player.duration()));
}

function formatPoint(sec: number | null) {
  if (sec === null) return "--:--";
  return `${formatTime(sec)}.${Math.floor((sec % 1) * 10)}`;
}

function loopTimes() {
  return Math.min(Math.max(Math.floor(Number(loopCount.value)) || 1, 1), 99);
}

function renderLoop() {
  loopATime.textContent = formatPoint(loop.a);
  loopBTime.textContent = formatPoint(loop.b);
  loopToggle.disabled = loop.a === null || loop.b === null;
  loopToggle.classList.toggle("active", loop.active);
  loopToggle.textContent = loop.active ? "■ ループ停止" : "🔁 ループ";
  loopStatus.textContent = loop.active ? `${Math.min(loop.played + 1, loopTimes())} / ${loopTimes()} 回目` : "";
}

function setLoopPoint(which: "a" | "b") {
  if (!player) return;
  const t = player.currentTime();
  loop[which] = t;
  // 開始点が終了点以降になったら、もう一方を解除して指定し直してもらう
  if (loop.a !== null && loop.b !== null && loop.a >= loop.b) {
    if (which === "a") loop.b = null;
    else loop.a = null;
  }
  if (loop.a === null || loop.b === null) stopLoop();
  renderLoop();
}

function startLoop() {
  if (!player || loop.a === null || loop.b === null) return;
  loop.active = true;
  loop.played = 0;
  seekTo(loop.a);
  player.play();
  renderLoop();
}

function stopLoop() {
  loop.active = false;
  loop.played = 0;
  renderLoop();
}

function toggleLoop() {
  if (loop.active) stopLoop();
  else startLoop();
}

/** 終了点をまたいだら開始点に戻す。指定回数に達したら終了点で停止する */
function updateLoop(now: number) {
  if (!player || !loop.active || loop.a === null || loop.b === null) return;
  // 動画末尾を終了点にした場合、currentTime がぴったり届かないことがあるので少し手前で判定する
  const end = Math.min(loop.b, player.duration() - 0.05);
  if (!(prevTime < end && now >= end)) return;
  loop.played++;
  if (loop.played >= loopTimes()) {
    player.pause();
    stopLoop();
    return;
  }
  seekTo(loop.a);
  player.play();
  renderLoop();
}

function isFullscreen() {
  return document.fullscreenElement === playerBox || playerBox.classList.contains("pseudo-fullscreen");
}

function toggleFullscreen() {
  if (document.fullscreenEnabled) {
    if (document.fullscreenElement) void document.exitFullscreen();
    else void playerBox.requestFullscreen().catch(() => showMessage("全画面表示にできませんでした。"));
    return;
  }
  // iPhone の Safari など要素の全画面表示に未対応の環境では、画面いっぱいに広げて代用する
  playerBox.classList.toggle("pseudo-fullscreen");
  renderFullscreen();
}

function renderFullscreen() {
  fullscreenBtn.textContent = isFullscreen() ? "⛶ 全画面解除" : "⛶ 全画面";
}

function nudgeRate(delta: number) {
  speed.value = String(Math.min(Math.max(Number(speed.value) + delta, Number(speed.min)), Number(speed.max)));
  applyRate();
}

function applyMirror() {
  stage.classList.toggle("mirrored", mirror.checked);
}

playBtn.addEventListener("click", togglePlay);
$("back").addEventListener("click", () => skip(-5));
$("forward").addEventListener("click", () => skip(5));
loopABtn.addEventListener("click", () => setLoopPoint("a"));
loopBBtn.addEventListener("click", () => setLoopPoint("b"));
loopToggle.addEventListener("click", toggleLoop);
loopCount.addEventListener("change", () => {
  loopCount.value = String(loopTimes());
  renderLoop();
});
fullscreenBtn.addEventListener("click", toggleFullscreen);
document.addEventListener("fullscreenchange", renderFullscreen);
mirror.addEventListener("change", applyMirror);
speed.addEventListener("input", applyRate);
document.querySelectorAll<HTMLButtonElement>("[data-rate]").forEach((btn) =>
  btn.addEventListener("click", () => {
    speed.value = btn.dataset.rate!;
    applyRate();
  }),
);

seek.addEventListener("input", () => {
  seeking = true;
  current.textContent = formatTime(Number(seek.value));
});
seek.addEventListener("change", () => {
  seekTo(Number(seek.value));
  seeking = false;
});

document.addEventListener("keydown", (e) => {
  if (e.target instanceof HTMLInputElement && (e.target.type === "text" || e.target.type === "number")) return;
  const actions: Record<string, () => void> = {
    " ": togglePlay,
    ArrowLeft: () => skip(-5),
    ArrowRight: () => skip(5),
    m: () => {
      mirror.checked = !mirror.checked;
      applyMirror();
    },
    "[": () => nudgeRate(-0.05),
    "]": () => nudgeRate(0.05),
    a: () => setLoopPoint("a"),
    b: () => setLoopPoint("b"),
    l: toggleLoop,
    f: toggleFullscreen,
    Escape: () => {
      if (!playerBox.classList.contains("pseudo-fullscreen")) return;
      playerBox.classList.remove("pseudo-fullscreen");
      renderFullscreen();
    },
  };
  const action = actions[e.key.length === 1 ? e.key.toLowerCase() : e.key];
  if (!action) return;
  e.preventDefault();
  action();
});

function tick() {
  if (player) {
    const dur = player.duration();
    seek.max = String(dur);
    durationEl.textContent = formatTime(dur);
    const now = player.currentTime();
    updateLoop(now);
    prevTime = now;
    if (!seeking) {
      seek.value = String(now);
      current.textContent = formatTime(now);
    }
    playBtn.textContent = player.isPlaying() ? "❚❚ 一時停止" : "▶ 再生";
  }
  requestAnimationFrame(tick);
}

applyMirror();
requestAnimationFrame(tick);
