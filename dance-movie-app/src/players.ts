/** YouTube とローカル動画を同じ操作で扱うための共通インターフェース */
export interface Player {
  play(): void;
  pause(): void;
  isPlaying(): boolean;
  currentTime(): number;
  duration(): number;
  seek(seconds: number): void;
  setRate(rate: number): void;
  /** 指定速度をネイティブ再生できず、疑似スローで再生しているか */
  isEmulating(): boolean;
  destroy(): void;
}

export class LocalPlayer implements Player {
  constructor(private video: HTMLVideoElement) {
    video.preservesPitch = true;
  }
  play() { void this.video.play(); }
  pause() { this.video.pause(); }
  isPlaying() { return !this.video.paused && !this.video.ended; }
  currentTime() { return this.video.currentTime; }
  duration() { return Number.isFinite(this.video.duration) ? this.video.duration : 0; }
  seek(seconds: number) { this.video.currentTime = seconds; }
  setRate(rate: number) { this.video.playbackRate = rate; }
  isEmulating() { return false; }
  destroy() {
    this.video.pause();
    URL.revokeObjectURL(this.video.src);
    this.video.removeAttribute("src");
    this.video.load();
  }
}

/** 疑似スロー時の1サイクルの長さ(ms)。再生→停止をこの周期で繰り返す */
const EMU_CYCLE_MS = 400;

export class YouTubePlayer implements Player {
  private wantPlaying = false;
  private emu: { duty: number } | null = null;
  private timer: number | undefined;

  constructor(private yt: YT.Player) {}

  /** YouTube側の状態変化（動画クリック・終了など）を反映する */
  handleStateChange(state: YT.PlayerState) {
    if (state === YT.PlayerState.ENDED) {
      this.wantPlaying = false;
      this.stopEmuLoop();
      return;
    }
    // 疑似スロー中は自分で再生/停止を繰り返しているので無視する
    if (this.emu) return;
    if (state === YT.PlayerState.PLAYING) this.wantPlaying = true;
    if (state === YT.PlayerState.PAUSED) this.wantPlaying = false;
  }

  play() {
    this.wantPlaying = true;
    if (this.emu) this.startEmuLoop();
    else this.yt.playVideo();
  }
  pause() {
    this.wantPlaying = false;
    this.stopEmuLoop();
    this.yt.pauseVideo();
  }
  isPlaying() { return this.wantPlaying; }
  currentTime() { return this.yt.getCurrentTime() ?? 0; }
  duration() { return this.yt.getDuration() ?? 0; }
  seek(seconds: number) { this.yt.seekTo(seconds, true); }

  setRate(rate: number) {
    const available = this.yt.getAvailablePlaybackRates();
    const native = available.find((r) => Math.abs(r - rate) < 1e-6);
    this.stopEmuLoop();
    if (native !== undefined) {
      this.emu = null;
      this.yt.setPlaybackRate(native);
      if (this.wantPlaying) this.yt.playVideo();
      return;
    }
    // 非対応の速度: 指定値以上で一番近い対応速度で再生し、再生時間の割合(duty)で実効速度を合わせる
    const base = available.filter((r) => r > rate).sort((a, b) => a - b)[0] ?? 1;
    this.yt.setPlaybackRate(base);
    this.emu = { duty: rate / base };
    if (this.wantPlaying) this.startEmuLoop();
  }
  isEmulating() { return this.emu !== null; }

  destroy() {
    this.stopEmuLoop();
    this.yt.destroy();
  }

  private startEmuLoop() {
    this.stopEmuLoop();
    const tick = () => {
      if (!this.emu || !this.wantPlaying) return;
      const playMs = EMU_CYCLE_MS * this.emu.duty;
      this.yt.playVideo();
      this.timer = window.setTimeout(() => {
        this.yt.pauseVideo();
        this.timer = window.setTimeout(tick, EMU_CYCLE_MS - playMs);
      }, playMs);
    };
    tick();
  }
  private stopEmuLoop() {
    window.clearTimeout(this.timer);
    this.timer = undefined;
  }
}

export function parseYouTubeId(input: string): string | null {
  const text = input.trim();
  if (/^[\w-]{11}$/.test(text)) return text;
  let url: URL;
  try {
    url = new URL(text.startsWith("http") ? text : `https://${text}`);
  } catch {
    return null;
  }
  const host = url.hostname.replace(/^(www|m|music)\./, "");
  let id: string | null = null;
  if (host === "youtu.be") {
    id = url.pathname.split("/")[1] ?? null;
  } else if (host === "youtube.com" || host === "youtube-nocookie.com") {
    id = url.searchParams.get("v");
    const m = url.pathname.match(/^\/(shorts|embed|live|v)\/([\w-]{11})/);
    if (!id && m) id = m[2];
  }
  return id && /^[\w-]{11}$/.test(id) ? id : null;
}

let apiPromise: Promise<void> | null = null;

export function loadYouTubeApi(): Promise<void> {
  if (apiPromise) return apiPromise;
  apiPromise = new Promise((resolve, reject) => {
    window.onYouTubeIframeAPIReady = () => resolve();
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.onerror = () => {
      apiPromise = null;
      reject(new Error("YouTube APIの読み込みに失敗しました"));
    };
    document.head.appendChild(script);
  });
  return apiPromise;
}

declare global {
  interface Window {
    onYouTubeIframeAPIReady?: () => void;
  }
}
