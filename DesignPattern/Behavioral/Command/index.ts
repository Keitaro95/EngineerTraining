
// 操作そのものをオブジェクトとして扱う
// 発行者 Invoker
// 実行者 Receiver


// とりあえずこんな操作を型定義します
interface Command {
    execute(): void;
    undo(): void;
}

// Receiver：実際の処理の仕方を決めています.
// insertかdeleteだよ
class Editor {
    text = "";
    insert(s: string) { this.text += s;}
    deleteLast(n: number) { this.text = this.text.slice(0, -n); }
}

// 具体的なコマンド
class InsertCommand implements Command {
    private editor: Editor;
    private s: string;
    constructor(editor: Editor, s: string) {
        this.editor = editor;
        this.s = s;
    }
    // Editorの中では、実行はこれにあたる
    execute() { this.editor.insert(this.s); }
    // Editorの中では、undoはこれにあたる
    undo() { this.editor.deleteLast(this.s.length); }
}

// Invoker は Stackを使って stackにpushするかpopしていく
class Invoker {
    private stack: Command[] = [];
    // 実行系はこれ
    run(cmd: Command) { cmd.execute(); this.stack.push(cmd); }
    // undo系はこれ
    undo() { this.stack.pop()?.undo(); }
}

const editor = new Editor();
const invoker = new Invoker();
// runなので実行系が走る。さらにeditorなので editorの実行系が走る
// このように runで実行系であることを伝えて、さらに実際に実行することは editor を代入して
// 決めている
invoker.run(new InsertCommand(editor, "Hello"));
invoker.run(new InsertCommand(editor, "World"));
console.log(editor.text);
// undoなので popが走る。こうして直前の動作を削除もできる
invoker.undo();
console.log(editor.text);

// 実行系か削除系かを決められる
// さらにstackを使ってpushかpopできる