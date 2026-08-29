

type Context = Map<string, number>;

// AbstractExpression： interpret()を宣言する共通interface
interface Expression {
    interpret(ctx: Context): number;
}


// ===Terminal Expression ：「末端（Terminal）が自分の責任範囲だけをチェックする===
// このクラスは Expression を持っている
// 数字が入った時はこれ
class NumberExpr implements Expression {
    private value: number;
    constructor(value: number) {
        this.value= value;
    }
    // constructor(private readonly value: number) {}
    // インタープリターの振る舞い
    interpret(): number { return this.value; }
}
// このクラスも Expression を持っている
// 変数が入った時はこれ
class VariableExpr implements Expression {
    private name: string;
    constructor(name: string) {
        this.name = name;
    }
    // constructor(private readonly name: string) {}
    // インタープリターの振る舞い
    interpret(ctx: Context): number {
        const v = ctx.get(this.name);
        if (v === undefined) throw new Error(`未定義の変数: ${this.name}`);
        return v;
    }
}

// ===Non terminal Expression 
// MulExpr や AddExpr は特にエラーチェックをしておらず、
// つまり各クラスは「自分の役割」だけに集中し、
// エラーの発生源に一番近いところ（今回なら変数参照）でチェックするのが自然な設計になっています。===
class AddExpr implements Expression {
    private l: Expression;
    private r: Expression;
    constructor(l: Expression, r: Expression) {
        this.l = l;
        this.r = r;
    }
    // constructor(private readonly l: Expression, private readonly r: Expression) {}
    // 足し算をしてね
    interpret(ctx: Context): number {
        return this.l.interpret(ctx) + this.r.interpret(ctx);
    }
}

class MulExpr implements Expression {
    private l: Expression;
    private r: Expression;
    constructor(l: Expression, r: Expression) {
        this.l = l;
        this.r = r;
    }
    // constructor(private readonly l: Expression, private readonly r: Expression) {}
    // 掛け算をしてね
    interpret(ctx: Context): number {
        return this.l.interpret(ctx) * this.r.interpret(ctx);
    }
}

// Client：構文木を組み立てて解釈を依頼する
// 全体としては掛け算をしてね。
// x * (y + 10) をしてね
const expr = new MulExpr(
    new VariableExpr("x"), // 初めに x
    new AddExpr(new VariableExpr("y"), new NumberExpr(10)),
);


// コンテキストを作ります
// xには3を、yには5をmapしてね。
const ctx: Context = new Map([["x", 3], ["y", 5]]);

// コンテキストを注入します
// expr.interpretは　x * (y + 10) 　をする
// xは3, yは5
console.log(expr.interpret(ctx));
// Context＝そのつど変わる「変数の値」 → 評価するたびに違うものを渡せる
const ctx2: Context = new Map([["x", 10], ["y", 0]]);
console.log(expr.interpret(ctx2)); // 100  ← 同じ expr を使い回している

// interpret(ctx) を呼んだ瞬間に、木を再帰的にたどりながら評価が走る
// MulExpr.interpret(ctx)
//  ├─ VariableExpr("x").interpret(ctx)  → ctx.get("x")
//  └─ AddExpr.interpret(ctx)
//      ├─ VariableExpr("y").interpret(ctx) → ctx.get("y")
//      └─ NumberExpr(10).interpret(ctx)    → 10