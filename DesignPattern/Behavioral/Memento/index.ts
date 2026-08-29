
// memento思い出の品：変更不可のインターフェース
class EditorMemento {
    private text: string;
    private cursor: number;
    private savedAt: Date;
    constructor(text: string, cursor: number) {
        this.text = text;
        this.cursor = cursor;
        this.savedAt = new Date();
    }
    // 状態はゲッター経由でのみ公開（外部からの書き換えを防ぐ）
    getText(): string { return this.text; }
    getCursor(): number { return this.cursor; }
    getSavedAt(): Date { return this.savedAt; }
}

// Originator：動作を記述する save, restore, toStringの動作
class Editor {
    // 自身の状態 今の文章とカーソル位置
    private text = "";
    private cursor = 0;

    type (s: string) {
        // 文字を今のカーソル位置に挿入する
        this.text = this.text.slice(0, this.cursor) + s + this.text.slice(this.cursor);
        this.cursor += s.length;
    }
    // 今の text,と cursor を渡して EditorMementoを新規作成する
    save(): EditorMemento { return new EditorMemento(this.text, this.cursor); }
    // 過去の状態に巻き戻す。初めにあった自分の状態に上書きする。
    restore(m: EditorMemento) { this.text = m.getText(); this.cursor = m.getCursor(); }
    // デバッグ表示
    toString() { return `"${this.text}" (cursor=${this.cursor})`; }
}


// CareTaker：backupではstackのpushをすしてsaveする, undoではpopとrestoreする。 mementoの中身には関与しない
class CareTaker {
    // 履歴の積み重ね
    private stack: EditorMemento[] = [];
    // priveate Editorとして保持する
    private editor: Editor;
    constructor(editor: Editor) {
        this.editor = editor;
    }
    // constructor(private editor: Editor) {}
    // editor.saveをしてさらにその状態を stackにpushする
    backup() { this.stack.push(this.editor.save()); }
    // stackから1つpopして　その後履歴が空でなければmを渡して復元する
    undo() {
        const m = this.stack.pop();
        if (m) this.editor.restore(m);
    }
}

const editor = new Editor();
const caretaker = new CareTaker(editor);


editor.type("Hello");
caretaker.backup();
editor.type(", World");
caretaker.backup();
editor.type("!!!"); // さらに文字を追加

caretaker.undo(); // pop 
caretaker.undo(); // pop
console.log(editor.toString());
