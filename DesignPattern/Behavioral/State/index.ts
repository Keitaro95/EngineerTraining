
// オブジェクトのStateが変わった時振る舞いを変える

// 支払い状態のStateはこれだよ
interface OrderState {
    readonly name: string;
    pay(order: Order): void;
    ship(order: Order): void;
    cancel(order: Order): void;
}

// ↑　order の中身はこうだよ　
// Orderの中に振る舞いも型定義しているよ
class Order {
    private state: OrderState = new PendingState();

    // stateの遷移はこうだよ
    setState(state: OrderState): void {
        console.log(` → ${this.state.name} から ${state.name} へ遷移`);
        this.state = state;
    }
    pay(): void { this.state.pay(this) };
    ship(): void { this.state.ship(this) }; // stateが何であれ、shipに投げるよ
    cancel(): void { this.state.cancel(this) };
}

// ペンディング状態ではこの振る舞いをする
class PendingState implements OrderState {
    readonly name = "未払い";
    // 支払いなら PaidStateへ遷移する
    pay(order: Order) { order.setState(new PaidState()); }
    // 未払いなのでここで通知
    ship(_: Order) { console.log(" x 未払いのため発送できません"); }
    // キャンセルなら CancelledStateへ遷移する
    cancel(order: Order) { order.setState(new CancelledState()); }
}

// 支払い状態ではこの振る舞いをする
class PaidState implements OrderState {
    readonly name = "支払い済み";
    pay(_: Order) { console.log(" x すでに支払い済みです"); }
    ship(order: Order) { order.setState(new ShippedState()); }
    cancel(order: Order) { console.log("返金処理を実行"); order.setState(new CancelledState()); }
}

// 発送済み状態ではこの振る舞いをする
class ShippedState implements OrderState {
    readonly name = "発送済み";
    pay(_: Order) { console.log(" すでに支払い済みです"); }
    ship(_: Order) { console.log(" すでに発送済みです"); }
    cancel(_: Order) { console.log(" 発送後はキャンセルできません"); }
}

// キャンセル状態ではこの振る舞いをする
class CancelledState implements OrderState {
    readonly name = "キャンセル";
    pay(_: Order) { console.log(" キャンセル済みの注文です"); }
    ship(_: Order) { console.log(" キャンセル済みの注文です"); }
    cancel(_: Order) { console.log(" すでにキャンセル済みです"); }
}

const order = new Order(); // 新しいオーダーはデフォルトでPending
order.ship(); 
// this.stateは今　PendingState実態そのもの
//  PendingState.ship() が実行される　console.log(" x 未払いのため発送できません")

order.pay(); // console.log(` → ${this.state.name}未払い から ${state.name}"支払い済み" へ遷移`);
order.ship(); // PaidState→ShippedState