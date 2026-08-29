
type Ask = { level: number; message: string };

// 抽象クラス
abstract class Handler {
    private next?: Handler;

    // 次のハンドラーをつなげる
    setNext(handler: Handler): Handler {
        this.next = handler;
        return handler;
    }   
    // ハンドルした時の振る舞いを書いている。
    handle(req: Ask): string {
        if (this.canHandle(req)) return this.process(req);
        return this.next ? this.next.handle(req) : "誰も対応できません";
    }
    protected abstract canHandle(req: Ask): boolean;
    protected abstract process(req: Ask): string;
}


// フロントデスクの振る舞い
class FrontDesk extends Handler {
    protected canHandle(r: Ask) { return r.level <= 1; }
    protected process(r: Ask) { return `フロントデスク: ${r.message}`}
}

class Engineer extends Handler {
    protected canHandle(r: Ask) { return r.level <= 2; }
    protected process(r: Ask) { return `技術担当: ${r.message}`}
}

class Manager extends Handler {
    protected canHandle(r: Ask) { return r.level <= 3; }
    protected process(r: Ask) { return `マネージャー: ${r.message}`}
}
class Unbelievable extends Handler {
    protected canHandle(r: Ask) { return r.level <= 9; }
    protected process(r: Ask) { return `アンビリーバボー: ${r.message}`}
}

const chain = new FrontDesk(); // コンストラクタ
// chainを　自分の好きな長さとか順番で繋げられる
chain.setNext(new Engineer()).setNext(new Manager()).setNext(new Unbelievable());

// コンストラクタで新しく FrontDeskから始まる chainを作るのが不思議
// でも setNext で繋いで 行けるのは Handler を継承したクラスだから
// どのコンストラクタを入れても setNext() で繋げられる
// なので順番とか関係なく繋げられるの便利

// あとは、 input が起こるだけ。入れた数字でchainを抜ける場所が変わるのがツボ。
console.log(chain.handle({ level: 1, message: "パスワード忘れ" }))
console.log(chain.handle({ level: 3, message: "APIエラー" }))
console.log(chain.handle({ level: 9, message: "A few moments later..." }))

